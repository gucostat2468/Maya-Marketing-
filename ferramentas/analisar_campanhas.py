#!/usr/bin/env python3
"""Análise determinística de campanhas (Meta Ads e Google Ads) a partir de CSVs exportados.

Usado pelo agente ``analista-de-campanhas``. O agente NÃO faz contas: ele roda esta
ferramenta e interpreta o resultado. Só biblioteca padrão do Python, para rodar em qualquer
máquina (inclusive na nuvem) sem instalar nada.

Uso:
    python3 ferramentas/analisar_campanhas.py dados/campanhas/*.csv
    python3 ferramentas/analisar_campanhas.py meta.csv google.csv --vendas vendas.csv --margem 0.35

Regras (herdadas de backend/app/domain/metrics.py):
- Dado ausente ("--", vazio) é ``None``, nunca zero.
- Divisão por zero vira "não calculável", nunca zero.
- ROI só é calculado com margem informada (ROAS não é lucro).
- Campanha com amostra pequena não entra no ranking: aparece separada.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.domain.metrics import CATALOG, MetricResult, MetricStatus, compute  # noqa: E402
from ferramentas.decisoes import decidir  # noqa: E402
from ferramentas.estatistica import poisson_ci  # noqa: E402,F401

# ---------------------------------------------------------------------------
# Leitura e normalização dos arquivos
# ---------------------------------------------------------------------------


def norm(text: str) -> str:
    """Minúsculas, sem acento, sem sufixo de moeda e sem espaços duplicados."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"\((brl|usd|r\$)\)", "", text.lower())
    return re.sub(r"\s+", " ", text).strip()


# Para cada campo, os nomes de coluna aceitos, em ordem de prioridade.
ALIASES: dict[str, list[str]] = {
    "campaign": ["nome da campanha", "campaign name", "campanha", "campaign"],
    "spend": ["valor usado", "amount spent", "custo", "cost", "investimento", "gasto"],
    "impressions": ["impressoes", "impressions", "impr."],
    "reach": ["alcance", "reach"],
    # No Meta, "cliques no link" é o clique que leva ao site; "cliques (todos)" inclui curtidas.
    "clicks": ["cliques no link", "link clicks", "cliques", "clicks"],
    "leads": ["leads", "leads (formulario)", "cadastros", "conversoes", "conversions", "conv."],
    "revenue": ["valor conv.", "valor de conversao", "conv. value", "conversion value", "receita"],
    "day": ["dia", "day", "data", "date"],
    "start": ["inicio dos relatorios", "reporting starts"],
    "end": ["termino dos relatorios", "reporting ends"],
    "result_indicator": ["indicador de resultados", "result indicator"],
    "results": ["resultados", "results"],
}
PT_MARKERS = {"nome da campanha", "campanha", "valor usado", "custo", "impressoes", "cliques"}
META_MARKERS = {"nome da campanha", "campaign name", "valor usado", "amount spent"}
GOOGLE_MARKERS = {"campanha", "campaign", "custo", "cost", "impr."}
NUMERIC = ("spend", "impressions", "reach", "clicks", "leads", "revenue")
MISSING_TOKENS = {"", "--", "-", "n/a", "na", "null", "none", "—"}


class LeituraErro(Exception):
    pass


def _decode(raw: bytes) -> str:
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")  # Google Ads às vezes exporta em UTF-16 com tabulação
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise LeituraErro("Codificação de arquivo não reconhecida.")


def parse_number(value: str | None, locale: str) -> Decimal | None:
    """Converte "R$ 1.234,56", "1,234.56", "12,5%" e "--" (ausente -> None)."""
    if value is None:
        return None
    text = value.strip().replace("R$", "").replace(" ", "").replace(" ", "").replace("%", "")
    if text.lower() in MISSING_TOKENS:
        return None
    if "," in text and "." in text:
        decimal_sep = "," if text.rfind(",") > text.rfind(".") else "."
    elif "," in text:
        decimal_sep = "." if (locale == "en" and re.fullmatch(r"-?\d{1,3}(,\d{3})+", text)) else ","
    elif "." in text:
        decimal_sep = "," if (locale == "pt" and re.fullmatch(r"-?\d{1,3}(\.\d{3})+", text)) else "."
    else:
        decimal_sep = "."
    thousands = "." if decimal_sep == "," else ","
    text = text.replace(thousands, "").replace(decimal_sep, ".")
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


@dataclass
class Arquivo:
    path: str
    platform: str
    locale: str
    rows_read: int = 0
    rows_used: int = 0
    rows_skipped: list[str] = field(default_factory=list)
    columns: dict[str, str] = field(default_factory=dict)  # campo -> coluna original
    period: tuple[str | None, str | None] = (None, None)


def _find_header(rows: list[list[str]]) -> int:
    campaign_aliases = set(ALIASES["campaign"])
    for i, row in enumerate(rows[:15]):  # relatórios do Google têm linhas de título antes
        if campaign_aliases & {norm(c) for c in row}:
            return i
    raise LeituraErro(
        "Não encontrei a coluna de campanha (ex.: 'Nome da campanha' ou 'Campanha') "
        "nas 15 primeiras linhas."
    )


def _map_columns(header: list[str]) -> dict[str, int]:
    normalized = [norm(h) for h in header]
    mapping: dict[str, int] = {}
    for fieldname, aliases in ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                mapping[fieldname] = normalized.index(alias)
                break
    return mapping


def read_file(path: Path, platform_hint: str | None = None) -> tuple[Arquivo, list[dict[str, Any]]]:
    text = _decode(path.read_bytes())
    sample = text[:4096]
    try:
        delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
    except csv.Error:
        delimiter = ","
    rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
    header_idx = _find_header(rows)
    header = rows[header_idx]
    cols = _map_columns(header)
    normalized_header = {norm(h) for h in header}

    if platform_hint:
        platform = platform_hint
    elif META_MARKERS & normalized_header:
        platform = "meta_ads"
    elif GOOGLE_MARKERS & normalized_header:
        platform = "google_ads"
    else:
        platform = "desconhecida"
    locale = "pt" if PT_MARKERS & normalized_header else "en"
    info = Arquivo(str(path), platform, locale,
                   columns={k: header[v] for k, v in cols.items()})
    if "spend" not in cols:
        raise LeituraErro(f"{path.name}: coluna de investimento não encontrada "
                          "(ex.: 'Valor usado (BRL)' ou 'Custo').")

    records: list[dict[str, Any]] = []
    days: list[str] = []
    for raw in rows[header_idx + 1:]:
        if not any(c.strip() for c in raw):
            continue
        info.rows_read += 1

        def get(fieldname: str, raw: list[str] = raw) -> str | None:
            idx = cols.get(fieldname)
            return raw[idx] if idx is not None and idx < len(raw) else None

        name = (get("campaign") or "").strip()
        if not name or norm(name).startswith("total") or name.strip() == "--":
            info.rows_skipped.append(name or "(linha sem nome de campanha)")
            continue
        rec: dict[str, Any] = {"platform": platform, "campaign": name}
        for fieldname in NUMERIC:
            rec[fieldname] = parse_number(get(fieldname), locale)
        # No Meta, "Resultados" só conta como lead quando o indicador do resultado é de lead.
        if rec["leads"] is None and "results" in cols:
            indicator = norm(get("result_indicator") or "")
            if "lead" in indicator or "cadastro" in indicator:
                rec["leads"] = parse_number(get("results"), locale)
        for key in ("day", "start", "end"):
            value = (get(key) or "").strip()
            if value:
                days.append(value)
        rec["day"] = (get("day") or "").strip() or None
        rec["indicator"] = norm(get("result_indicator") or "") or None
        records.append(rec)
        info.rows_used += 1
    if days:
        info.period = (min(days), max(days))
    return info, records


# ---------------------------------------------------------------------------
# Agregação, métricas e ranking
# ---------------------------------------------------------------------------


def _sum(values: list[Decimal | None]) -> Decimal | None:
    known = [v for v in values if v is not None]
    return sum(known, Decimal(0)) if known else None


@dataclass
class Campanha:
    platform: str
    campaign: str
    base: dict[str, Decimal | None]
    metrics: dict[str, MetricResult]
    roi: MetricResult | None = None
    eligible: bool = False
    ci: tuple[float | None, float | None] = (None, None)
    label: str | None = None


def aggregate(records: list[dict[str, Any]],
              sales: dict[str, dict[str, Decimal | None]] | None) -> list[Campanha]:
    """Com arquivo de vendas, campanha ausente dele = 0 vendas registradas (zero medido).
    Sem arquivo de vendas, vendas ficam "sem dados"."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for rec in records:
        groups.setdefault((rec["platform"], rec["campaign"]), []).append(rec)
    campanhas = []
    for (platform, name), recs in groups.items():
        base = {f: _sum([r[f] for r in recs]) for f in NUMERIC}
        if platform != "meta_ads":
            base.pop("reach", None)
        match = sales.get(norm(name)) if sales is not None else None
        if sales is None:
            base["sales"] = None
        else:
            base["sales"] = match["sales"] if match else Decimal(0)
        if match and match.get("revenue") is not None:
            base["revenue"] = match["revenue"]  # receita comercial real prevalece
        campanhas.append(Campanha(platform, name, base, compute(base)))
    return campanhas


def roi(revenue: Decimal | None, spend: Decimal | None, margin: Decimal | None) -> MetricResult:
    if margin is None:
        return MetricResult("roi", MetricStatus.NO_DATA, missing_inputs=["margem"],
                            reason="ROI exige a margem de contribuição (--margem).")
    if revenue is None or spend is None:
        missing = [k for k, v in (("revenue", revenue), ("spend", spend)) if v is None]
        return MetricResult("roi", MetricStatus.NO_DATA, missing_inputs=missing,
                            reason="Sem receita atribuída ou sem investimento.")
    if spend == 0:
        return MetricResult("roi", MetricStatus.UNDEFINED, reason="Investimento igual a zero.")
    profit = revenue * margin - spend
    return MetricResult("roi", MetricStatus.OK, profit / spend, profit, spend)


# Métrica que decide o ranking, conforme os dados disponíveis.
RANKING_RULES = {
    "cpa": ("sales", "vendas", 5),
    "cpl": ("leads", "leads", 10),
    "cpc": ("clicks", "cliques", 100),
}


def choose_metric(campanhas: list[Campanha]) -> str:
    if any(c.base.get("sales") for c in campanhas):
        return "cpa"
    if any(c.base.get("leads") for c in campanhas):
        return "cpl"
    return "cpc"


def rank(campanhas: list[Campanha], metric: str, minimum: int) -> list[Campanha]:
    count_key = RANKING_RULES[metric][0]
    for c in campanhas:
        count = c.base.get(count_key)
        spend = c.base.get("spend")
        result = c.metrics[metric]
        c.eligible = bool(result.status == MetricStatus.OK and count is not None
                          and count >= minimum)
        if c.eligible and spend is not None:
            low, high = poisson_ci(int(count))
            # custo por X: dividir pelo limite SUPERIOR da contagem dá o custo MÍNIMO plausível
            c.ci = (float(spend) / high, float(spend) / low if low > 0 else None)
    eligible = sorted([c for c in campanhas if c.eligible],
                      key=lambda c: c.metrics[metric].value)
    if eligible:
        leader = eligible[0]
        leader.label = "melhor"
        leader_high = leader.ci[1]
        for c in eligible[1:]:
            overlaps = leader_high is None or (c.ci[0] is not None and c.ci[0] <= leader_high)
            c.label = "empate técnico com o melhor" if overlaps else "inferior"
    return eligible


# ---------------------------------------------------------------------------
# Diagnósticos (fatos observados + hipótese, nunca causalidade)
# ---------------------------------------------------------------------------


def diagnostics(campanhas: list[Campanha], minimum_leads: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    total_spend = _sum([c.base["spend"] for c in campanhas]) or Decimal(0)
    total_leads = _sum([c.base["leads"] for c in campanhas])
    total_clicks = _sum([c.base["clicks"] for c in campanhas])
    avg_cpl = total_spend / total_leads if total_leads else None
    avg_ctl = total_leads / total_clicks if total_leads is not None and total_clicks else None
    has_sales = any(c.base.get("sales") is not None for c in campanhas)

    for c in campanhas:
        spend, leads, clicks = c.base["spend"], c.base["leads"], c.base["clicks"]
        share = spend / total_spend if spend and total_spend else None
        cpl = c.metrics["cpl"].value
        if share and share > Decimal("0.4") and cpl and avg_cpl and cpl > avg_cpl * Decimal("1.2"):
            out.append({
                "tipo": "investimento_concentrado", "campanha": c.campaign,
                "evidencia": f"{fmt_pct(share)} do investimento com CPL {fmt_money(cpl)} "
                             f"vs. média {fmt_money(avg_cpl)}",
                "hipotese": "Orçamento concentrado na campanha menos eficiente em CPL.",
                "acao": "Avaliar redistribuir verba para campanhas com CPL menor, "
                        "confirmando antes a qualidade dos leads.",
                "confianca": confidence(leads),
            })
        if spend and avg_cpl and (leads == 0) and spend > 2 * avg_cpl:
            out.append({
                "tipo": "gasto_sem_lead", "campanha": c.campaign,
                "evidencia": f"Investiu {fmt_money(spend)} (mais de 2 CPLs médios) e teve 0 leads",
                "hipotese": "Problema de oferta, público, página ou rastreamento de conversão.",
                "acao": "Verificar primeiro se a conversão está sendo registrada (GTM/pixel); "
                        "depois, segmentação e página.",
                "confianca": "média",
            })
        ctl = leads / clicks if leads is not None and clicks else None
        if clicks and clicks >= 100 and ctl is not None and avg_ctl and ctl < avg_ctl / 2:
            out.append({
                "tipo": "cliques_sem_conversao", "campanha": c.campaign,
                "evidencia": f"{fmt_int(clicks)} cliques, conversão clique→lead {fmt_pct(ctl)} "
                             f"vs. média {fmt_pct(avg_ctl)}",
                "hipotese": "O anúncio atrai cliques, mas a página ou o formulário não converte, "
                            "ou o público clica sem intenção.",
                "acao": "Revisar a coerência anúncio-página e testar o formulário.",
                "confianca": confidence(leads),
            })
        if leads is not None and 0 < leads < minimum_leads:
            out.append({
                "tipo": "amostra_pequena", "campanha": c.campaign,
                "evidencia": f"Apenas {fmt_int(leads)} leads (mínimo para ranking: {minimum_leads})",
                "hipotese": "Resultado pode ser acaso.",
                "acao": "Aguardar mais dados antes de concluir.", "confianca": "baixa",
            })
    if has_sales:
        sold = [c for c in campanhas if c.metrics["cpl"].value and c.metrics["cpa"].value]
        if len(sold) >= 2:
            cpls = sorted(c.metrics["cpl"].value for c in sold)
            cpas = sorted(c.metrics["cpa"].value for c in sold)
            med_cpl, med_cpa = cpls[len(cpls) // 2], cpas[len(cpas) // 2]
            for c in sold:
                if c.metrics["cpl"].value < med_cpl and c.metrics["cpa"].value > med_cpa:
                    out.append({
                        "tipo": "lead_barato_venda_cara", "campanha": c.campaign,
                        "evidencia": f"CPL {fmt_money(c.metrics['cpl'].value)} abaixo da mediana, "
                                     f"CPA {fmt_money(c.metrics['cpa'].value)} acima da mediana",
                        "hipotese": "Gera volume de leads de baixa qualidade.",
                        "acao": "Não julgar pela CPL: revisar público e qualificação.",
                        "confianca": confidence(c.base.get("sales")),
                    })
    return out


def confidence(count: Decimal | None) -> str:
    if count is None or count < 10:
        return "baixa"
    return "média" if count < 30 else "alta"


# ---------------------------------------------------------------------------
# Formatação pt-BR e relatório
# ---------------------------------------------------------------------------


def _br(value: float, decimals: int) -> str:
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "§").replace(".", ",").replace("§", ".")


def fmt_money(v: Decimal | float | None) -> str:
    return "sem dados" if v is None else f"R$ {_br(float(v), 2)}"


def fmt_int(v: Decimal | float | None) -> str:
    return "sem dados" if v is None else _br(float(v), 0)


def fmt_pct(v: Decimal | float | None) -> str:
    return "sem dados" if v is None else f"{_br(float(v) * 100, 1)}%"


def fmt_ratio(v: Decimal | float | None) -> str:
    return "sem dados" if v is None else f"{_br(float(v), 2)}x"


FORMATTERS = {"currency": fmt_money, "count": fmt_int, "percent": fmt_pct, "ratio": fmt_ratio}


def show(c: Campanha, key: str) -> str:
    result = c.roi if key == "roi" else c.metrics[key]
    if result is None:
        return "sem dados"
    if result.status == MetricStatus.UNDEFINED:
        return "não calculável"
    if result.status == MetricStatus.NO_DATA:
        return "sem dados"
    unit = "percent" if key == "roi" else CATALOG[key].unit.value
    return FORMATTERS[unit](result.value)


PLATFORM_LABEL = {"meta_ads": "Meta Ads", "google_ads": "Google Ads"}
DIAG_LABELS = {
    "investimento_concentrado": "investimento concentrado",
    "gasto_sem_lead": "gasto sem lead",
    "cliques_sem_conversao": "cliques sem conversão",
    "amostra_pequena": "amostra pequena",
    "lead_barato_venda_cara": "lead barato, venda cara",
}


def build_report(files: list[Arquivo], campanhas: list[Campanha], metric: str, minimum: int,
                 ranking: list[Campanha], diags: list[dict[str, Any]], margin: Decimal | None,
                 has_sales_file: bool) -> str:
    L: list[str] = []
    L.append("# Análise de campanhas\n")
    L.append("## Dados analisados\n")
    for f in files:
        period = f" | período no arquivo: {f.period[0]} a {f.period[1]}" if f.period[0] else ""
        L.append(f"- `{Path(f.path).name}`: {PLATFORM_LABEL.get(f.platform, f.platform)}, "
                 f"{f.rows_used} linhas usadas de {f.rows_read}{period}")
        if f.rows_skipped:
            L.append(f"  - ignoradas (totais ou sem nome): {len(f.rows_skipped)}")
    L.append("")

    totals = compute({k: _sum([c.base.get(k) for c in campanhas])
                      for k in ("spend", "impressions", "clicks", "leads", "sales", "revenue")})
    L.append("## Totais do período\n")
    L.append("| Indicador | Valor |\n|---|---|")
    for key in ("spend", "impressions", "clicks", "leads", "cpl", "cpc", "ctr", "sales", "cpa",
                "revenue", "roas"):
        r = totals[key]
        value = (FORMATTERS[CATALOG[key].unit.value](r.value) if r.status == MetricStatus.OK
                 else ("não calculável" if r.status == MetricStatus.UNDEFINED else "sem dados"))
        L.append(f"| {CATALOG[key].label} | {value} |")
    L.append("")

    L.append("## Por campanha\n")
    L.append("| Plataforma | Campanha | Investimento | Cliques | CPC | CTR | Leads | CPL | "
             "Conv. clique→lead | Vendas | CPA | ROAS | ROI |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in sorted(campanhas, key=lambda c: -(c.base["spend"] or 0)):
        L.append(f"| {PLATFORM_LABEL.get(c.platform, c.platform)} | {c.campaign} | "
                 f"{fmt_money(c.base['spend'])} | {fmt_int(c.base['clicks'])} | {show(c, 'cpc')} | "
                 f"{show(c, 'ctr')} | {fmt_int(c.base['leads'])} | {show(c, 'cpl')} | "
                 f"{show(c, 'click_to_lead_rate')} | {fmt_int(c.base.get('sales'))} | "
                 f"{show(c, 'cpa')} | {show(c, 'roas')} | {show(c, 'roi')} |")
    L.append("")

    label = CATALOG[metric].label
    count_name = RANKING_RULES[metric][1]
    L.append(f"## Ranking: qual campanha performa melhor ({label})\n")
    L.append(f"Critério: menor {label}. Só entram campanhas com pelo menos {minimum} "
             f"{count_name}. O intervalo mostra a faixa plausível (95%) do custo, considerando "
             "o volume; faixas que se sobrepõem significam **empate técnico**.\n")
    if ranking:
        L.append(f"| Posição | Campanha | {label} | Faixa plausível | Situação |")
        L.append("|---|---|---|---|---|")
        for i, c in enumerate(ranking, 1):
            high = fmt_money(c.ci[1]) if c.ci[1] is not None else "sem limite"
            L.append(f"| {i} | {c.campaign} ({PLATFORM_LABEL.get(c.platform, c.platform)}) | "
                     f"{show(c, metric)} | {fmt_money(c.ci[0])} a {high} | {c.label} |")
    else:
        L.append("Nenhuma campanha tem volume suficiente para um ranking confiável.")
    excluded = [c for c in campanhas if not c.eligible]
    if excluded:
        L.append("\nFora do ranking (volume insuficiente ou sem dados): "
                 + ", ".join(c.campaign for c in excluded) + ".")
    if metric == "cpc":
        L.append("\n> Sem leads nos dados: o ranking mede só eficiência de tráfego, não resultado.")
    L.append("")

    L.append("## Diagnósticos automáticos\n")
    if diags:
        for d in diags:
            L.append(f"- **{d['campanha']}** ({DIAG_LABELS[d['tipo']]}, confiança "
                     f"{d['confianca']}): {d['evidencia']}. Hipótese: {d['hipotese']} "
                     f"Ação sugerida: {d['acao']}")
    else:
        L.append("Nenhum padrão crítico detectado pelas regras automáticas.")
    L.append("")

    L.append("## Limitações\n")
    if has_sales_file:
        L.append("- Vendas vêm do arquivo comercial, ligadas pelo nome da campanha. Campanha que "
                 "não aparece nele conta como 0 vendas registradas no período.")
    if not has_sales_file:
        L.append("- Sem dados de vendas: **não há conclusão sobre retorno comercial**. CPA e "
                 "ROI não foram calculados. Informe `--vendas` para incluir.")
    if margin is None:
        L.append("- ROI não calculado: falta a margem de contribuição (`--margem`). "
                 "ROAS mede receita, não lucro.")
    L.append("- \"Leads\" são os registrados pelas plataformas; podem diferir dos leads "
             "recebidos pelo time comercial (duplicados, testes, spam).")
    L.append("- Comparar CPL entre Meta e Google exige cautela: a qualidade do lead costuma "
             "ser diferente entre os canais.")
    L.append("- Correlação não é causalidade: os diagnósticos são hipóteses a validar.")
    return "\n".join(L) + "\n"


def read_sales(path: Path) -> dict[str, dict[str, Decimal | None]]:
    """CSV comercial com colunas: campanha, vendas, receita (receita é opcional)."""
    text = _decode(path.read_bytes())
    delimiter = csv.Sniffer().sniff(text[:2048], delimiters=",;\t").delimiter
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    fields = {norm(f): f for f in reader.fieldnames or []}
    if "campanha" not in fields or "vendas" not in fields:
        raise LeituraErro("O arquivo de vendas precisa das colunas 'campanha' e 'vendas'.")
    out: dict[str, dict[str, Decimal | None]] = {}
    for row in reader:
        key = norm(row[fields["campanha"]] or "")
        if not key:
            continue
        entry = out.setdefault(key, {"sales": Decimal(0), "revenue": None})
        sold = parse_number(row[fields["vendas"]], "pt")
        entry["sales"] = (entry["sales"] or Decimal(0)) + (sold or Decimal(0))
        if "receita" in fields:
            rev = parse_number(row[fields["receita"]], "pt")
            if rev is not None:
                entry["revenue"] = (entry["revenue"] or Decimal(0)) + rev
    return out


def decide_all(campanhas: list[Campanha], records: list[dict[str, Any]],
               cpl_alvo: Decimal | None, cpa_alvo: Decimal | None) -> dict[tuple[str, str], Any]:
    """Uma decisão por campanha. Vendas (CPA) mandam quando há dados do comercial."""
    tem_vendas = any(c.base.get("sales") is not None for c in campanhas)
    usa_cpa = tem_vendas and (cpa_alvo is not None or any(c.base.get("sales") for c in campanhas))
    metrica = "cpa" if usa_cpa else "cpl"
    alvo = cpa_alvo if metrica == "cpa" else cpl_alvo
    provisorio = alvo is None
    if provisorio:  # meta provisória: custo médio da conta
        chave = "sales" if metrica == "cpa" else "leads"
        gasto = _sum([c.base["spend"] for c in campanhas if c.base.get(chave)])
        qtd = _sum([c.base.get(chave) for c in campanhas])
        alvo = gasto / qtd if gasto and qtd else None
    series: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in records:
        series.setdefault((r["platform"], r["campaign"]), []).append(r)
    out: dict[tuple[str, str], Any] = {}
    for c in campanhas:
        if alvo is None:
            out[(c.platform, c.campaign)] = None
            continue
        serie = series.get((c.platform, c.campaign)) or []
        inds = [r.get("indicator") for r in serie if r.get("indicator")]
        objetivo_lead = (any("lead" in i or "cadastro" in i for i in inds) if inds else None)
        out[(c.platform, c.campaign)] = decidir(c.base, c.platform, metrica, alvo, provisorio,
                                                serie, objetivo_lead)
    return out


ORDEM_ACAO = ["PAUSAR", "ESCALAR", "AJUSTAR", "VERIFICAR", "MANTER", "AGUARDAR",
              "OUTRO_OBJETIVO", "SEM_DADOS"]


def render_decisoes(campanhas: list[Campanha], decisoes: dict[tuple[str, str], Any]) -> str:
    itens = [(c, decisoes.get((c.platform, c.campaign))) for c in campanhas]
    itens = [(c, d) for c, d in itens if d]
    if not itens:
        return ("## O que fazer com cada campanha\n\nSem leads nem vendas nos dados: "
                "não há como decidir por resultado.\n\n")
    itens.sort(key=lambda x: ORDEM_ACAO.index(x[1]["acao"]))
    d0 = itens[0][1]
    nome = "venda (CPA)" if d0["metrica"] == "cpa" else "lead (CPL)"
    meta = fmt_money(d0["alvo"]) + (" (provisória: média da conta)" if any(
        "provisória" in a for a in d0["alertas"]) else "")
    L = ["## O que fazer com cada campanha\n",
         f"Decisão pelo custo por {nome}. Meta usada: {meta}. Com pouca amostra a resposta é "
         "**aguardar**: mexer cedo reinicia o aprendizado da plataforma.\n",
         "| Campanha | Decisão | Por quê | O que fazer agora | Confiança |",
         "|---|---|---|---|---|"]
    for c, d in itens:
        L.append(f"| {c.campaign} ({PLATFORM_LABEL.get(c.platform, c.platform)}) | "
                 f"**{d['rotulo']}** | {d['motivo']} | {d['fazer']} | {d['confianca']} |")
    alertas = [(c, a) for c, d in itens for a in d["alertas"] if "provisória" not in a]
    if alertas:
        L.append("\n**Alertas:**")
        for c, a in alertas:
            L.append(f"- **{c.campaign}**: {a}")
    return "\n".join(L) + "\n\n"


def analyze(paths: list[Path], sales_path: Path | None = None, margin: Decimal | None = None,
            minimum: int | None = None, cpl_alvo: Decimal | None = None,
            cpa_alvo: Decimal | None = None) -> dict[str, Any]:
    seen: set[str] = set()
    files: list[Arquivo] = []
    records: list[dict[str, Any]] = []
    warnings: list[str] = []
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in seen:
            warnings.append(f"{path.name} é idêntico a outro arquivo e foi ignorado "
                            "(evita contar em dobro).")
            continue
        seen.add(digest)
        info, recs = read_file(path)
        files.append(info)
        records.extend(recs)
    # Mesma campanha, mesmo dia, mesmos números em arquivos diferentes = linha duplicada.
    unique, keys = [], set()
    for r in records:
        key = (r["platform"], r["campaign"], r["day"], r["spend"], r["clicks"], r["leads"])
        if r["day"] and key in keys:
            continue
        keys.add(key)
        unique.append(r)
    if len(unique) < len(records):
        warnings.append(f"{len(records) - len(unique)} linhas duplicadas removidas.")
    sales = read_sales(sales_path) if sales_path else None
    campanhas = aggregate(unique, sales)
    for c in campanhas:
        c.roi = roi(c.base.get("revenue"), c.base.get("spend"), margin)
    metric = choose_metric(campanhas)
    minimum = minimum if minimum is not None else RANKING_RULES[metric][2]
    ranking = rank(campanhas, metric, minimum)
    diags = diagnostics(campanhas, RANKING_RULES["cpl"][2])
    decisoes = decide_all(campanhas, unique, cpl_alvo, cpa_alvo)
    report = build_report(files, campanhas, metric, minimum, ranking, diags, margin,
                          sales_path is not None)
    report = report.replace("## Ranking:", render_decisoes(campanhas, decisoes) + "## Ranking:", 1)
    if warnings:
        report = report.replace("## Totais", "> " + "\n> ".join(warnings) + "\n\n## Totais", 1)
    return {
        "metric": metric, "minimum": minimum, "warnings": warnings,
        "files": [f.__dict__ for f in files],
        "campaigns": [{
            "platform": c.platform, "campaign": c.campaign,
            "base": {k: None if v is None else float(v) for k, v in c.base.items()},
            "metrics": {k: v.to_dict() for k, v in c.metrics.items()},
            "roi": c.roi.to_dict() if c.roi else None,
            "eligible": c.eligible, "ci": c.ci, "label": c.label,
            "decisao": decisoes.get((c.platform, c.campaign)),
        } for c in campanhas],
        "ranking": [c.campaign for c in ranking],
        "diagnostics": diags,
        "report_markdown": report,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("arquivos", nargs="+", type=Path, help="CSVs exportados do Meta/Google")
    parser.add_argument("--vendas", type=Path, help="CSV comercial: campanha, vendas, receita")
    parser.add_argument("--margem", type=Decimal, help="margem de contribuição (0.35 = 35%%)")
    parser.add_argument("--minimo", type=int, help="volume mínimo para entrar no ranking")
    parser.add_argument("--cpl-alvo", type=Decimal, help="custo máximo aceitável por lead (R$)")
    parser.add_argument("--cpa-alvo", type=Decimal, help="custo máximo aceitável por venda (R$)")
    parser.add_argument("--saida", type=Path, help="pasta para salvar relatorio.md e resultado.json")
    args = parser.parse_args(argv)
    if args.margem is not None and not (Decimal(0) < args.margem <= Decimal(1)):
        parser.error("--margem deve estar entre 0 e 1 (ex.: 0.35).")
    try:
        result = analyze(args.arquivos, args.vendas, args.margem, args.minimo,
                         args.cpl_alvo, args.cpa_alvo)
    except (LeituraErro, FileNotFoundError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    if args.saida:
        args.saida.mkdir(parents=True, exist_ok=True)
        (args.saida / "relatorio.md").write_text(result["report_markdown"], encoding="utf-8")
        (args.saida / "resultado.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(f"Relatório salvo em {args.saida}/relatorio.md")
    print(result["report_markdown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
