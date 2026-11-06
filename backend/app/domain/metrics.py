"""Catálogo e cálculo de indicadores (determinístico, local, sem IA).

Regras de ouro implementadas aqui:

1. **Ausente ≠ zero.** ``None`` significa "não sabemos" (sem fonte de dados);
   ``0`` significa "medimos e deu zero". Nunca convertemos um no outro.
2. **Denominador zero não vira zero.** CPL com 0 leads é *indefinido*, não R$ 0.
3. **Cada número carrega sua origem**: numerador, denominador, fórmula e insumos ausentes.
4. **CAC ≠ CPA** e **ROAS ≠ lucro**: são indicadores distintos, com ressalvas explícitas.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from typing import Any

Number = Decimal | int | float


class MetricStatus(StrEnum):
    OK = "ok"
    NO_DATA = "no_data"  # algum insumo não existe (fonte não conectada / não importada)
    UNDEFINED = "undefined"  # insumos existem, mas o denominador é zero


class Unit(StrEnum):
    CURRENCY = "currency"
    COUNT = "count"
    PERCENT = "percent"  # armazenado como fração (0.25 = 25%)
    RATIO = "ratio"  # ex.: ROAS 3.2x


@dataclass(frozen=True)
class MetricDefinition:
    key: str
    label: str
    unit: Unit
    group: str
    description: str
    formula: str | None = None  # None = indicador base (soma direta da fonte)
    numerator: str | None = None
    denominator: str | None = None
    multiplier: int = 1  # CPM = custo / impressões x 1000
    caveat: str | None = None
    higher_is_better: bool | None = None


@dataclass
class MetricResult:
    key: str
    status: MetricStatus
    value: Decimal | None = None
    numerator: Decimal | None = None
    denominator: Decimal | None = None
    missing_inputs: list[str] = field(default_factory=list)
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for k in ("value", "numerator", "denominator"):
            data[k] = None if data[k] is None else float(data[k])
        data["status"] = self.status.value
        return data


def _dec(value: Number | None) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


BASE_METRICS: list[MetricDefinition] = [
    MetricDefinition(
        "spend",
        "Investimento em mídia",
        Unit.CURRENCY,
        "investimento",
        "Soma do valor gasto em anúncios no período, conforme as plataformas.",
    ),
    MetricDefinition(
        "acquisition_cost_total",
        "Custo total de aquisição",
        Unit.CURRENCY,
        "investimento",
        "Mídia + custos comerciais e operacionais incluídos na metodologia de CAC "
        "(equipe, ferramentas, comissões). Informado manualmente.",
    ),
    MetricDefinition(
        "impressions",
        "Impressões",
        Unit.COUNT,
        "alcance",
        "Número de vezes que os anúncios foram exibidos.",
    ),
    MetricDefinition(
        "reach",
        "Alcance",
        Unit.COUNT,
        "alcance",
        "Pessoas únicas alcançadas. Não é somável entre plataformas.",
        caveat="Alcance de plataformas diferentes não pode ser somado: a mesma "
        "pessoa pode ter sido alcançada em ambas.",
    ),
    MetricDefinition("clicks", "Cliques", Unit.COUNT, "alcance", "Cliques nos anúncios."),
    MetricDefinition(
        "engagements",
        "Engajamento",
        Unit.COUNT,
        "social",
        "Interações (curtidas, comentários, compartilhamentos, salvamentos).",
    ),
    MetricDefinition(
        "followers_net",
        "Crescimento líquido de seguidores",
        Unit.COUNT,
        "social",
        "Novos seguidores menos seguidores perdidos.",
        caveat="Crescimento no mesmo período de uma campanha não prova que a "
        "campanha gerou os seguidores.",
    ),
    MetricDefinition(
        "leads", "Leads gerados", Unit.COUNT, "leads", "Contatos recebidos, após deduplicação."
    ),
    MetricDefinition(
        "qualified_leads",
        "Leads qualificados",
        Unit.COUNT,
        "leads",
        "Leads classificados como qualificados pelos critérios configurados.",
    ),
    MetricDefinition(
        "sales",
        "Vendas registradas",
        Unit.COUNT,
        "comercial",
        "Vendas atribuídas a leads de marketing (manual, planilha ou CRM).",
    ),
    MetricDefinition(
        "revenue",
        "Receita atribuída",
        Unit.CURRENCY,
        "comercial",
        "Receita das vendas atribuídas a campanhas.",
    ),
]

DERIVED_METRICS: list[MetricDefinition] = [
    MetricDefinition(
        "cpl",
        "Custo por lead (CPL)",
        Unit.CURRENCY,
        "eficiencia",
        "Quanto custa, em média, cada contato recebido.",
        "investimento ÷ leads",
        "spend",
        "leads",
        caveat="CPL baixo não significa leads bons: compare com o CPQL e o CPA.",
        higher_is_better=False,
    ),
    MetricDefinition(
        "cpql",
        "Custo por lead qualificado (CPQL)",
        Unit.CURRENCY,
        "eficiencia",
        "Quanto custa cada contato que atende aos critérios de qualificação.",
        "investimento ÷ leads qualificados",
        "spend",
        "qualified_leads",
        higher_is_better=False,
    ),
    MetricDefinition(
        "qualification_rate",
        "Taxa de qualificação",
        Unit.PERCENT,
        "eficiencia",
        "Parcela dos leads que foi qualificada.",
        "leads qualificados ÷ leads",
        "qualified_leads",
        "leads",
        higher_is_better=True,
    ),
    MetricDefinition(
        "cpa",
        "Custo por aquisição (CPA)",
        Unit.CURRENCY,
        "comercial",
        "Custo de MÍDIA por venda atribuída.",
        "investimento em mídia ÷ vendas atribuídas",
        "spend",
        "sales",
        caveat="CPA considera só mídia. Não é o CAC.",
        higher_is_better=False,
    ),
    MetricDefinition(
        "cac",
        "Custo de aquisição de cliente (CAC)",
        Unit.CURRENCY,
        "comercial",
        "Custo TOTAL de aquisição por cliente, conforme a metodologia definida.",
        "custo total de aquisição ÷ vendas",
        "acquisition_cost_total",
        "sales",
        caveat="Depende de quais custos entram na metodologia. Sem custo total "
        "informado, o CAC não é calculado (nunca usamos só a mídia).",
        higher_is_better=False,
    ),
    MetricDefinition(
        "lead_to_sale_rate",
        "Conversão de lead em venda",
        Unit.PERCENT,
        "comercial",
        "Parcela dos leads que virou venda.",
        "vendas ÷ leads",
        "sales",
        "leads",
        higher_is_better=True,
    ),
    MetricDefinition(
        "roas",
        "ROAS",
        Unit.RATIO,
        "comercial",
        "Receita atribuída para cada R$ 1 investido em anúncios.",
        "receita atribuída ÷ investimento em mídia",
        "revenue",
        "spend",
        caveat="ROAS mede receita, não lucro. Um ROAS de 2x pode dar prejuízo "
        "dependendo da margem.",
        higher_is_better=True,
    ),
    MetricDefinition(
        "ctr",
        "CTR",
        Unit.PERCENT,
        "alcance",
        "Parcela das impressões que gerou clique.",
        "cliques ÷ impressões",
        "clicks",
        "impressions",
        higher_is_better=True,
    ),
    MetricDefinition(
        "cpc",
        "CPC",
        Unit.CURRENCY,
        "alcance",
        "Custo médio por clique.",
        "investimento ÷ cliques",
        "spend",
        "clicks",
        higher_is_better=False,
    ),
    MetricDefinition(
        "cpm",
        "CPM",
        Unit.CURRENCY,
        "alcance",
        "Custo por mil impressões.",
        "investimento ÷ impressões × 1.000",
        "spend",
        "impressions",
        multiplier=1000,
        higher_is_better=False,
    ),
    MetricDefinition(
        "click_to_lead_rate",
        "Taxa de conversão (clique → lead)",
        Unit.PERCENT,
        "eficiencia",
        "Parcela dos cliques que virou lead.",
        "leads ÷ cliques",
        "leads",
        "clicks",
        higher_is_better=True,
    ),
]

CATALOG: dict[str, MetricDefinition] = {m.key: m for m in BASE_METRICS + DERIVED_METRICS}


def ratio(
    definition: MetricDefinition, numerator: Number | None, denominator: Number | None
) -> MetricResult:
    num, den = _dec(numerator), _dec(denominator)
    missing = [
        k
        for k, v in ((definition.numerator, num), (definition.denominator, den))
        if v is None and k
    ]
    if missing:
        labels = ", ".join(CATALOG[k].label.lower() for k in missing)
        return MetricResult(
            definition.key,
            MetricStatus.NO_DATA,
            None,
            num,
            den,
            missing,
            f"Sem dados de: {labels}.",
        )
    assert num is not None and den is not None
    if den == 0:
        return MetricResult(
            definition.key,
            MetricStatus.UNDEFINED,
            None,
            num,
            den,
            [],
            f"Não calculável: {CATALOG[definition.denominator].label.lower()} "
            "igual a zero no período.",
        )
    return MetricResult(
        definition.key, MetricStatus.OK, num / den * definition.multiplier, num, den
    )


def compute(base: dict[str, Number | None]) -> dict[str, MetricResult]:
    """Calcula todos os indicadores a partir dos valores base.

    Chaves ausentes do dicionário são tratadas como ``None`` (sem dados), nunca como zero.
    """
    results: dict[str, MetricResult] = {}
    for definition in BASE_METRICS:
        value = _dec(base.get(definition.key))
        if value is None:
            results[definition.key] = MetricResult(
                definition.key,
                MetricStatus.NO_DATA,
                missing_inputs=[definition.key],
                reason="Nenhuma fonte forneceu este dado no período.",
            )
        else:
            results[definition.key] = MetricResult(definition.key, MetricStatus.OK, value)
    for definition in DERIVED_METRICS:
        results[definition.key] = ratio(
            definition, base.get(definition.numerator), base.get(definition.denominator)
        )
    return results


@dataclass
class Change:
    status: MetricStatus
    absolute: Decimal | None = None
    relative: Decimal | None = None  # fração; None quando o período anterior é zero/ausente

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "absolute": None if self.absolute is None else float(self.absolute),
            "relative": None if self.relative is None else float(self.relative),
        }


def compare(current: MetricResult, previous: MetricResult) -> Change:
    if current.value is None or previous.value is None:
        return Change(MetricStatus.NO_DATA)
    absolute = current.value - previous.value
    if previous.value == 0:
        return Change(MetricStatus.OK, absolute, None)
    return Change(MetricStatus.OK, absolute, absolute / abs(previous.value))


def round_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
