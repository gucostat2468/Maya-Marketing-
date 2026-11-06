#!/usr/bin/env python3
"""UTMs da Maya Protege: gerar links, modelos dinâmicos para Meta/Google e auditar links.

Usado pelo agente ``especialista-utm``. Só biblioteca padrão.

    python3 ferramentas/utm.py gerar --url https://site.com/plano --source instagram \\
        --medium paid_social --campaign "Leads Proteção Familiar SP 202611" --content video-depoimento
    python3 ferramentas/utm.py modelos
    python3 ferramentas/utm.py auditar links.csv        # CSV com uma coluna "url"
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

CONVENCAO = json.loads(
    (Path(__file__).resolve().parents[1] / "marketing/utm/convencao.json").read_text("utf-8"))
UTM_KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "utm_id"]
DYNAMIC = re.compile(r"\{\{?[\w.]+\}?\}")  # {{campaign.name}} (Meta) ou {keyword} (Google)


def slug(text: str) -> str:
    """'Leads Proteção Familiar SP' -> 'leads-protecao-familiar-sp'."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    text = re.sub(r"[^a-z0-9_]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-")


class UtmErro(ValueError):
    pass


def gerar(url: str, source: str, medium: str, campaign: str,
          content: str | None = None, term: str | None = None) -> str:
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise UtmErro("A URL precisa começar com https:// e ter um domínio.")
    source, medium = slug(source), slug(medium).replace("-", "_")
    if source not in CONVENCAO["sources"]:
        raise UtmErro(f"utm_source '{source}' fora do padrão. Use: "
                      + ", ".join(CONVENCAO["sources"]))
    if medium not in CONVENCAO["mediums"]:
        raise UtmErro(f"utm_medium '{medium}' fora do padrão. Use: "
                      + ", ".join(CONVENCAO["mediums"]))
    utms = {"utm_source": source, "utm_medium": medium, "utm_campaign": slug(campaign)}
    if content:
        utms["utm_content"] = slug(content)
    if term:
        utms["utm_term"] = slug(term)
    # Mantém parâmetros já existentes (que não sejam UTM) e substitui UTMs antigas.
    kept = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
            if k.lower() not in UTM_KEYS]
    query = urlencode(kept + list(utms.items()))
    return urlunsplit((parts.scheme, parts.netloc, parts.path or "/", query, parts.fragment))


def auditar_url(url: str) -> list[str]:
    problemas: list[str] = []
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https"):
        problemas.append("URL sem http(s)")
    params = parse_qsl(parts.query, keep_blank_values=True)
    keys = [k for k, _ in params]
    lower = {k.lower(): v for k, v in params}
    for key in CONVENCAO["obrigatorios"]:
        if key not in lower:
            problemas.append(f"falta {key}")
        elif not lower[key].strip():
            problemas.append(f"{key} vazio")
    for k in keys:
        if k.lower().startswith("utm_") and k != k.lower():
            problemas.append(f"parâmetro '{k}' com maiúscula (o GA4 diferencia)")
        if keys.count(k) > 1:
            problemas.append(f"parâmetro '{k}' repetido")
    for key in ("utm_source", "utm_medium", "utm_campaign", "utm_content"):
        value = lower.get(key)
        if not value or DYNAMIC.search(value):
            continue  # valores dinâmicos são preenchidos pela plataforma
        if value != slug(value).replace("-", "_" if key == "utm_medium" else "-"):
            problemas.append(f"{key}='{value}' fora do padrão (minúsculas, sem acento, hífen)")
    if lower.get("utm_source") and not DYNAMIC.search(lower["utm_source"]) \
            and lower["utm_source"] not in CONVENCAO["sources"]:
        problemas.append(f"utm_source '{lower['utm_source']}' não está na convenção")
    if lower.get("utm_medium") and lower["utm_medium"] not in CONVENCAO["mediums"]:
        problemas.append(f"utm_medium '{lower['utm_medium']}' não está na convenção "
                         "(o GA4 pode classificar como Unassigned)")
    return list(dict.fromkeys(problemas))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="UTMs da Maya Protege")
    sub = parser.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gerar", help="gera um link com UTMs")
    g.add_argument("--url", required=True)
    g.add_argument("--source", required=True)
    g.add_argument("--medium", required=True)
    g.add_argument("--campaign", required=True)
    g.add_argument("--content")
    g.add_argument("--term")
    sub.add_parser("modelos", help="parâmetros dinâmicos para colar no Meta e no Google Ads")
    a = sub.add_parser("auditar", help="audita um CSV com coluna 'url'")
    a.add_argument("arquivo", type=Path)
    args = parser.parse_args(argv)

    if args.cmd == "gerar":
        try:
            print(gerar(args.url, args.source, args.medium, args.campaign, args.content, args.term))
        except UtmErro as exc:
            print(f"Erro: {exc}", file=sys.stderr)
            return 2
    elif args.cmd == "modelos":
        din = CONVENCAO["parametros_dinamicos"]
        print("Meta Ads (anúncio > Rastreamento > Parâmetros de URL):\n  " + din["meta"])
        print("\nGoogle Ads (Campanha > Configurações > Opções de URL > Sufixo do URL final):\n  "
              + din["google"])
        print("\nObs.: no Google, troque {_campanha} por um parâmetro personalizado com o nome "
              "da campanha no padrão, e mantenha a codificação automática (gclid) ativada.")
    else:
        with args.arquivo.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
        ok = 0
        for i, row in enumerate(rows, 2):
            url = (row.get("url") or "").strip()
            problemas = auditar_url(url) if url else ["linha sem URL"]
            if problemas:
                print(f"linha {i}: {url}\n  - " + "\n  - ".join(problemas))
            else:
                ok += 1
        print(f"\n{ok} de {len(rows)} links dentro do padrão.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
