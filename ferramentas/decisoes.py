"""Motor de decisão por campanha: PAUSAR, AGUARDAR, AJUSTAR, MANTER ou ESCALAR.

Regras determinísticas (sem IA), explicáveis e testadas. A decisão olha primeiro para
VENDAS (CPA) quando há dados do comercial, e para LEADS (CPL) quando não há. Toda decisão
considera o tamanho da amostra: com pouco volume a resposta é "aguardar", não "vencedora".

As regras de escala (até +20% a cada 2-3 dias, duplicar para público novo) são boas práticas
de mercado, não regras oficiais das plataformas, e aparecem assim no relatório.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from ferramentas.estatistica import poisson_ci

ACOES = {
    "PAUSAR": "Pausar",
    "AJUSTAR": "Ajustar antes de pausar",
    "AGUARDAR": "Aguardar (não mexer)",
    "MANTER": "Manter",
    "ESCALAR": "Escalar",
    "VERIFICAR": "Verificar rastreamento",
    "SEM_DADOS": "Sem dados",
    "OUTRO_OBJETIVO": "Outro objetivo",
}
MINIMO = {"cpa": 5, "cpl": 10}  # volume mínimo para julgar com alguma confiança
FREQUENCIA_ALTA = Decimal("3.5")


def _money(v: Decimal | float) -> str:
    text = f"{float(v):,.2f}"
    return "R$ " + text.replace(",", "§").replace(".", ",").replace("§", ".")


def decidir(base: dict[str, Decimal | None], platform: str, metrica: str, alvo: Decimal,
            alvo_provisorio: bool, serie: list[dict[str, Any]] | None = None,
            objetivo_lead: bool | None = None) -> dict[str, Any]:
    """Decide o que fazer com uma campanha.

    metrica: "cpa" (vendas) ou "cpl" (leads). alvo: custo máximo aceitável por resultado.
    """
    spend = base.get("spend")
    count = base.get("sales") if metrica == "cpa" else base.get("leads")
    nome_res = "vendas" if metrica == "cpa" else "leads"
    alertas: list[str] = []
    if alvo_provisorio:
        alertas.append("Meta provisória (média da conta). Informe a sua meta para decisões melhores.")

    # Sinais complementares que não mudam a decisão principal, mas pedem ação.
    reach, impressions = base.get("reach"), base.get("impressions")
    freq = impressions / reach if reach and impressions else None
    if platform == "meta_ads" and freq is not None and freq >= FREQUENCIA_ALTA:
        alertas.append(f"Frequência {float(freq):.1f}: a mesma pessoa viu o anúncio muitas vezes. "
                       "Troque o criativo (sinal de fadiga).")
    if metrica == "cpa" and base.get("leads") and base["leads"] >= 15 and count == 0:
        alertas.append(f"{int(base['leads'])} leads e nenhuma venda: os leads desta campanha "
                       "não estão virando cliente (lead frio ou atendimento).")
    tendencia = _tendencia(serie or [], metrica)
    if tendencia:
        alertas.append(tendencia)

    def out(acao: str, motivo: str, fazer: str, confianca: str,
            faixa: tuple[float | None, float | None] = (None, None)) -> dict[str, Any]:
        return {"acao": acao, "rotulo": ACOES[acao], "motivo": motivo, "fazer": fazer,
                "confianca": confianca, "metrica": metrica, "alvo": float(alvo),
                "faixa": faixa, "alertas": alertas}

    if not spend:
        return out("SEM_DADOS", "Sem investimento no período.", "Nada a decidir.", "-")
    if objetivo_lead is False:
        return out("OUTRO_OBJETIVO", "Campanha com objetivo diferente de leads (ex.: alcance).",
                   "Não julgue por custo por lead. Avalie pelo objetivo dela (alcance, CPM) e pelo "
                   "efeito nas campanhas de leads.", "-")
    if count is None:
        return out("VERIFICAR", f"Há investimento, mas nenhum dado de {nome_res}.",
                   "Confira se a conversão está sendo registrada (pixel, GTM, formulário) e se "
                   "a coluna foi exportada.", "-")

    orcamento_teste = alvo * 2
    if count == 0:
        if spend >= orcamento_teste:
            return out("PAUSAR", f"Gastou {_money(spend)} (mais de 2x a meta de {_money(alvo)}) "
                       f"sem nenhuma {nome_res[:-1]}.",
                       "Pause e leve a verba para a campanha mais eficiente. Antes, confirme que a "
                       "conversão está sendo registrada.", "média")
        falta = orcamento_teste - spend
        return out("AGUARDAR", f"Ainda dentro do orçamento de teste (2x a meta = "
                   f"{_money(orcamento_teste)}).",
                   f"Não mexa. Reavalie depois de gastar mais {_money(falta)} sem resultado.",
                   "baixa")

    n = int(count)
    low, high = poisson_ci(n)
    custo = spend / count
    melhor = float(spend) / high  # custo plausível mais baixo
    pior = float(spend) / low if low > 0 else None  # custo plausível mais alto
    faixa = (melhor, pior)

    if n < MINIMO[metrica]:
        if custo > alvo * 2 and spend >= alvo * 3:
            return out("PAUSAR", f"{n} {nome_res if n != 1 else nome_res[:-1]} a {_money(custo)} cada: mais que o dobro da meta, "
                       "mesmo com pouca amostra e gasto alto.",
                       "Pause ou reduza bastante a verba; reveja oferta, público e página.",
                       "média", faixa)
        return out("AGUARDAR", f"Só {n} {nome_res if n != 1 else nome_res[:-1]}: pouca amostra para concluir "
                   f"(mínimo {MINIMO[metrica]}).",
                   "Não mexa: mudanças reiniciam o aprendizado da plataforma. Reavalie quando "
                   f"chegar a {MINIMO[metrica]} {nome_res}.", "baixa", faixa)

    conf = "alta" if n >= 30 else "média"
    if pior is not None and pior <= float(alvo):
        return out("ESCALAR", f"Custo de {_money(custo)} por {nome_res[:-1]}; mesmo no pior cenário "
                   f"({_money(pior)}) fica abaixo da meta de {_money(alvo)}.",
                   "Aumente o orçamento em até 20% a cada 2 a 3 dias enquanto o custo seguir abaixo "
                   "da meta. Para crescer mais rápido, duplique o conjunto vencedor para um público "
                   "novo, em vez de dobrar o orçamento de uma vez. (Boa prática de mercado, não "
                   "regra oficial da plataforma.)", conf, faixa)
    if melhor > float(alvo):
        if custo > alvo * Decimal("1.5"):
            return out("PAUSAR", f"Custo de {_money(custo)}, mais de 50% acima da meta de "
                       f"{_money(alvo)}, com volume suficiente para confiar.",
                       "Pause e redistribua a verba. Se for a única campanha, refaça criativo e "
                       "público antes de reativar.", conf, faixa)
        return out("AJUSTAR", f"Custo de {_money(custo)}, acima da meta de {_money(alvo)} "
                   "mesmo no melhor cenário, mas perto dela.",
                   "Não pause ainda: teste um criativo novo ou um público mais específico e "
                   "reavalie em 3 dias.", conf, faixa)
    if custo > alvo:
        return out("AJUSTAR", f"Custo de {_money(custo)}, acima da meta de {_money(alvo)}, mas com "
                   "volume que ainda não permite cravar que é ruim.",
                   "Não aumente a verba. Teste um criativo novo ou um público mais específico e "
                   "reavalie em 3 dias.", "baixa", faixa)
    return out("MANTER", f"Custo de {_money(custo)}: dentro da meta de {_money(alvo)}, mas ainda "
               "sem folga para escalar com segurança.",
               "Mantenha como está e reavalie em 3 dias.", conf, faixa)


def _tendencia(serie: list[dict[str, Any]], metrica: str) -> str | None:
    """Compara o custo dos últimos 3 dias com os dias anteriores (só para leads)."""
    if metrica != "cpl":
        return None
    dias = sorted((d for d in serie if d.get("day") and d.get("spend") is not None),
                  key=lambda d: d["day"])
    if len(dias) < 6:
        return None
    rec, ant = dias[-3:], dias[:-3]
    s_rec = sum(d["spend"] for d in rec)
    s_ant = sum(d["spend"] for d in ant)
    l_rec = sum(d["leads"] or 0 for d in rec)
    l_ant = sum(d["leads"] or 0 for d in ant)
    if l_ant < 5:
        return None
    custo_ant = s_ant / l_ant
    if l_rec == 0:
        return (f"Últimos 3 dias: {_money(s_rec)} gastos e nenhum lead (antes: {_money(custo_ant)} "
                "por lead). Pode ser fadiga ou problema no rastreamento.")
    custo_rec = s_rec / l_rec
    if custo_rec > custo_ant * Decimal("1.3"):
        return (f"Piorando: custo por lead de {_money(custo_rec)} nos últimos 3 dias contra "
                f"{_money(custo_ant)} antes (+{float(custo_rec / custo_ant - 1) * 100:.0f}%).")
    return None
