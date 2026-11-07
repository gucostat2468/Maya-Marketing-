"""Testes das regras de decisão por campanha."""

import sys
import tempfile
import unittest
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.analisar_campanhas import analyze  # noqa: E402
from ferramentas.decisoes import decidir  # noqa: E402

FX = Path(__file__).parent / "fixtures"


def base(**kw):
    b = {"spend": None, "leads": None, "sales": None, "impressions": None, "reach": None,
         "clicks": None}
    b.update({k: D(str(v)) for k, v in kw.items()})
    return b


class RegrasTest(unittest.TestCase):
    def d(self, b, metrica="cpl", alvo=25, plat="meta_ads", **kw):
        return decidir(b, plat, metrica, D(alvo), False, **kw)

    def test_sem_resultado_dentro_do_teste_aguarda(self):
        self.assertEqual(self.d(base(spend=30, leads=0))["acao"], "AGUARDAR")

    def test_sem_resultado_apos_2x_meta_pausa(self):
        self.assertEqual(self.d(base(spend=60, leads=0))["acao"], "PAUSAR")

    def test_pouca_amostra_aguarda(self):
        self.assertEqual(self.d(base(spend=60, leads=3))["acao"], "AGUARDAR")

    def test_bem_abaixo_da_meta_com_volume_escala(self):
        self.assertEqual(self.d(base(spend=600, leads=60))["acao"], "ESCALAR")

    def test_muito_acima_da_meta_com_volume_pausa(self):
        self.assertEqual(self.d(base(spend=2000, leads=40))["acao"], "PAUSAR")

    def test_um_pouco_acima_ajusta(self):
        self.assertEqual(self.d(base(spend=600, leads=20))["acao"], "AJUSTAR")

    def test_na_meta_mantem(self):
        self.assertEqual(self.d(base(spend=480, leads=20))["acao"], "MANTER")

    def test_sem_dado_de_conversao_verifica_rastreamento(self):
        self.assertEqual(self.d(base(spend=100))["acao"], "VERIFICAR")

    def test_objetivo_de_alcance_nao_e_julgado_por_lead(self):
        self.assertEqual(self.d(base(spend=100), objetivo_lead=False)["acao"], "OUTRO_OBJETIVO")

    def test_frequencia_alta_gera_alerta_de_criativo(self):
        r = self.d(base(spend=600, leads=60, impressions=40000, reach=8000))
        self.assertTrue(any("Frequência" in a for a in r["alertas"]))

    def test_leads_sem_venda_alerta(self):
        r = self.d(base(spend=900, leads=40, sales=0), metrica="cpa", alvo=150)
        self.assertEqual(r["acao"], "PAUSAR")
        self.assertTrue(any("nenhuma venda" in a for a in r["alertas"]))

    def test_tendencia_piorando(self):
        serie = [{"day": f"2026-11-0{i}", "spend": D(50), "leads": D(5)} for i in range(1, 5)]
        serie += [{"day": f"2026-11-0{i}", "spend": D(50), "leads": D(1)} for i in range(5, 8)]
        r = self.d(base(spend=350, leads=23), serie=serie)
        self.assertTrue(any("Piorando" in a for a in r["alertas"]))


class IntegracaoTest(unittest.TestCase):
    def test_venda_manda_quando_ha_dado_comercial(self):
        r = analyze([FX / "meta_exemplo.csv", FX / "google_exemplo.csv"], FX / "vendas_exemplo.csv",
                    cpa_alvo=D(150))
        dec = {c["campaign"]: c["decisao"]["acao"] for c in r["campaigns"]}
        self.assertEqual(dec["[TESTE] Pesquisa Marca"], "ESCALAR")
        self.assertEqual(dec["[TESTE] Leads Assistência"], "PAUSAR")
        self.assertEqual(dec["[TESTE] Alcance Marca"], "OUTRO_OBJETIVO")
        self.assertIn("O que fazer com cada campanha", r["report_markdown"])

    def test_sem_meta_usa_media_da_conta_e_avisa(self):
        r = analyze([FX / "meta_exemplo.csv"])
        d = next(c["decisao"] for c in r["campaigns"] if c["campaign"] == "[TESTE] Leads Teste")
        self.assertTrue(any("provisória" in a for a in d["alertas"]))
        self.assertIn("provisória", r["report_markdown"])

    def test_csv_diario_detecta_tendencia(self):
        linhas = ["Dia,Nome da campanha,Valor usado (BRL),Impressões,Alcance,Cliques no link,"
                  "Resultados,Indicador de resultados"]
        for i in range(1, 8):
            leads = 6 if i <= 4 else 1
            linhas.append(f"2026-11-0{i},[TESTE] Diario,\"50,00\",4000,3000,80,{leads},"
                          "actions:onsite_conversion.lead_grouped")
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "diario.csv"
            p.write_text("\n".join(linhas), encoding="utf-8")
            r = analyze([p], cpl_alvo=D(25))
        d = r["campaigns"][0]["decisao"]
        self.assertTrue(any("Piorando" in a for a in d["alertas"]), d["alertas"])


if __name__ == "__main__":
    unittest.main()
