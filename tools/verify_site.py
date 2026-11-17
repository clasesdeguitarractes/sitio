#!/usr/bin/env python3
"""Verificación del sitio construido (Paso 3). Solo escucha en 127.0.0.1 y bloquea cualquier otro host.

Uso (desde la raíz del repo): python3 -I tools/verify_site.py [carpeta_capturas_previas]
Requiere: node, playwright (python), Pillow, google-chrome.
Aplica las cabeceras de vercel.json para poder probar la CSP de verdad.
"""
import importlib.util
import json
import mimetypes
import re
import subprocess
import sys
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUT = ROOT / "informes"
CAP = OUT / "capturas"
PREV = Path(sys.argv[1]) if len(sys.argv) > 1 else CAP
PORT = 8777
SITE = "https://clases-guitarra.example"

spec = importlib.util.spec_from_file_location("inventory", ROOT / "tools/inventory.py")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)

# 1) Build real
b = subprocess.run(["node", "build.mjs"], cwd=ROOT, env={"SITE_URL": SITE, "PATH": "/usr/bin:/bin:/opt/node22/bin"},
                   capture_output=True, text=True)
print(b.stdout.strip() or b.stderr.strip())
assert b.returncode == 0

# 1b) El build debe fallar sin dominio
nb = subprocess.run(["node", "build.mjs"], cwd=ROOT, env={"PATH": "/usr/bin:/bin:/opt/node22/bin"},
                    capture_output=True, text=True)
print("build sin dominio falla (esperado):", nb.returncode != 0)

# 2) Inventario sobre lo construido
r = subprocess.run([sys.executable, "-I", str(ROOT / "tools/inventory.py"), str(DIST / "index.html"),
                    "--json", str(OUT / "inventario-despues.json")], capture_output=True, text=True)
print(r.stdout)

# 3) Servidor que imita vercel.json
CFG = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
CT = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".woff2": "font/woff2",
      ".txt": "text/plain; charset=utf-8", ".xml": "application/xml"}


class H(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _headers(self, path):
        for rule in CFG["headers"]:
            if re.fullmatch(rule["source"].replace("(.*)", ".*"), path):
                for h in rule["headers"]:
                    self.send_header(h["key"], h["value"])

    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/index.html":
            self.send_response(308); self.send_header("Location", "/"); self.end_headers(); return
        fp = DIST / (p.lstrip("/") or "index.html")
        if fp.is_dir():
            fp = fp / "index.html"
        status = 200
        if not fp.is_file():
            status, fp = 404, DIST / "404.html"
        data = fp.read_bytes()
        self.send_response(status)
        self.send_header("Content-Type", CT.get(fp.suffix, mimetypes.guess_type(str(fp))[0] or "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self._headers(p)
        self.end_headers()
        self.wfile.write(data)


srv = HTTPServer(("127.0.0.1", PORT), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}"

CHECK = """() => {
  const q = s => document.querySelector(s), qa = s => [...document.querySelectorAll(s)];
  const hs = qa('h1,h2,h3,h4,h5,h6').map(h => +h.tagName[1]);
  let jumps = 0; hs.forEach((l, i) => { if (i && l > hs[i-1] + 1) jumps++; });
  return {
    overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    h1: qa('h1').length, jumps,
    headingsOverflow: qa('h1,h2,h3').filter(e => e.scrollWidth > e.clientWidth + 1).map(e => e.textContent.trim()),
    tapLt44: qa('a').map(a => { const r = a.getBoundingClientRect(); return [a.textContent.trim().slice(0,30), Math.round(r.width), +r.height.toFixed(1)]; })
              .filter(x => x[2] < 43.5),
    fontsOk: document.fonts.check("16px 'Archivo Black'") && document.fonts.check("700 16px 'Archivo'"),
    inlineStyleAttrs: qa('[style]').length,
    scrollBehavior: getComputedStyle(document.documentElement).scrollBehavior,
    csp: window.__csp || [],
    text: document.body.innerText
  };
}"""
INIT = "window.__csp=[];document.addEventListener('securitypolicyviolation',e=>window.__csp.push(e.violatedDirective+' '+e.blockedURI));"

res, bad_hosts = {}, []
with sync_playwright() as p:
    br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])

    def ctx_for(w, **kw):
        c = br.new_context(viewport={"width": w, "height": 900}, **kw)
        c.route("**/*", lambda r: (bad_hosts.append(r.request.url), r.abort())
                if urlparse(r.request.url).hostname != "127.0.0.1" else r.continue_())
        c.add_init_script(INIT)
        return c

    for w in (320, 360, 375, 768, 1280):
        c = ctx_for(w)
        pg = c.new_page()
        errs, fails = [], []
        pg.on("console", lambda m: errs.append(m.text) if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("requestfailed", lambda r: fails.append(r.url))
        resp = pg.goto(BASE + "/")
        pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        d = pg.evaluate(CHECK)
        d["status"] = resp.status
        d["errores_consola"] = errs
        d["requests_fallidos"] = fails
        if w in (375, 768, 1280):
            pg.screenshot(path=str(CAP / f"despues-{w}.png"), full_page=True)
        res[w] = d
        c.close()

    # Sin JS y con reduced-motion
    c = ctx_for(1280, java_script_enabled=False)
    pg = c.new_page(); pg.goto(BASE + "/")
    nojs = {"h1": pg.inner_text("h1"), "jsonld": pg.locator('script[type="application/ld+json"]').count(),
            "canonical": pg.get_attribute('link[rel=canonical]', "href"),
            "og_url": pg.get_attribute('meta[property="og:url"]', "content")}
    c.close()
    c = ctx_for(1280, reduced_motion="reduce")
    pg = c.new_page(); pg.goto(BASE + "/")
    rm = pg.evaluate("getComputedStyle(document.documentElement).scrollBehavior")
    c.close()

    # 404 real
    c = ctx_for(375)
    pg = c.new_page(); r404 = pg.goto(BASE + "/no-existe")
    pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(200)
    nf = {"status": r404.status, "h1": pg.inner_text("h1"), "overflowX": pg.evaluate(
        "document.documentElement.scrollWidth > document.documentElement.clientWidth"),
          "csp": pg.evaluate("window.__csp")}
    pg.screenshot(path=str(CAP / "despues-404-375.png"), full_page=True)
    c.close()
    br.close()

# Cabeceras servidas
import urllib.request
hdr = {}
for path in ("/", "/robots.txt", "/sitemap.xml", "/fonts/archivo-latin-400-normal.woff2", "/styles.css?v=20261117"):
    with urllib.request.urlopen(BASE + path) as rr:
        hdr[path] = {k: v for k, v in rr.headers.items() if k.lower() in (
            "content-type", "content-security-policy", "x-content-type-options", "referrer-policy",
            "permissions-policy", "x-frame-options", "cache-control")}
        if path in ("/robots.txt", "/sitemap.xml"):
            hdr[path]["body"] = rr.read().decode()
try:
    urllib.request.urlopen(BASE + "/index.html")
except Exception as e:
    pass

# JSON-LD y términos
html = (DIST / "index.html").read_text(encoding="utf-8")
ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
vis = inv.norm(res[1280]["text"])
terms = [("knowsAbout", t) for t in ld["knowsAbout"]]
terms += [("keywords", t.strip()) for t in ld["keywords"].split(",")]
terms += [("hasOfferCatalog", o["itemOffered"]["name"]) for o in ld["hasOfferCatalog"]["itemListElement"]]
terms += [("jobTitle", ld["founder"]["jobTitle"]), ("founder", ld["founder"]["name"]), ("areaServed", ld["areaServed"]["name"]),
          ("name", ld["name"])]
# La description se respalda por afirmaciones (no como oración literal)
terms += [("description", t) for t in ("guitarra, bajo, ukelele, teoría y composición musical", "Corrientes Capital",
                                       "barrio Camba Cuá", "individuales", "grupales", "todas las edades")]
tabla = [(c, t, inv.norm(t) in vis) for c, t in terms]
dump = json.dumps(ld, ensure_ascii=False).lower()
no_prohibidos = all(k not in dump for k in ("pricerange", "aggregaterating", "\"review\"", "openinghours", "streetaddress", "\"geo\""))
meta_desc = re.search(r'<meta name="description" content="([^"]*)"', html).group(1)

# Diferencia de píxeles contra el diseño actual con los textos aprobados (simulada-N.png)
from PIL import Image, ImageChops
diffs = {}
for w in (375, 768, 1280):
    a = Image.open(PREV / f"simulada-{w}.png").convert("RGB")
    b_ = Image.open(CAP / f"despues-{w}.png").convert("RGB")
    entry = {"tam_simulada": a.size, "tam_despues": b_.size}
    if a.size == b_.size:
        d = ImageChops.difference(a, b_).convert("L")
        h = d.histogram()
        total = a.size[0] * a.size[1]
        entry["pixeles_distintos_pct"] = round(100 * (total - h[0]) / total, 4)
        entry["distintos_gt32_pct"] = round(100 * sum(h[33:]) / total, 4)
        entry["bbox"] = ImageChops.difference(a, b_).getbbox()
    diffs[w] = entry

out = {"por_ancho": {w: {k: v for k, v in d.items() if k != "text"} for w, d in res.items()},
       "sin_js": nojs, "reduced_motion_scroll": rm, "pagina_404": nf, "cabeceras": hdr,
       "requests_a_otros_hosts": bad_hosts, "jsonld_ok": True, "terminos": tabla,
       "sin_campos_prohibidos": no_prohibidos, "desc_len": len(meta_desc),
       "desc_igual_jsonld": meta_desc == ld["description"], "diferencia_pixeles": diffs}
(OUT / "verificacion.json").write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

print("=== NAVEGADOR (127.0.0.1, resto bloqueado) ===")
for w, d in res.items():
    print(f"{w:>5}px status={d['status']} overflowX={d['overflowX']} h1={d['h1']} saltos={d['jumps']} fuentes={d['fontsOk']} "
          f"style[]={d['inlineStyleAttrs']} CSP={d['csp']} consola={d['errores_consola']} fallidos={d['requests_fallidos']} "
          f"tap<44={d['tapLt44']} desborde_h={d['headingsOverflow']}")
print("requests a otros hosts:", bad_hosts)
print("sin JS:", nojs)
print("reduced-motion scroll-behavior:", rm, "| normal:", res[1280]["scrollBehavior"])
print("404:", nf)
print("cabeceras /:", json.dumps(hdr["/"], ensure_ascii=False)[:400])
print("robots:", hdr["/robots.txt"]["body"].strip().replace("\n", " | "))
print("sitemap loc:", re.findall(r"<loc>(.*?)</loc>", hdr["/sitemap.xml"]["body"]))
print("fonts cache:", hdr["/fonts/archivo-latin-400-normal.woff2"].get("Cache-Control"))
print("=== JSON-LD === parsea OK; desc meta len", len(meta_desc), "; igual a JSON-LD:", meta_desc == ld["description"],
      "; sin campos prohibidos:", no_prohibidos)
print("términos sin respaldo visible:", [(c, t) for c, t, ok in tabla if not ok], f"({len(tabla)} chequeados)")
print("=== PÍXELES vs diseño actual con textos aprobados ===")
for w, e in diffs.items():
    print(w, e)
srv.shutdown()
