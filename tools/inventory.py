#!/usr/bin/env python3
"""Inventario y línea de base SEO on-page para un HTML (estático o .dc.html).

Uso: python3 -I inventory.py archivo.html [--json salida.json] [--quiet]
Solo lee el archivo; no modifica nada.
"""
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser

from bs4 import BeautifulSoup

VOID = {"meta", "link", "br", "hr", "img", "input", "source", "track", "wbr",
        "area", "base", "col", "embed", "param"}

# Términos objetivo (orden de prioridad provisional, a confirmar en el Paso 1)
TERMS = [
    "clases de guitarra en Corrientes",
    "profesor de guitarra",
    "clases de bajo",
    "clases de ukelele",
    "clases de música",
    "teoría musical",
    "composición musical",
    "composición de canciones",
    "clases individuales",
    "clases grupales",
    "todas las edades",
    "niños",
    "Corrientes Capital",
    "Camba Cuá",
    "Gonzalo Corrales",
]


def norm(s):
    s = unicodedata.normalize("NFKD", s.replace(" ", " ")).lower()
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip()


class Balance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for t, ln in self.stack[i + 1:]:
                    self.errors.append(
                        f"<{t}> abierto en línea {ln} sin cerrar antes de </{tag}> (línea {self.getpos()[0]})")
                del self.stack[i:]
                return
        self.errors.append(f"</{tag}> sin apertura (línea {self.getpos()[0]})")

    def close(self):
        super().close()
        for t, ln in self.stack:
            self.errors.append(f"<{t}> de la línea {ln} nunca se cierra")


def visible_text(soup):
    s2 = BeautifulSoup(str(soup), "html.parser")
    for t in s2(["script", "style", "svg", "template"]):
        t.decompose()
    return re.sub(r"\s+", " ", s2.get_text(" ")).strip()


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    path = args[0]
    out_json = args[args.index("--json") + 1] if "--json" in args else None
    html = open(path, encoding="utf-8").read()

    bal = Balance()
    bal.feed(html)
    bal.close()

    soup = BeautifulSoup(html, "html.parser")
    inv = {"archivo": path}
    inv["lang"] = (soup.html or {}).get("lang") if soup.html else None
    inv["title"] = soup.title.get_text().strip() if soup.title else None
    inv["title_len"] = len(inv["title"]) if inv["title"] else 0

    def meta(attr, val):
        m = soup.find("meta", attrs={attr: val})
        return m.get("content") if m else None

    inv["meta_description"] = meta("name", "description")
    inv["meta_description_len"] = len(inv["meta_description"] or "")
    inv["viewport"] = meta("name", "viewport")
    inv["robots_meta"] = meta("name", "robots")
    can = soup.find("link", rel="canonical")
    inv["canonical"] = can.get("href") if can else None
    inv["og"] = {m.get("property"): m.get("content") for m in soup.find_all("meta") if (m.get("property") or "").startswith("og:")}
    inv["twitter"] = {m.get("name"): m.get("content") for m in soup.find_all("meta") if (m.get("name") or "").startswith("twitter:")}
    inv["jsonld_blocks"] = len(soup.find_all("script", type="application/ld+json"))

    heads = []
    prev, jumps = 0, []
    for h in soup.find_all(re.compile(r"^h[1-6]$")):
        lvl = int(h.name[1])
        txt = re.sub(r"\s+", " ", h.get_text()).strip()
        heads.append({"nivel": lvl, "texto": txt})
        if prev and lvl > prev + 1:
            jumps.append(f"salto h{prev} → h{lvl}: {txt}")
        prev = lvl
    inv["headings"] = heads
    inv["h1_count"] = sum(1 for h in heads if h["nivel"] == 1)
    inv["heading_jumps"] = jumps

    ids = {t.get("id") for t in soup.find_all(id=True)}
    links, broken = [], []
    for a in soup.find_all("a"):
        href = a.get("href", "")
        links.append({"href": href, "texto": re.sub(r"\s+", " ", a.get_text()).strip(), "aria-label": a.get("aria-label")})
        if href.startswith("#") and len(href) > 1 and href[1:] not in ids:
            broken.append(href)
    inv["links"] = links
    inv["anchors_rotas"] = broken

    imgs = soup.find_all("img")
    inv["img_total"] = len(imgs)
    inv["img_sin_alt"] = sum(1 for i in imgs if i.get("alt") is None)
    inv["svg_decorativos"] = sum(1 for s in soup.find_all("svg") if s.get("aria-hidden") == "true")
    inv["svg_total"] = len(soup.find_all("svg"))

    styled = soup.find_all(style=True)
    inv["style_attr_count"] = len(styled)
    inv["style_attr_distintos"] = len({t["style"] for t in styled})
    inv["placeholders_plantilla"] = len(re.findall(r"\{\{[^}]+\}\}", html))
    ext_css = [l.get("href") for l in soup.find_all("link", rel="stylesheet") if (l.get("href") or "").startswith("http")]
    ext_js = [s.get("src") for s in soup.find_all("script") if s.get("src")]
    inv["css_externo"] = ext_css
    inv["js_src"] = ext_js
    inv["render_cliente"] = bool(soup.find("x-dc"))
    inv["landmarks"] = {t: len(soup.find_all(t)) for t in ["header", "nav", "main", "footer", "address", "section"]}
    inv["tags_desbalanceados"] = bal.errors

    text = visible_text(soup)
    inv["texto_visible_chars"] = len(text)
    inv["texto_bracket_placeholders"] = re.findall(r"\[[^\]]{3,}\]", text)
    nt = norm(text)
    inv["terminos"] = {t: (norm(t) in nt) for t in TERMS}

    # Línea de base: PASS / WARN / FAIL
    chk = []

    def add(st, msg):
        chk.append((st, msg))

    add("PASS" if inv["lang"] else "FAIL", f"html lang = {inv['lang']}")
    add("PASS" if inv["viewport"] else "FAIL", "meta viewport " + ("presente" if inv["viewport"] else "AUSENTE"))
    if not inv["title"]:
        add("FAIL", "title ausente")
    else:
        add("PASS" if inv["title_len"] <= 60 else "WARN", f"title {inv['title_len']} car.: {inv['title']!r}")
    d = inv["meta_description_len"]
    add("PASS" if 120 <= d <= 160 else "FAIL", f"meta description {d} car." + ("" if d else " (ausente)"))
    add("PASS" if inv["canonical"] else "FAIL", f"canonical: {inv['canonical']}")
    add("PASS" if inv["og"] else "FAIL", f"og:* ({len(inv['og'])} etiquetas)")
    add("PASS" if inv["twitter"] else "WARN", f"twitter:* ({len(inv['twitter'])} etiquetas)")
    add("PASS" if inv["jsonld_blocks"] == 1 else "FAIL", f"JSON-LD: {inv['jsonld_blocks']} bloque(s)")
    add("PASS" if inv["h1_count"] == 1 else "FAIL", f"H1: {inv['h1_count']}")
    add("PASS" if not jumps else "FAIL", "jerarquía de encabezados " + ("sin saltos" if not jumps else "; ".join(jumps)))
    add("PASS" if not broken else "FAIL", "anclas internas rotas: " + (", ".join(broken) if broken else "ninguna"))
    add("PASS" if not bal.errors else "FAIL", "etiquetas balanceadas" if not bal.errors else "HTML mal anidado: " + " | ".join(bal.errors))
    add("PASS" if inv["landmarks"]["main"] == 1 else "WARN", f"landmark <main>: {inv['landmarks']['main']}")
    add("WARN" if inv["render_cliente"] else "PASS", "contenido renderizado por JS en el cliente (x-dc + react)" if inv["render_cliente"] else "HTML estático")
    add("WARN" if ext_css else "PASS", f"CSS externo: {ext_css}")
    add("WARN" if inv["style_attr_count"] else "PASS", f"style=\"\" en línea: {inv['style_attr_count']} ({inv['style_attr_distintos']} distintos)")
    add("FAIL" if inv["texto_bracket_placeholders"] else "PASS", f"placeholders [..] visibles: {inv['texto_bracket_placeholders']}")
    inv["checks"] = [{"estado": s, "detalle": m} for s, m in chk]

    if "--quiet" not in args:
        print(f"== {path}")
        for s, m in chk:
            print(f"[{s}] {m}")
        print("-- encabezados")
        for h in heads:
            print("  " + "  " * (h["nivel"] - 1) + f"h{h['nivel']}: {h['texto']}")
        print("-- términos objetivo visibles hoy")
        for t, v in inv["terminos"].items():
            print(f"  {'sí' if v else 'NO'}  {t}")
        print(f"-- enlaces: {len(links)}; svg decorativos {inv['svg_decorativos']}/{inv['svg_total']}; img {inv['img_total']}")
    if out_json:
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(inv, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
