#!/usr/bin/env node
/*
 * Grava uma peça HTML animada como vídeo MP4 (H.264) pronto para Instagram.
 * A página deve ter animações CSS e a função window.irPara(ms) que posiciona as animações.
 * Uso: node ferramentas/gravar_video.cjs <peca.html> <largura> <altura> <segundos> <saida.mp4> [fps]
 */
const path = require("path"), fs = require("fs"), os = require("os"), { execFileSync } = require("child_process");
let chromium;
try { ({ chromium } = require("playwright")); } catch {
  ({ chromium } = require(execFileSync("npm", ["root", "-g"]).toString().trim() + "/playwright"));
}
const [html, w, h, secs, out, fpsArg] = process.argv.slice(2);
if (!out) { console.error("Uso: node ferramentas/gravar_video.cjs <peca.html> <largura> <altura> <segundos> <saida.mp4> [fps]"); process.exit(2); }
const fps = Number(fpsArg || 30), frames = Math.round(Number(secs) * fps);
(async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "quadros-"));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.resolve(html));
  await page.evaluate(() => document.fonts && document.fonts.ready);
  if (!(await page.evaluate(() => typeof window.irPara === "function"))) { console.error("A peça não tem window.irPara(ms)."); process.exit(2); }
  for (let i = 0; i < frames; i++) {
    await page.evaluate((t) => window.irPara(t), (i * 1000) / fps);
    await page.screenshot({ path: path.join(dir, String(i).padStart(5, "0") + ".png") });
  }
  await browser.close();
  execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-framerate", String(fps), "-i", path.join(dir, "%05d.png"),
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "18", "-movflags", "+faststart", out]);
  fs.rmSync(dir, { recursive: true, force: true });
  console.log(`MP4 ${w}x${h}, ${secs}s, ${fps} fps salvo em ${out}`);
})();
