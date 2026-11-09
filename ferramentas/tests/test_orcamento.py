import sys
import unittest
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.analisar_campanhas import analyze  # noqa: E402
from ferramentas.orcamento import distribuir  # noqa: E402

FX = Path(__file__).parent / "fixtures"


def camp(nome, gasto, acao):
    return {"nome": nome, "gasto_dia": D(gasto), "acao": acao}


class OrcamentoTest(unittest.TestCase):
    def test_pausa_libera_e_vencedora_sobe_20(self):
        o = distribuir([camp("a", 50, "ESCALAR"), camp("b", 30, "PAUSAR"), camp("c", 20, "MANTER")],
                       D(120), D(25))
        novo = {l["nome"]: l["novo"] for l in o["linhas"]}
        self.assertEqual(novo, {"a": D("60.00"), "b": D("0.00"), "c": D("20.00")})
        self.assertEqual(o["sobra"], D("40.00"))
        self.assertIn("duplique", o["recomendacao"])

    def test_nunca_passa_do_limite(self):
        o = distribuir([camp("a", 50, "ESCALAR"), camp("c", 48, "MANTER")], D(100), D(25))
        self.assertLessEqual(o["total"], D("100.00"))
        self.assertEqual({l["nome"]: l["novo"] for l in o["linhas"]}["a"], D("52.00"))
        self.assertTrue(o["avisos"])

    def test_gasto_atual_acima_do_limite_reduz_as_outras(self):
        o = distribuir([camp("a", 60, "ESCALAR"), camp("b", 60, "AJUSTAR"), camp("c", 30, "MANTER")],
                       D(120), D(25))
        novo = {l["nome"]: l["novo"] for l in o["linhas"]}
        self.assertEqual(novo["a"], D("60.00"))
        self.assertEqual(novo["b"] + novo["c"], D("60.00"))
        self.assertEqual(o["total"], D("120.00"))

    def test_sobra_pequena_nao_abre_campanha(self):
        o = distribuir([camp("a", 90, "MANTER")], D(100), D(25))
        self.assertIn("não abra campanha nova", o["recomendacao"])

    def test_sobra_sem_vencedora_vira_teste(self):
        o = distribuir([camp("a", 40, "MANTER")], D(100), D(25))
        self.assertIn("teste novo", o["recomendacao"])

    def test_integrado_no_relatorio(self):
        r = analyze([FX / "meta_exemplo.csv", FX / "google_exemplo.csv"], cpl_alvo=D(25),
                    orcamento_diario=D(120))
        self.assertEqual(r["orcamento"]["dias"], 31)  # período lido do arquivo do Meta
        self.assertLessEqual(r["orcamento"]["total"], D("120.00"))
        self.assertIn("Quanto investir por dia", r["report_markdown"])


if __name__ == "__main__":
    unittest.main()
