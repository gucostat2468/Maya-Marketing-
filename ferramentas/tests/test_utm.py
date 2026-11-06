import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ferramentas.utm import UtmErro, auditar_url, gerar, slug  # noqa: E402


class UtmTest(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(slug("Leads Proteção Familiar  SP!"), "leads-protecao-familiar-sp")

    def test_gerar_normaliza_e_preserva_parametros(self):
        url = gerar("https://site.com.br/plano?ref=abc&utm_source=velho", "Instagram",
                    "paid_social", "Leads Proteção Familiar 202611", "Vídeo Depoimento")
        q = parse_qs(urlsplit(url).query)
        self.assertEqual(q["ref"], ["abc"])
        self.assertEqual(q["utm_source"], ["instagram"])
        self.assertEqual(q["utm_campaign"], ["leads-protecao-familiar-202611"])
        self.assertEqual(q["utm_content"], ["video-depoimento"])

    def test_gerar_rejeita_fora_do_padrao(self):
        with self.assertRaises(UtmErro):
            gerar("https://site.com.br", "tiktokzz", "cpc", "x")
        with self.assertRaises(UtmErro):
            gerar("https://site.com.br", "google", "pago", "x")
        with self.assertRaises(UtmErro):
            gerar("site.com.br", "google", "cpc", "x")

    def test_auditar(self):
        self.assertEqual(auditar_url(gerar("https://a.com", "google", "cpc", "teste")), [])
        problemas = auditar_url("https://a.com/?UTM_Source=Facebook&utm_medium=Pago")
        texto = " ".join(problemas)
        self.assertIn("falta utm_campaign", texto)
        self.assertIn("maiúscula", texto)
        self.assertIn("Unassigned", texto)

    def test_auditar_aceita_parametros_dinamicos(self):
        url = ("https://a.com/?utm_source={{site_source_name}}&utm_medium=paid_social"
               "&utm_campaign={{campaign.name}}")
        self.assertEqual(auditar_url(url), [])


if __name__ == "__main__":
    unittest.main()
