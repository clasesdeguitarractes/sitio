// Copia src/ a dist/ y reemplaza %%SITE_URL%% por el dominio real del sitio.
// Dominio: SITE_URL (si lo definís) o, en Vercel, VERCEL_PROJECT_PRODUCTION_URL
// (el dominio de producción del proyecto: el propio si lo agregás, o el .vercel.app).
// Si no hay ninguno, falla: es preferible a publicar un canonical equivocado.
import { cp, readFile, writeFile, rm } from "node:fs/promises";

const fromEnv =
  process.env.SITE_URL ||
  (process.env.VERCEL_PROJECT_PRODUCTION_URL
    ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
    : "");

if (!fromEnv) {
  console.error(
    "Falta el dominio. Definí SITE_URL (ej.: https://midominio.com) o activá " +
      "'Automatically expose System Environment Variables' en Vercel."
  );
  process.exit(1);
}

const site = fromEnv.replace(/\/+$/, "");
if (!/^https?:\/\/[^\s/?#]+$/.test(site)) {
  console.error(`SITE_URL inválida: ${site} (debe ser https://dominio, sin ruta)`);
  process.exit(1);
}

await rm("dist", { recursive: true, force: true });
await cp("src", "dist", { recursive: true });

for (const f of ["index.html", "robots.txt", "sitemap.xml"]) {
  const p = `dist/${f}`;
  const txt = (await readFile(p, "utf8")).replaceAll("%%SITE_URL%%", site);
  if (txt.includes("%%")) {
    console.error(`Quedó un marcador sin reemplazar en ${p}`);
    process.exit(1);
  }
  await writeFile(p, txt);
}

console.log(`Build listo en dist/ con SITE_URL=${site}`);
