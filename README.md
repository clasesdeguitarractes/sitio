# Clases de Guitarra en Corrientes

Sitio estático (HTML + CSS, sin JavaScript). Se publica en Vercel desde GitHub.

## Estructura

```
src/                 lo que se publica
  index.html         página única, con title, description, Open Graph y JSON-LD
  404.html           página de error
  styles.css         estilos (clases; no hay style="" en línea)
  fonts/             Archivo y Archivo Black (OFL), alojadas acá
  robots.txt, sitemap.xml
build.mjs            copia src/ a dist/ y pone el dominio real en canonical, og:url, JSON-LD, robots y sitemap
vercel.json          comando de build, carpeta de salida y cabeceras de seguridad (CSP estricta)
design/Main.dc.html  diseño original (referencia; no se publica)
informes/            propuesta, informe y capturas del trabajo SEO
tools/               scripts de verificación (Python)
```

## Dominio

`build.mjs` toma el dominio de `SITE_URL` o, en Vercel, de `VERCEL_PROJECT_PRODUCTION_URL`
(el dominio propio si lo agregaste; si no, el `.vercel.app`). No hay que editar nada a mano.
Si agregás un dominio propio después, hacé un nuevo deploy (Redeploy) para que el canonical
y el sitemap lo usen.

## Publicar

1. Subí el repo a GitHub.
2. En Vercel: Add New → Project → importá el repo. Framework Preset: **Other**.
   El comando de build y la carpeta de salida ya vienen de `vercel.json`.
3. Verificá que esté activa la opción «Automatically expose System Environment Variables»
   (Settings → Environment Variables). Es la opción por defecto. Si el build falla pidiendo
   el dominio, definí `SITE_URL` ahí con `https://tu-dominio`.
4. Deploy.

## Probar en local

```
SITE_URL=http://localhost:8000 node build.mjs
python3 -m http.server 8000 -d dist
```

## Después de publicar

- `curl -I https://TU-DOMINIO/` → debe mostrar `Content-Security-Policy` y 200.
- `curl -I https://TU-DOMINIO/no-existe` → 404 con la página propia.
- Abrí `/robots.txt` y `/sitemap.xml`: las URLs tienen que ser las de tu dominio.
- Search Console: propiedad de dominio (registro TXT en el DNS), enviar `sitemap.xml`,
  inspeccionar la URL de la portada, y probar la portada en la Prueba de resultados enriquecidos.
- Ficha de Google: el nombre, la categoría, la URL y el teléfono tienen que coincidir con el sitio.
  El nombre visible en el sitio y en el JSON-LD es «Clases de Guitarra Corrientes»; si en la
  ficha usás otro, cambialo en `src/index.html` (JSON-LD `name` y bloque «Dónde estamos»).

## Licencias

Tipografías Archivo y Archivo Black: SIL Open Font License 1.1 (ver `src/fonts/`).
