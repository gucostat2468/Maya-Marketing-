"""Distribuição do orçamento diário entre campanhas, respeitando um limite.

Regras determinísticas, aplicadas depois das decisões de `decisoes.py`:
- PAUSAR: orçamento vai a zero e a verba é liberada.
- ESCALAR: aumento de até 20% por ajuste (boa prática de mercado para não reiniciar o
  aprendizado; não é regra oficial da plataforma), enquanto couber no limite.
- Demais decisões: mantêm o gasto atual.
- Se o total passar do limite, os aumentos são cortados primeiro; se ainda passar, as
  campanhas que não estão em ESCALAR são reduzidas na mesma proporção.
- A sobra vira reserva de teste: duplicar a vencedora para público novo, ou criar um teste,
  só quando a sobra paga pelo menos 1 lead por dia na meta (senão o teste não aprende).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

PASSO_ESCALA = Decimal("0.20")


def _m(v: Decimal) -> str:
    text = f"{float(v):,.2f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return "R$ " + text


def _r(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def distribuir(campanhas: list[dict[str, Any]], limite_diario: Decimal,
               custo_lead_ref: Decimal | None) -> dict[str, Any]:
    """campanhas: [{nome, gasto_dia (Decimal), acao}]. Retorna linhas, sobra e recomendação."""
    linhas = []
    for c in campanhas:
        atual = c["gasto_dia"] or Decimal(0)
        if c["acao"] == "PAUSAR":
            novo = Decimal(0)
        elif c["acao"] == "ESCALAR":
            novo = atual * (1 + PASSO_ESCALA)
        else:
            novo = atual
        linhas.append({"nome": c["nome"], "acao": c["acao"], "atual": atual, "novo": novo})

    avisos: list[str] = []
    total = sum(l["novo"] for l in linhas)
    if total > limite_diario:  # 1º: tirar os aumentos, do menor ganho para o maior
        excesso = total - limite_diario
        for l in linhas:
            if l["acao"] == "ESCALAR" and excesso > 0:
                corte = min(l["novo"] - l["atual"], excesso)
                l["novo"] -= corte
                excesso -= corte
        total = sum(l["novo"] for l in linhas)
        if total > limite_diario:  # 2º: o gasto atual já estoura o limite
            fixos = sum(l["novo"] for l in linhas if l["acao"] == "ESCALAR")
            outros = total - fixos
            if outros > 0 and limite_diario > fixos:
                fator = (limite_diario - fixos) / outros
                for l in linhas:
                    if l["acao"] != "ESCALAR":
                        l["novo"] *= fator
            else:
                fator = limite_diario / total
                for l in linhas:
                    l["novo"] *= fator
            avisos.append("O gasto atual já passa do limite: as campanhas que não estão em "
                          "escala foram reduzidas na mesma proporção.")
        else:
            avisos.append("O limite não comporta todo o aumento de 20%: a escala foi parcial.")

    for l in linhas:
        l["atual"], l["novo"] = _r(l["atual"]), _r(l["novo"])
        l["variacao"] = _r(l["novo"] - l["atual"])
    total = sum(l["novo"] for l in linhas)
    sobra = _r(limite_diario - total)
    tem_vencedora = any(l["acao"] == "ESCALAR" for l in linhas)

    if sobra <= 0:
        recomendacao = "Sem sobra: todo o limite está alocado. Não crie campanha nova agora."
    elif custo_lead_ref is None:
        recomendacao = (f"Sobra de {_m(sobra)}/dia. Sem meta de custo por lead não dá para dizer "
                        "se a sobra sustenta um teste: informe a meta.")
    elif sobra >= custo_lead_ref:
        if tem_vencedora:
            recomendacao = (f"Sobra de {_m(sobra)}/dia: **duplique o conjunto vencedor para um "
                            "público novo** (outra cidade ou outro público) com essa verba. É a "
                            "forma mais segura de crescer.")
        else:
            recomendacao = (f"Sobra de {_m(sobra)}/dia: use em **um teste novo** (criativo novo "
                            "na melhor campanha ou um conjunto novo). Um teste por vez.")
    else:
        recomendacao = (f"Sobra de {_m(sobra)}/dia, menor que 1 lead por dia na meta "
                        f"({_m(custo_lead_ref)}): **não abra campanha nova**, o teste não "
                        "aprenderia. Guarde como reserva ou some à melhor campanha.")
    return {"limite": _r(limite_diario), "total": _r(total), "sobra": sobra,
            "linhas": linhas, "recomendacao": recomendacao, "avisos": avisos}
