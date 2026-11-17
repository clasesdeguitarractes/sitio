# SEO on-page — Propuesta APROBADA (2026-11-17)

Versión aprobada de la propuesta borrador (abajo, sin cambios), con las respuestas de Gonzalo:

| # | Pregunta | Respuesta | Qué se hizo |
|---|---|---|---|
| 1 | ¿index.html estático? | Sí | `src/index.html`; `Main.dc.html` pasa a `design/` como referencia |
| 2 | ¿Dominio final? | Lo asigna Vercel al deployar | `build.mjs` inyecta el dominio (SITE_URL o VERCEL_PROJECT_PRODUCTION_URL); no hay placeholders en producción |
| 3 | Ficha de Google | En proceso | Nombre provisorio «Clases de Guitarra Corrientes»; sin `sameAs` hasta tener la ficha |
| 4 | ¿379 487-0266 celular o fijo? | WhatsApp (celular) | `tel:` y `telephone` en formato `+54 9 379…` |
| 5 | ¿«Junín y Chaco» visible? | Sí | Se mantiene; sin `streetAddress`, `geo` ni `hasMap` en el marcado |
| 6 | ¿Quitar «Cómo empezar»? | Sí | Quitado del menú |
| 7 | ¿Términos y prioridad? | Confirmados | Copy de la sección 4.2 aplicado |
| 8 | ¿Algo más para afirmar? | No | No se agregó online, tipos de guitarra, edad mínima ni horarios |
| 9 | ¿CSS + fuentes propias + CSP estricta? | «Decidilo vos» | **Sí (opción B)**: 0 `style=""`, fuentes alojadas, CSP `style-src 'self'` |
| 10 | ¿`vercel.json` y 404? | «Decidilo vos» | **Sí**: cabeceras de seguridad, `404.html` con noindex |

Ajustes respecto del borrador: ninguno de contenido. Solo el dominio dinámico (punto 2) y que el logo
tiene área táctil de 44 px (padding + margen negativo, sin cambiar el alto del encabezado).

---

# SEO on-page — Clases de Guitarra en Corrientes · Propuesta borrador (Paso 1)

ID: `SEO-20261117` · Fecha: 2026-11-17 · Estado: **borrador, esperando tu OK** (no se tocó ningún archivo del sitio).
Archivo analizado: tu `Main.dc.html` vigente (el doc del Project es una versión vieja con placeholders `[Tu presentación…]`; conviene sincronizarlo después).

## 0. Resumen

- **El texto ya es bastante bueno**: el H1 tiene el término principal con la ciudad, hay un solo H1, la jerarquía no salta y el contenido es real. El problema no es el copy, es todo lo que lo rodea.
- **Lo que hoy impide que Google (y WhatsApp) lo entiendan bien**:
  1. Sin `meta description`, `canonical`, `og:*`, `twitter:*` ni JSON-LD. Solo hay `<title>`.
  2. El contenido lo dibuja JS en el navegador (`<x-dc>` + `react.js` + `support.js`). Google puede renderizarlo, pero WhatsApp/Telegram/Facebook **no ejecutan JS**: sin `og:*` en el HTML estático, el link compartido sale pelado, y tu canal principal de contacto es WhatsApp.
  3. Faltan en el `<head>` el `viewport` (si `support.js` no lo inyecta, el celular renderiza a 980 px) y las etiquetas de arriba.
  4. Errores de HTML: un `<div>` sin cerrar en `#info` y un enlace del menú a `#como-empezar` que no existe.
- **Propuesta**: publicar un `index.html` estático (misma apariencia), con 6 cambios de texto mínimos que suman 5 términos que hoy no están a la vista, más head completo y JSON-LD. Verificado en simulación: mismo hero, sin scroll horizontal a 375/768/1280, 0 pedidos externos.
- **Necesito tus respuestas a 10 preguntas** (sección 8, cada una con mi recomendación). Las 4 que más cambian lo que hago: #1 (estático), #2 (dominio), #3 (ficha de Google), #5 (dirección).

## 1. Estado de partida

- No hay repo todavía (subís a GitHub después). La regla «rama `seo-AAAAMMDD` y un commit» se aplica cuando armemos el repo en el Paso 2.
- No hay verificador de proyecto: armé uno (`scripts/inventory.py`, solo lectura) y esta es su **línea de base** sobre tu archivo:

| Estado | Chequeo |
|---|---|
| PASS | `lang="es"`; title 32 car.; 1 H1; jerarquía sin saltos |
| FAIL | sin `viewport`; sin `meta description`; sin `canonical`; sin `og:*`; sin JSON-LD |
| FAIL | ancla rota `#como-empezar` (nav) |
| FAIL | HTML mal anidado: `<div>` de la línea 128 (`#info`) nunca se cierra |
| WARN | sin `twitter:*`; sin landmark `<main>` |
| WARN | contenido renderizado por JS (`x-dc` + React) |
| WARN | CSS externo (Google Fonts) |
| WARN | 110 `style=""` en línea (58 distintos) |

Objetivo del Paso 3: 0 FAIL, sin WARN nuevos y `style=""` que no sube (o baja a 0 con la opción B de la pregunta 9).

## 2. Inventario de la página (generado desde el archivo)

- `<title>`: «Clases de Guitarra en Corrientes» (32 car.). Description, canonical, og, twitter, JSON-LD: **ninguno**. `robots.txt` y `sitemap.xml`: no existen en lo que me pasaste.
- Imágenes: 0 `<img>`; 1 SVG decorativo con `aria-hidden="true"` (correcto). No hay favicon ni imagen para compartir.
- Encabezados:

```
h1 Clases de guitarra en Corrientes
  h2 Elegí tu instrumento o tu camino
    h3 Guitarra · Bajo · Ukelele · Teoría musical · Composición musical · Composición de canciones
  h2 A tu ritmo, solo o en grupo
    h3 Clases individuales · Clases grupales · Todas las edades
  h2 Gonzalo Corrales
  h2 Reservá tu lugar
```

- Enlaces (10): `#inicio`, `#clases`, `#modalidades`, **`#como-empezar` (roto)**, `#contacto`, 3 × `wa.me/5493794870266`, 1 × `tel:+543794870266`. Textos descriptivos salvo «WhatsApp» del menú (aceptable).
- Servicios que figuran hoy: guitarra, bajo, ukelele, teoría musical, composición musical, composición de canciones; modalidades individual y grupal; todas las edades. Dato visible: barrio Camba Cuá, Corrientes Capital, «Junín y Chaco», teléfono 379 487-0266.
- Landmarks: `header`, `nav`, `footer`, `address`; **sin `<main>`**.

## 3. Mapa de términos

Prioridad **provisional** (la confirmás en la pregunta 7).

| # | Término objetivo | ¿Visible hoy? | Copy propuesto | Dónde | Por qué ahí |
|---|---|---|---|---|---|
| 1 | clases de guitarra en Corrientes | Sí (H1) | Sin cambio | H1, title, description | Ya está como oferta y con la ciudad |
| 2 | profesor de guitarra | No | Antetítulo «Profesor de guitarra» sobre el H2 «Gonzalo Corrales» | `#info` | Liga el término a la persona. Probé sumarlo al H2 y lo lleva de 1 a 3–4 líneas; el antetítulo no cambia el layout |
| 3 | clases de bajo | No (solo «Bajo») | H3 «Clases de bajo» | tarjeta 02 | Nombrar el servicio como oferta, no solo el instrumento |
| 4 | clases de ukelele | No (solo «Ukelele») | H3 «Clases de ukelele» | tarjeta 03 | Ídem |
| 5 | clases de música | No | H2 «Clases de música: elegí tu camino» | `#clases` | Término genérico de búsqueda; mantiene tu voz («elegí… camino») y las mismas 3 líneas |
| 6 | clases de guitarra (H3) | No como H3 (solo «Guitarra») | H3 «Clases de guitarra» | tarjeta 01 | Coherencia con las otras dos |
| 7 | teoría musical · composición musical · composición de canciones | Sí (H3) | Sin cambio (hero suma «musical» a «composición») | tarjetas 04–06, hero | Ya están |
| 8 | clases individuales · clases grupales | Sí (H3 y chips) | Sin cambio | `#modalidades` | Ya están. Dejo el H2 «A tu ritmo, solo o en grupo»: repetirlas en el H2 sería redundante |
| 9 | niños | No (dice «chicos») | Párrafo: «Clases para niños, adolescentes y adultos. Nunca es temprano ni tarde para empezar a tocar.» | `#modalidades`, 3.ª tarjeta | «Niños» es lo que se busca; el H3 «Todas las edades» queda igual |
| 10 | Corrientes Capital · barrio Camba Cuá | Sí | Sin cambio | eyebrow del hero, dirección | Intención local cubierta |
| 11 | Gonzalo Corrales | Sí | Sin cambio | `#info` | — |

No agrego «online», «acústica/eléctrica/criolla», «para principiantes», precios ni horarios: no están a la vista y no me los confirmaste (pregunta 8).

## 4. Antes → después

### 4.1 `<head>`

| Elemento | Antes | Después |
|---|---|---|
| `<meta charset>` | sí | igual |
| `<meta viewport>` | **no** | `width=device-width, initial-scale=1` |
| `<title>` | Clases de Guitarra en Corrientes (32) | **Clases de Guitarra, Bajo y Ukelele en Corrientes** (48). Alternativa: `Clases de Guitarra en Corrientes \| Gonzalo Corrales` (51) |
| `meta description` | no | **Clases de guitarra, bajo, ukelele, teoría y composición musical en Corrientes Capital, barrio Camba Cuá. Individuales o grupales, para todas las edades.** (152) |
| `canonical` | no | `https://DOMINIO/` |
| `og:type / locale / site_name` | no | `website` / `es_AR` / `Clases de Guitarra Corrientes` |
| `og:title` / `og:description` / `og:url` | no | = title / = description / = canonical |
| `og:image` | no | **no se agrega** (no hay imagen; regla 2). Ver observación 6 |
| `twitter:card / title / description` | no | `summary` / = title / = description |
| JSON-LD | no | bloque único (4.3) |
| Fuentes | Google Fonts (externo) | self-host (pregunta 9) |

### 4.2 Texto visible (todo lo demás queda idéntico)

| Dónde | Antes | Después |
|---|---|---|
| Menú | …Modalidades · **Cómo empezar** · Contacto… | quitar «Cómo empezar» (ancla inexistente; pregunta 6) |
| Hero, párrafo | Guitarra, bajo, ukelele, teoría y composición. Para todas… | Guitarra, bajo, ukelele, teoría y composición **musical**. Para todas… |
| `#clases` H2 | Elegí tu instrumento o tu camino | **Clases de música: elegí tu camino** |
| H3 tarjetas 01–03 | Guitarra · Bajo · Ukelele | **Clases de guitarra · Clases de bajo · Clases de ukelele** (con `&nbsp;` entre «de» y el sustantivo) |
| H3 tarjetas 04–06 | — | sin cambio |
| `#modalidades` 3.ª tarjeta, párrafo | Chicos, adolescentes y adultos. … | **Clases para niños, adolescentes y adultos.** … |
| `#info` antetítulo | «Clases a cargo de␣» (con espacio sobrante) | **Profesor de guitarra** |
| Bloque de contacto | línea grande «Barrio Camba Cuá» / «Corrientes Capital, Argentina» | línea grande **«Clases de Guitarra Corrientes»** (nombre idéntico a la ficha; a confirmar, pregunta 3) / «**Barrio Camba Cuá, Corrientes Capital, Argentina**» |
| Estructura | secciones sueltas, `<div>` sin cerrar | secciones dentro de `<main>`; `<div>` de `#info` cerrado |
| Enlaces, footer, WhatsApp, teléfono | — | sin cambio (salvo pregunta 4) |

### 4.3 JSON-LD completo (un bloque, parseable; `DOMINIO` y `name` a confirmar)

```json
{
  "@context": "https://schema.org",
  "@type": ["LocalBusiness", "EducationalOrganization"],
  "@id": "https://DOMINIO/#negocio",
  "name": "Clases de Guitarra Corrientes",
  "url": "https://DOMINIO/",
  "description": "Clases de guitarra, bajo, ukelele, teoría y composición musical en Corrientes Capital, barrio Camba Cuá. Individuales o grupales, para todas las edades.",
  "telephone": "+5493794870266",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Corrientes",
    "addressRegion": "Corrientes",
    "addressCountry": "AR"
  },
  "areaServed": { "@type": "City", "name": "Corrientes" },
  "founder": {
    "@type": "Person",
    "name": "Gonzalo Corrales",
    "jobTitle": "Profesor de guitarra"
  },
  "knowsAbout": [
    "Guitarra",
    "Bajo",
    "Ukelele",
    "Teoría musical",
    "Composición musical",
    "Composición de canciones"
  ],
  "keywords": "clases de guitarra, clases de bajo, clases de ukelele, teoría musical, composición musical, composición de canciones, clases individuales, clases grupales, Corrientes",
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "Clases",
    "itemListElement": [
      { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Clases de guitarra" } },
      { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Clases de bajo" } },
      { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Clases de ukelele" } },
      { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Teoría musical" } },
      { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Composición musical" } },
      { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Composición de canciones" } },
      { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Clases individuales" } },
      { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Clases grupales" } }
    ]
  }
}
```

Decisiones de este bloque:
- **Tipo `["LocalBusiness","EducationalOrganization"]`**: schema.org no tiene un subtipo de `LocalBusiness` para escuelas de música; `EducationalOrganization` es un tipo aparte, y tipar con los dos es válido. Si preferís lo del prompt original, `ProfessionalService`. Lo validamos con el Validador de schema.org y la Prueba de resultados enriquecidos (te toca a vos, está en tu lista «Después»).
- `telephone` está porque el teléfono es visible en esta página. Lo dejé en formato internacional de celular (`+54 9 …`, igual que el `wa.me`); depende de la pregunta 4.
- **Omitidos a propósito**: `image`/`logo` (no hay imagen), `email` (no hay uno visible), `sameAs` (no me diste perfiles reales todavía), `geo`, `hasMap`, calle, `openingHours`, `priceRange`, `aggregateRating`, `review`.
- **Sin `Course`, sin `FAQPage`**: Google retiró Course Info en junio de 2025 y los resultados enriquecidos de FAQ dejaron de mostrarse el 7 de mayo de 2026. No sumarían nada visible.
- Verificado: el JSON parsea; la `description` es idéntica a la meta; **cada término** de `knowsAbout`, `keywords` y `hasOfferCatalog` (y `jobTitle`, `areaServed`, `name`) tiene texto visible que lo respalda en la versión simulada (27 de 27).

### 4.4 Archivos nuevos que crearía en el Paso 2 (propuesta)

```
index.html        estático, head completo, sin React ni support.js
404.html          «No encontramos esa página» + enlace al inicio, noindex
styles.css?v=20261117   (opción B) clases en lugar de style=""
fonts/            Archivo 400/500/600/700 + Archivo Black, woff2 latin
robots.txt        User-agent: * / Allow: / / Sitemap: https://DOMINIO/sitemap.xml
sitemap.xml       solo https://DOMINIO/ (sin lastmod: no lo vamos a mantener)
vercel.json       cabeceras (abajo)
Main.dc.html      sin tocar (fuente de diseño)
```

`vercel.json`, solo cabeceras, propuesta (opción B, CSP estricta): `Content-Security-Policy: default-src 'none'; style-src 'self'; font-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`, `X-Frame-Options: DENY`. Con la opción A el único cambio es `style-src 'self' 'unsafe-inline'`.

### 4.5 Señales técnicas de Vercel (verificar después de publicar, no se publica desde acá)

- HTTPS: Vercel redirige http→https y `www`→raíz con **308** (permanente; Google lo trata como 301). El `www`→raíz se configura en el panel, sección Domains. Un detalle: `http://www…` puede hacer dos saltos.
- HSTS: Vercel manda `max-age=63072000` (2 años) por defecto en dominios propios. El «escalonado 300 → 86400 → 31536000» del prompt no aplica salvo que lo sobrescribas en `vercel.json`; para un dominio nuevo solo-HTTPS no hace falta.
- La purga de CDN es automática en cada deploy de Vercel. El paso «apagar recompresión de imágenes» no aplica (no hay imágenes).
- `*.vercel.app` de producción es indexable: el `canonical` absoluto al dominio propio evita duplicados.
- Verificaciones para tu simulacro: `curl -I` a las 4 variantes (http/https × www/raíz), a una URL inexistente (debe dar 404 real) y a `/robots.txt` y `/sitemap.xml`.

## 5. Negocio local: bloque de contacto

Visible: nombre (idéntico a la ficha) + barrio + ciudad + país + teléfono (ya estaba). Dato de contacto solo donde está hoy (WhatsApp y teléfono en `#contacto`; WhatsApp en menú y hero). Sin calle ni mapa hasta que respondas la pregunta 5. La intención es **local**: ciudad en title, H1, description y bloque de contacto, que es lo que hay. Modalidad (presencial/online) **no se afirma** hasta la pregunta 8.

## 6. Simulación en el navegador (cambios en el DOM en memoria; Chrome, sin red, fuentes Archivo reales)

Capturas: `capturas/comparacion-375.png`, `-768.png`, `-1280.png` (izquierda antes, derecha simulada) y las individuales `antes-N.png` / `simulada-N.png`.

| Medida | 375 px antes → simulada | 768 px | 1280 px |
|---|---|---|---|
| Scroll horizontal | no → **no** | no → no | no → no |
| Alto del hero | 883 → 883 | 738 → 738 | 911 → 911 |
| Líneas del H1 / párrafo del hero | 4 / 3 → 4 / 3 | 4 / 2 → 4 / 2 | 4 / 2 → 4 / 2 |
| Líneas del H2 de `#clases` | 3 → 3 | 3 → 3 | 3 → 3 |
| Líneas del H2 de `#info` | 2 → 2 | 2 → 2 | 1 → 1 |
| Alto total de la página | 5936 → 6043 (+107) | 3937 → 3963 (+26) | 3744 → 3744 |
| Alto del bloque de dirección | 275 → 329 | 275 → 329 | 248 → 248 |
| Pedidos externos / errores de consola | 0 / 0 | 0 / 0 | 0 / 0 |

El único crecimiento es en celular: los H3 «Clases de guitarra/ukelele» pasan a 2 líneas y el nombre en el bloque de dirección ocupa 3.

Dos cosas que **corregí en mi propia propuesta** gracias a la simulación:
- `&nbsp;` entre todas las palabras de un H3 («Composición&nbsp;musical») desborda la tarjeta y mete scroll horizontal a 375 px (Archivo Black en mayúsculas es ancho). Por eso solo uso `&nbsp;` entre «de» y el sustantivo, y no toco los H3 de teoría y composición.
- «Gonzalo Corrales, profesor de guitarra» en el H2 lo llevaba de 1 a 3–4 líneas. Pasó al antetítulo.

Limitaciones: no tuve `support.js` ni `react.js`, así que el «antes» es tu HTML con `{{accent}}` = `#F5B83D` y el wrapper `<x-dc>` retirado; supongo que el runtime lo dibuja tal cual está escrito. Toque táctil: el enlace del logo mide 26 px de alto a 768/1280 (ya era así; sugiero `padding` vía clase en la opción B).

## 7. Observaciones fuera de la propuesta

1. **Viewport**: confirmá si `support.js` lo inyecta; si no, hoy el celular ve la página a 980 px.
2. **Teléfono**: `tel:+543794870266` (sin el 9) vs `wa.me/5493794870266` (con el 9). Si es celular, el formato internacional correcto es `+54 9 379…`; con el actual la llamada podría no conectar.
3. **Voz mezclada**: «Escribinos / coordinamos» (plural) vs la bio en primera persona («Empecé…», «te comparto»). Sugiero unificarla, pero es decisión tuya y no la toco.
4. **Ficha de Google**: nombre, categoría, URL y teléfono tienen que coincidir con el sitio. Para un negocio chico, usá el nombre con el que realmente te conocen (revisá las pautas de la ficha al crearla; los nombres con palabras clave de más pueden traer problemas).
5. **Doc del Project desactualizado** (tiene placeholders): al final lo sincronizo con la versión final.
6. **Sin imagen para compartir ni favicon**: los links por WhatsApp saldrán sin imagen. Un 1200×630 y un favicon son un buen siguiente paso, pero requieren assets nuevos (fuera de las reglas actuales).

## 8. Preguntas abiertas (máx. 10; marcada mi recomendación)

1. **¿Qué se publica en Vercel?** Recomiendo: `index.html` estático como fuente de verdad y `Main.dc.html` como referencia de diseño. Así los rastreadores y las vistas previas leen el texto sin JS. Alternativa: mantener el `.dc.html` con runtime (no recomendado por lo de `og:*` y WhatsApp).
2. **¿Dominio final?** Se usa en `canonical`, `og:url`, sitemap y JSON-LD. Recomiendo dominio propio sin `www` como canónico.
3. **Ficha de Google**: ¿existe? ¿Nombre exacto, categoría principal y perfiles reales (Instagram, YouTube, etc.) para `sameAs`? Recomiendo nombre «Clases de Guitarra Corrientes» solo si así te conocen; si no, «Gonzalo Corrales – Clases de guitarra». Categoría sugerida: la de escuela o profesor de música.
4. **¿El 379 487-0266 es celular o fijo?** Recomiendo ajustar el `tel:` al formato correcto y usar el mismo en `telephone`.
5. **«Junín y Chaco» visible**: ¿lo dejás? Recomiendo mostrar solo barrio y ciudad si es un domicilio particular (sin calle ni mapa en el marcado) y dar la referencia por WhatsApp al coordinar.
6. **Menú «Cómo empezar»** (ancla inexistente): recomiendo quitarlo. Si tenías una sección, pasame el texto real.
7. **Términos y prioridad**: ¿confirmás la lista de la sección 3? En particular «profesor de guitarra», «clases de música» y «niños». Orden que propongo: guitarra Corrientes → bajo/ukelele → profesor de guitarra → clases de música → teoría/composición.
8. **Datos que no afirmo salvo que me los confirmes**: clases online, tipo de guitarra (acústica, eléctrica, criolla), edad mínima, si son presenciales en tu estudio, duración y horarios. Recomiendo no agregar nada por ahora.
9. **Estilos, CSP y fuentes (opción B)**: pasar los 110 `style=""` a un `styles.css` con clases, alojar las fuentes y usar CSP estricta; yo verifico por diferencia de píxeles que el sitio se ve igual. Alternativa A (menos trabajo): dejar los estilos en línea con `style-src 'unsafe-inline'`. Recomiendo B.
10. **Alcance de `vercel.json` y 404**: ¿te sirve la propuesta de cabeceras (4.4) y una `404.html` con ese texto breve? Recomiendo sí.

## 9. Qué pasa con tu OK

Con tus respuestas actualizo esta propuesta y paso al Paso 2: rama `seo-20261117` y un commit con los archivos de 4.4, luego verificación (verificador, navegador a 360/375/768/1280, JSON-LD, capturas) e informe `SEO-20261117-seo.md` con el runbook de publicación **sin ejecutar**. No hago push ni deploy.

Fuentes consultadas: [Google Search Central — Simplifying search results (jun 2025)](https://developers.google.com/search/blog/2025/06/simplifying-search-results), [PPC Land — fin de FAQ rich results (may 2026)](https://ppc.land/google-kills-faq-rich-results-what-seos-saw-coming-since-2019/), [Vercel — HTTPS y HSTS](https://vercel.com/docs/cdn-security/encryption), [Vercel — comunidad: redirects 308 www/http](https://community.vercel.com/t/redirects-from-http-www-to-non-www-on-https/8374), [schema.org — jerarquía de tipos](https://webarchive.library.unt.edu/web/20210120170015mp_/http://schema.org/docs/full.html).
