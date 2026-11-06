from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Platform
from app.services.dashboard import (
    FILTER_KEYS,
    Period,
    build_summary,
    default_period,
    metric_definitions,
)

router = APIRouter(tags=["dashboard"])
MAX_DAYS = 731


@router.get("/dashboard/summary")
def summary(
    start: date | None = None,
    end: date | None = None,
    platform: str | None = Query(default=None, max_length=60),
    campaign: str | None = Query(default=None, max_length=120),
    ad_group: str | None = Query(default=None, max_length=120),
    ad: str | None = Query(default=None, max_length=120),
    objective: str | None = Query(default=None, max_length=60),
    channel: str | None = Query(default=None, max_length=60),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    if (start is None) != (end is None):
        raise HTTPException(422, "Informe início e fim do período juntos.")
    period = Period(start, end) if start and end else default_period()
    if period.end < period.start:
        raise HTTPException(422, "A data final deve ser igual ou posterior à inicial.")
    if period.days > MAX_DAYS:
        raise HTTPException(422, f"Período máximo: {MAX_DAYS} dias.")
    values = dict(
        zip(FILTER_KEYS, (platform, campaign, ad_group, ad, objective, channel), strict=True)
    )
    filters = {k: v for k, v in values.items() if v}
    return build_summary(db, period, filters)


@router.get("/dashboard/filters")
def filter_options(db: Session = Depends(get_db)) -> dict[str, Any]:
    platforms = db.scalars(select(Platform).where(Platform.kind.in_(["ads", "social"])))
    return {
        "platforms": [{"value": p.code, "label": p.name} for p in platforms],
        # Campanhas, conjuntos e anúncios passam a existir com as importações da Fase 2.
        "campaigns": [],
        "ad_groups": [],
        "ads": [],
        "objectives": [],
        "channels": [],
    }


@router.get("/metrics/definitions")
def definitions() -> list[dict[str, Any]]:
    return metric_definitions()
