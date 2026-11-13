#!/usr/bin/env python3
"""Empacota uma ou mais peças HTML em UM arquivo autocontido, com um slide por peça.

Serve para importar as peças em editores (Adobe Express, Canva) mantendo texto editável:
imagens viram base64, o CSS de cada peça fica isolado no seu slide.
Uso: python3 ferramentas/empacotar_html.py <saida.html> <largura> <altura> <peca1.html> [peca2.html ...]
"""
from __future__ import annotations

import base64
import io
import re
import sys
from pathlib import Path

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml"}


def _data_uri(path: Path, largura_max: int) -> str:
    dados = path.read_bytes()
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        try:  # fotos grandes são reduzidas para o arquivo não ficar pesado
            from PIL import Image
            im = Image.open(io.BytesIO(dados))
            if im.width > largura_max * 2:
                im.thumbnail((largura_max * 2, largura_max * 4))
                buf = io.BytesIO()
                im.convert("RGB").save(buf, "JPEG", quality=88)
                dados = buf.getvalue()
        except ImportError:
            pass
    return f"data:{MIME.get(ext, 'application/octet-stream')};base64,{base64.b64encode(dados).decode()}"


def _escopo(css: str, alvo: str) -> str:
    """Troca os seletores de html/body pelo seletor do slide."""
    css = re.sub(r"html\s*,\s*body\s*\{", f"{alvo} {{", css)
    css = re.sub(r"(^|[\s,}])body(?=[.\s{,])", lambda m: m.group(1) + alvo, css)
    css = re.sub(r":root\s*\{", f"{alvo} {{", css)
    saida, pos = [], 0
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel, corpo = m.group(1), m.group(2)
        if sel.strip().startswith("@"):
            saida.append(m.group(0))
            continue
        partes = [s.strip() for s in sel.split(",") if s.strip()]
        novo = ", ".join(p if p.startswith(alvo) or p in ("from", "to") or p.endswith("%") else f"{alvo} {p}" for p in partes)
        saida.append(f"{novo} {{{corpo}}}")
    return "\n".join(saida)


def empacotar(saida: Path, largura: int, altura: int, pecas: list[Path]) -> None:
    links, slides, estilos = [], [], []
    for i, peca in enumerate(pecas, 1):
        html = peca.read_text(encoding="utf-8")
        for link in re.findall(r"<link[^>]+fonts\.googleapis[^>]+>", html):
            if link not in links:
                links.append(link)
        css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.S))
        for href in re.findall(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"', html):
            if not href.startswith("http"):
                css = (peca.parent / href).read_text(encoding="utf-8") + "\n" + css
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        m = re.search(r"<body([^>]*)>(.*?)</body>", html, flags=re.S)
        attrs, corpo = m.group(1), re.sub(r"<script.*?</script>", "", m.group(2), flags=re.S)
        classes = re.search(r'class="([^"]*)"', attrs)
        classes = classes.group(1) if classes else ""
        corpo = re.sub(r'src="([^"]+)"', lambda s: s.group(0) if s.group(1).startswith(("data:", "http"))
                       else f'src="{_data_uri((peca.parent / s.group(1)).resolve(), largura)}"', corpo)
        corpo = re.sub(r'id="([\w-]+)"', rf'id="s{i}-\1"', corpo)
        corpo = re.sub(r"url\(#([\w-]+)\)", rf"url(#s{i}-\1)", corpo)
        alvo = f".slide.s{i}"
        estilos.append(_escopo(css, alvo))
        slides.append(f'<div class="slide s{i} {classes}" data-document-role="page" data-label="{peca.stem}" '
                      f'data-canvas-width="{largura}" data-canvas-height="{altura}">{corpo}</div>')
    doc = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{saida.stem}</title>'
           f'<meta name="hz:slide-selector" content=".slide"><meta name="hz:canvas-width" content="{largura}">'
           f'<meta name="hz:canvas-height" content="{altura}">' + "".join(links) +
           f"<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{margin:0;background:#ddd}}"
           f".slide{{position:relative;width:{largura}px;height:{altura}px;overflow:hidden;margin:0 auto}}\n"
           + "\n".join(estilos) + "</style></head><body>" + "\n".join(slides) + "</body></html>")
    saida.write_text(doc, encoding="utf-8")
    print(f"{len(pecas)} slide(s) em {saida} ({saida.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    empacotar(Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), [Path(p) for p in sys.argv[4:]])
