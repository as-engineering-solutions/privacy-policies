#!/usr/bin/env python3
"""Render the reviewed plain-text policies as static, accessible HTML."""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
DOCS = ROOT / "docs"
BASE = "https://as-engineering-solutions.github.io/privacy-policies"
APPS = {
    "network-timer": ("Network Timer", "network-timer.txt"),
    "media-merge": ("MediaMerge", "mediamerge.txt"),
    "onecast": ("OneCast", "onecast.txt"),
}


def page(title: str, body: str, canonical: str, current: str = "") -> str:
    navigation = " ".join(
        f'<a href="{BASE}/{slug}/"'
        + (' aria-current="page"' if slug == current else "")
        + f">{html.escape(name)}</a>"
        for slug, (name, _) in APPS.items()
    )
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(title, quote=True)} de AS Engineering Solutions">
  <link rel="canonical" href="{canonical}">
  <link rel="stylesheet" href="{BASE}/assets/site.css">
  <title>{html.escape(title)} | AS Engineering Solutions</title>
</head>
<body>
  <a class="skip" href="#main">Saltar al contenido</a>
  <header class="site-header"><div class="shell header-inner">
    <a class="brand" href="{BASE}/">AS <span>Engineering Solutions</span></a>
    <nav aria-label="Aplicaciones">{navigation}</nav>
  </div></header>
  <main id="main" class="shell">{body}</main>
  <footer class="shell footer">© AS Engineering Solutions · Contacto: <a href="mailto:agustinsrur+dev@gmail.com">agustinsrur+dev@gmail.com</a></footer>
</body>
</html>
"""


def policy_body(source: str) -> str:
    paragraphs: list[str] = []
    list_items: list[str] = []

    def flush_list() -> None:
        if list_items:
            paragraphs.append("<ul>" + "".join(f"<li>{item}</li>" for item in list_items) + "</ul>")
            list_items.clear()

    lines = [line.strip() for line in source.splitlines()]
    title = html.escape(lines[0])
    paragraphs.append(f'<article class="policy"><h1>{title}</h1>')
    for line in lines[1:]:
        if not line or re.fullmatch(r"_{8,}", line):
            flush_list()
            continue
        if line.startswith(("* ", "- ")):
            list_items.append(html.escape(line[2:]))
            continue
        flush_list()
        match = re.fullmatch(r"(\d+)\.\s+(.+)", line)
        if match:
            paragraphs.append(f"<h2>{html.escape(match.group(2))}</h2>")
        elif re.fullmatch(r"[A-Z]\.\s+.+", line):
            paragraphs.append(f"<h3>{html.escape(line)}</h3>")
        else:
            klass = ' class="updated"' if line.lower().startswith(("última actualización:", "actualizada para ")) else ""
            paragraphs.append(f"<p{klass}>{html.escape(line)}</p>")
    flush_list()
    paragraphs.append("</article>")
    return "\n".join(paragraphs)


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / ".nojekyll").touch()
    cards = []
    for slug, (name, filename) in APPS.items():
        source = (SOURCE / filename).read_text(encoding="utf-8-sig")
        if not source.strip():
            raise ValueError(f"Empty policy: {filename}")
        target = DOCS / slug / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            page(f"Política de privacidad de {name}", policy_body(source), f"{BASE}/{slug}/", slug),
            encoding="utf-8",
        )
        cards.append(
            f'<li><a href="{BASE}/{slug}/"><strong>{html.escape(name)}</strong>'
            "<span>Leer política de privacidad</span></a></li>"
        )
    body = (
        '<section class="home"><p class="eyebrow">Privacidad</p>'
        "<h1>Políticas de privacidad</h1>"
        "<p>Consulta cómo cada aplicación de AS Engineering Solutions procesa tus datos.</p>"
        f'<ul class="policy-list">{"".join(cards)}</ul></section>'
    )
    (DOCS / "index.html").write_text(page("Políticas de privacidad", body, f"{BASE}/"), encoding="utf-8")


if __name__ == "__main__":
    main()
