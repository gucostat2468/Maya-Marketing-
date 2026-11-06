"""Montagem do Dashboard Executivo.

Fase 1: ainda não existem tabelas de fatos (métricas de campanha, leads, vendas).
Por isso ``aggregate_base_metrics`` devolve um dicionário vazio, e TODOS os
indicadores saem com status ``no_data``, explicando o motivo. Nenhum número é
inventado. Na Fase 2 esta função passa a somar os dados importados, sem mudar o
contrato da API nem a interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.metrics import BASE_METRICS, CATALOG, DERIVED_METRICS, Number, compare, compute
from app.models import ImportBatch, Integration

DASHBOARD_KPIS = [
    "spend",
    "leads",
    "qualified_leads",
    "cpl",
    "cpql",
    "sales",
    "cpa",
    "revenue",
    "roas",
    "followers_net",
    "reach",
    "impressions",
    "engagements",
    "ctr",
    "cpc",
    "click_to_lead_rate",
]
FILTER_KEYS = ["platform", "campaign", "ad_group", "ad", "objective", "channel"]


@dataclass(frozen=True)
class Period:
    start: date
    end: date  # inclusivo

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1

    def previous(self) -> Period:
        end = self.start - timedelta(days=1)
        return Period(end - timedelta(days=self.days - 1), end)

    def to_dict(self) -> dict[str, Any]:
        return {"start": self.start.isoformat(), "end": self.end.isoformat(), "days": self.days}


def default_period(today: date | None = None) -> Period:
    today = today or date.today()
    return Period(today - timedelta(days=29), today)


def aggregate_base_metrics(
    db: Session, period: Period, filters: dict[str, str]
) -> dict[str, Number | None]:
    # Fase 1: sem tabelas de fatos. Retornar vazio = "sem dados", nunca zero.
    return {}


def data_coverage(db: Session) -> dict[str, Any]:
    imports = db.scalar(
        select(func.count()).select_from(ImportBatch).where(ImportBatch.status == "completed")
    )
    connected = db.scalar(
        select(func.count()).select_from(Integration).where(Integration.status == "connected")
    )
    has_data = bool(imports or connected)
    message = (
        None
        if has_data
        else (
            "Nenhuma integração foi autenticada e nenhum relatório foi importado. "
            "Os indicadores ficarão disponíveis a partir da importação de relatórios CSV (Fase 2)."
        )
    )
    return {
        "has_data": has_data,
        "imports_completed": imports or 0,
        "integrations_connected": connected or 0,
        "message": message,
    }


def build_summary(db: Session, period: Period, filters: dict[str, str]) -> dict[str, Any]:
    previous = period.previous()
    current_results = compute(aggregate_base_metrics(db, period, filters))
    previous_results = compute(aggregate_base_metrics(db, previous, filters))
    kpis = []
    for key in DASHBOARD_KPIS:
        definition = CATALOG[key]
        kpis.append(
            {
                "key": key,
                "label": definition.label,
                "unit": definition.unit.value,
                "group": definition.group,
                "formula": definition.formula,
                "numerator_key": definition.numerator,
                "denominator_key": definition.denominator,
                "caveat": definition.caveat,
                "higher_is_better": definition.higher_is_better,
                "current": current_results[key].to_dict(),
                "previous": previous_results[key].to_dict(),
                "change": compare(current_results[key], previous_results[key]).to_dict(),
            }
        )
    return {
        "period": period.to_dict(),
        "comparison_period": previous.to_dict(),
        "filters": filters,
        "coverage": data_coverage(db),
        "kpis": kpis,
    }


def metric_definitions() -> list[dict[str, Any]]:
    return [
        {
            "key": d.key,
            "label": d.label,
            "unit": d.unit.value,
            "group": d.group,
            "description": d.description,
            "formula": d.formula,
            "numerator": d.numerator,
            "denominator": d.denominator,
            "caveat": d.caveat,
            "kind": kind,
        }
        for kind, items in (("base", BASE_METRICS), ("derived", DERIVED_METRICS))
        for d in items
    ]
