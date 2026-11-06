#!/usr/bin/env node
/*
 * Renderiza uma peça HTML em PNG no tamanho exato do formato.
 * Uso: node ferramentas/renderizar_peca.cjs entregas/x/peca.html 1080 1350 entregas/x/peca.png
 * Requer Playwright (já disponível no claude.ai/code). Em outra máquina: npm i -g playwright
 * e npx playwright install chromium.
 */
const path = require("path");
let chromium;
try {
  ({ chromium } = require("playwright"));
} catch {
  try {
    ({ chromium } = require(require("child_process").execSync("npm root -g").toString().trim() + "/playwright"));
  } catch {
    console.error("Playwright não encontrado. Instale com: npm i -g playwright");
    process.exit(2);
  }
}
const [html, w, h, out] = process.argv.slice(2);
if (!html || !w || !h || !out) {
  console.error("Uso: node ferramentas/renderizar_peca.cjs <peca.html> <largura> <altura> <saida.png>");
  process.exit(2);
}
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.resolve(html));
  await page.evaluate(() => document.fonts && document.fonts.ready);
  const overflow = await page.evaluate(() => ({
    x: document.documentElement.scrollWidth > innerWidth,
    y: document.documentElement.scrollHeight > innerHeight,
  }));
  await page.screenshot({ path: out, clip: { x: 0, y: 0, width: +w, height: +h } });
  await browser.close();
  console.log(`PNG ${w}x${h} salvo em ${out}`);
  if (overflow.x || overflow.y) {
    console.warn("ATENÇÃO: o conteúdo passou do tamanho da peça e foi cortado. Ajuste o layout.");
    process.exitCode = 1;
  }
})();
