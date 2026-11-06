"""Testes da ferramenta de análise. Rodar: python3 -m unittest discover ferramentas/tests"""

import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ferramentas.analisar_campanhas import analyze, parse_number, poisson_ci  # noqa: E402

FX = Path(__file__).parent / "fixtures"


def by_name(result, name):
    return next(c for c in result["campaigns"] if c["campaign"] == name)


class ParseNumberTest(unittest.TestCase):
    def test_formatos(self):
        self.assertEqual(parse_number("R$ 1.234,56", "pt"), Decimal("1234.56"))
        self.assertEqual(parse_number("1,234.56", "en"), Decimal("1234.56"))
        self.assertEqual(parse_number("1.234", "pt"), Decimal("1234"))
        self.assertEqual(parse_number("1,234", "en"), Decimal("1234"))
        self.assertEqual(parse_number("12,5%", "pt"), Decimal("12.5"))
        self.assertEqual(parse_number("0", "pt"), Decimal("0"))

    def test_ausente_nao_vira_zero(self):
        for token in ("--", "", " ", "N/A"):
            self.assertIsNone(parse_number(token, "pt"))


class AnaliseTest(unittest.TestCase):
    def setUp(self):
        self.r = analyze([FX / "meta_exemplo.csv", FX / "google_exemplo.csv"],
                         FX / "vendas_exemplo.csv", Decimal("0.4"))

    def test_metricas_basicas(self):
        c = by_name(self.r, "[TESTE] Leads Proteção Familiar")
        self.assertEqual(c["base"]["spend"], 1250.0)
        self.assertAlmostEqual(c["metrics"]["cpl"]["value"], 1250 / 95)
        self.assertAlmostEqual(c["metrics"]["cpc"]["value"], 1250 / 1700)
        self.assertAlmostEqual(c["metrics"]["roas"]["value"], 5400 / 1250)
        self.assertAlmostEqual(c["roi"]["value"], (5400 * 0.4 - 1250) / 1250)

    def test_linhas_de_total_ignoradas(self):
        names = [c["campaign"] for c in self.r["campaigns"]]
        self.assertFalse(any(n.lower().startswith("total") for n in names))
        self.assertEqual(len(names), 6)

    def test_google_com_linhas_de_titulo(self):
        c = by_name(self.r, "[TESTE] Pesquisa Marca")
        self.assertEqual(c["platform"], "google_ads")
        self.assertEqual(c["base"]["leads"], 40.0)

    def test_campanha_de_alcance_nao_tem_leads_inventados(self):
        c = by_name(self.r, "[TESTE] Alcance Marca")
        self.assertIsNone(c["base"]["leads"])
        self.assertEqual(c["metrics"]["cpl"]["status"], "no_data")

    def test_vendas_ausentes_no_arquivo_comercial_sao_zero_e_cpa_indefinido(self):
        c = by_name(self.r, "[TESTE] Leads Assistência")
        self.assertEqual(c["base"]["sales"], 0.0)
        self.assertEqual(c["metrics"]["cpa"]["status"], "undefined")

    def test_ranking_usa_cpa_quando_ha_vendas_e_exige_volume(self):
        self.assertEqual(self.r["metric"], "cpa")
        self.assertEqual(self.r["ranking"][0], "[TESTE] Pesquisa Marca")
        self.assertNotIn("[TESTE] Pesquisa Genérica", self.r["ranking"])  # só 1 venda

    def test_sem_vendas_ranking_por_cpl_e_sem_roi(self):
        r = analyze([FX / "meta_exemplo.csv"])
        self.assertEqual(r["metric"], "cpl")
        self.assertEqual(r["ranking"][0], "[TESTE] Leads Proteção Familiar")
        self.assertIn("não há conclusão sobre retorno comercial", r["report_markdown"])
        c = by_name(r, "[TESTE] Leads Proteção Familiar")
        self.assertIsNone(c["base"]["sales"])
        self.assertEqual(c["roi"]["status"], "no_data")

    def test_arquivo_duplicado_nao_infla(self):
        r = analyze([FX / "meta_exemplo.csv", FX / "meta_exemplo.csv"])
        self.assertEqual(by_name(r, "[TESTE] Leads Proteção Familiar")["base"]["spend"], 1250.0)
        self.assertTrue(r["warnings"])

    def test_amostra_pequena_sinalizada(self):
        tipos = {(d["campanha"], d["tipo"]) for d in self.r["diagnostics"]}
        self.assertIn(("[TESTE] Leads Teste", "amostra_pequena"), tipos)

    def test_intervalo_poisson(self):
        low, high = poisson_ci(100)
        self.assertTrue(80 < low < 100 < high < 122)


if __name__ == "__main__":
    unittest.main()
