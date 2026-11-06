// Testa marketing/gtm/captura-origem.html num navegador real (Playwright), sem servidor.
// Rodar: node ferramentas/tests/gtm/teste_captura_origem.cjs
const fs = require("fs");
const path = require("path");
let chromium;
try { ({ chromium } = require("playwright")); } catch {
  ({ chromium } = require(require("child_process").execSync("npm root -g").toString().trim() + "/playwright"));
}
const snippet = fs.readFileSync(path.join(__dirname, "../../../marketing/gtm/captura-origem.html"), "utf8");
const page = `<!doctype html><html><body><form>
<input name="nome"><input type="hidden" name="utm_source"><input type="hidden" name="utm_campaign">
<input type="hidden" name="ft_utm_campaign"><input type="hidden" name="gclid"><input type="hidden" name="landing_page">
</form>${snippet}</body></html>`;
let falhas = 0;
const check = (ok, msg) => { console.log((ok ? "ok: " : "FALHOU: ") + msg); if (!ok) falhas++; };
(async () => {
  const browser = await chromium.launch();
  const p = await (await browser.newContext()).newPage();
  await p.route("http://site-teste.local/**", (r) => r.fulfill({ contentType: "text/html", body: page }));
  const v = (n) => p.$eval(`input[name="${n}"]`, (e) => e.value);
  await p.goto("http://site-teste.local/plano?utm_source=instagram&utm_medium=paid_social&utm_campaign=leads-a&gclid=XYZ");
  check((await v("utm_source")) === "instagram", "preenche utm_source");
  check((await v("gclid")) === "XYZ", "preenche gclid");
  check((await v("landing_page")) === "/plano", "registra a página de entrada");
  const dl = await p.evaluate(() => window.dataLayer[0]);
  check(dl.event === "maya_origem_capturada" && dl.maya_lt_campaign === "leads-a", "evento no dataLayer");
  await p.goto("http://site-teste.local/plano?utm_source=google&utm_medium=cpc&utm_campaign=leads-b");
  check((await v("utm_campaign")) === "leads-b", "último toque atualizado");
  check((await v("ft_utm_campaign")) === "leads-a", "primeiro toque preservado");
  await p.goto("http://site-teste.local/plano");
  check((await v("utm_campaign")) === "leads-b", "visita direta mantém a origem");
  await browser.close();
  console.log(falhas ? `${falhas} falha(s)` : "todos os testes passaram");
  process.exitCode = falhas ? 1 : 0;
})();
