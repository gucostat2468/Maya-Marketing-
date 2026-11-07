#!/usr/bin/env node
/*
 * Radar de anúncios ativos na Biblioteca de Anúncios da Meta (Brasil), por palavra-chave.
 * Uso: node ferramentas/radar_anuncios.cjs "plano funerário" "assistência funeral" --max 60 --saida radar.json
 * Saída: JSON com anunciante, data de início, dias no ar, nº de anúncios com o mesmo criativo,
 * texto, domínio do link e chamada. Só lê dados públicos; não faz login nem interage.
 */
const fs = require("fs");
let chromium;
try { ({ chromium } = require("playwright")); } catch {
  ({ chromium } = require(require("child_process").execSync("npm root -g").toString().trim() + "/playwright"));
}
const args = process.argv.slice(2);
const termos = args.filter((a, i) => !a.startsWith("--") && !(args[i - 1] || "").startsWith("--"));
const opt = (n, d) => { const i = args.indexOf("--" + n); return i >= 0 ? args[i + 1] : d; };
const MAX = Number(opt("max", 60)), SAIDA = opt("saida", null);
if (!termos.length) { console.error('Uso: node ferramentas/radar_anuncios.cjs "termo" ["termo 2"] [--max 60] [--saida arquivo.json]'); process.exit(2); }

const MESES = { jan: 0, fev: 1, mar: 2, abr: 3, mai: 4, jun: 5, jul: 6, ago: 7, set: 8, out: 9, nov: 10, dez: 11 };
function parseData(s) {
  const m = s && s.match(/(\d{1,2}) de (\w{3})\w* de (\d{4})/);
  return m ? new Date(Date.UTC(+m[3], MESES[m[2].toLowerCase()], +m[1])) : null;
}

function parseCards(texto) {
  const partes = texto.split(/Identificação da biblioteca:\s*/).slice(1);
  return partes.map((p) => {
    const id = (p.match(/^(\d+)/) || [])[1];
    const inicio = (p.match(/Veiculação iniciada em ([^\n]+)/) || [])[1] || null;
    const variantes = Number((p.match(/(\d+) anúncios usam esse criativo/) || [])[1] || 1);
    const linhas = p.split("\n").map((l) => l.trim()).filter(Boolean);
    const iPat = linhas.findIndex((l) => l === "Patrocinado");
    const anunciante = iPat > 0 ? linhas[iPat - 1] : null;
    const corpo = iPat >= 0 ? linhas.slice(iPat + 1).filter((l) => !/^(Ativo|Ver detalhes|Ver resumo|See Details|Learn More|Saiba mais|Enviar mens|Fale conosco|Fale Conosco)/i.test(l)).slice(0, 8).join(" ") : "";
    const dominio = (p.match(/\b([A-Z0-9.-]+\.(?:COM|COM\.BR|BR|NET|ORG))\b/i) || [])[1] || null;
    const dt = parseData(inicio);
    const dias = dt ? Math.max(0, Math.round((Date.now() - dt) / 864e5)) : null;
    return { id, anunciante, inicio, dias_no_ar: dias, anuncios_mesmo_criativo: variantes, dominio: dominio && dominio.toLowerCase(), texto: corpo.slice(0, 600) };
  }).filter((c) => c.id);
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 1600 }, locale: "pt-BR" });
  const resultado = { coletado_em: new Date().toISOString(), fonte: "Biblioteca de Anúncios da Meta (Brasil, anúncios ativos)", termos: {} };
  for (const termo of termos) {
    const url = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=BR&media_type=all&search_type=keyword_unordered&q=" + encodeURIComponent(termo);
    try {
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
      await page.waitForTimeout(5000);
      const ok = page.getByRole("button", { name: "OK" }); if (await ok.count()) await ok.first().click().catch(() => {});
      let cards = [];
      for (let i = 0; i < 12 && cards.length < MAX; i++) {
        cards = parseCards(await page.evaluate(() => document.body.innerText));
        await page.mouse.wheel(0, 4000); await page.waitForTimeout(1500);
      }
      const total = (await page.evaluate(() => document.body.innerText)).match(/~?([\d.]+) resultados/);
      resultado.termos[termo] = { url, total_aproximado: total ? total[1] : null, anuncios: cards.slice(0, MAX) };
    } catch (e) {
      resultado.termos[termo] = { url, erro: e.message.slice(0, 200), anuncios: [] };
    }
  }
  await browser.close();
  const json = JSON.stringify(resultado, null, 2);
  if (SAIDA) fs.writeFileSync(SAIDA, json);
  for (const [t, r] of Object.entries(resultado.termos)) {
    console.log(`\n"${t}": ${r.anuncios.length} anúncios lidos (total aprox. ${r.total_aproximado || "?"})${r.erro ? " ERRO: " + r.erro : ""}`);
    const porAnunciante = {};
    for (const a of r.anuncios) { const k = a.anunciante || "?"; (porAnunciante[k] ||= []).push(a); }
    Object.entries(porAnunciante).sort((x, y) => y[1].length - x[1].length).slice(0, 15)
      .forEach(([k, v]) => console.log(`  ${k}: ${v.length} anúncio(s), mais antigo no ar há ${Math.max(...v.map((a) => a.dias_no_ar || 0))} dias`));
  }
})();
