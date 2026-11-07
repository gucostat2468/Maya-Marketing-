// Testa marketing/gtm/maya-track.js e marketing/gtm/var-utm-persistida.js num navegador real
// (Playwright), sem servidor. Rodar: node ferramentas/tests/gtm/teste_maya_track.cjs
const fs = require("fs");
const path = require("path");
let chromium;
try { ({ chromium } = require("playwright")); } catch {
  ({ chromium } = require(require("child_process").execSync("npm root -g").toString().trim() + "/playwright"));
}
const dir = path.join(__dirname, "../../../marketing/gtm/");
const helper = fs.readFileSync(dir + "maya-track.js", "utf8");
const variavel = fs.readFileSync(dir + "var-utm-persistida.js", "utf8");
const page = `<!doctype html><html><body><script>${helper}</script>
<script>window.varUtm = (${variavel});</script></body></html>`;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
let falhas = 0;
const check = (ok, msg) => { console.log((ok ? "ok: " : "FALHOU: ") + msg); if (!ok) falhas++; };
(async () => {
  const browser = await chromium.launch();
  const p = await (await browser.newContext()).newPage();
  await p.route("http://site-teste.local/**", (r) => r.fulfill({ contentType: "text/html", body: page }));
  const track = (ev, params) => p.evaluate(([e, pr]) => window.mayaTrack(e, pr), [ev, params]);
  const dl = () => p.evaluate(() => window.dataLayer || []);
  const todos = [];

  // 1. UTM da URL vira minúscula (sem acento) e é salva
  await p.goto("http://site-teste.local/plano?utm_source=Instagram&utm_medium=Paid_Social&utm_campaign=Leads_Proteção_SP&utm_content=Video_1");
  await track("page_view");
  let ev = (await dl())[0];
  check(ev.utm_source === "instagram" && ev.utm_medium === "paid_social", "UTM da URL em minúsculas");
  check(ev.utm_campaign === "leads_protecao_sp", "acento removido da campanha");
  check(ev.page_url === "http://site-teste.local/plano", "page_url sem query string");
  const cookie = (await p.context().cookies()).find((c) => c.name === "maya_utm");
  check(cookie && decodeURIComponent(cookie.value).includes("leads_protecao_sp"), "cookie maya_utm gravado");
  check(cookie && cookie.expires * 1000 - Date.now() > 29 * 864e5, "cookie dura ~30 dias");
  const ls = await p.evaluate(() => JSON.parse(localStorage.getItem("maya_utm")));
  check(ls && ls.utm.utm_campaign === "leads_protecao_sp", "cópia no localStorage");
  check((await p.evaluate(() => window.varUtm())).utm_campaign === "leads_protecao_sp", "variável GTM lê a URL");

  // 2. mesmo evento não entra 2x; event_id UUID único
  check((await track("page_view")) === null, "page_view repetido é bloqueado");
  await track("view_quiz_start");
  check((await track("view_quiz_start")) === null, "view_quiz_start repetido é bloqueado");
  // 3. quiz_step 1 e 2 entram, step 1 repetido não
  await track("quiz_step", { step_number: 1, step_name: "nome" });
  await track("quiz_step", { step_number: 2, step_name: "telefone" });
  check((await track("quiz_step", { step_number: 1, step_name: "nome" })) === null, "quiz_step 1 repetido é bloqueado");
  let evs = await dl();
  check(evs.filter((e) => e.event === "quiz_step").map((e) => e.step_number).join() === "1,2", "quiz_step 1 e 2 entraram");
  // 4. lead com PII: nada pessoal no push
  await track("generate_lead", { lead_source: "formulario", nome: "Maria Teste", telefone: "11 98888-7777",
    email: "maria@teste.com", whatsapp: "11988887777", observacao: "maria@teste.com" });
  check((await track("generate_lead", { lead_source: "formulario" })) === null, "generate_lead repetido é bloqueado");
  evs = await dl(); todos.push(...evs);
  const lead = evs.find((e) => e.event === "generate_lead");
  check(lead.lead_source === "formulario" && lead.utm_campaign === "leads_protecao_sp", "lead leva lead_source e campanha");

  // 5. visita sem UTM recupera do cookie (nova página = novo carregamento)
  await p.goto("http://site-teste.local/contato");
  await track("page_view");
  ev = (await dl())[0];
  check(ev.utm_source === "instagram" && ev.utm_campaign === "leads_protecao_sp", "sem UTM na URL recupera do cookie");
  check((await p.evaluate(() => window.varUtm())).utm_source === "instagram", "variável GTM recupera do cookie");
  todos.push(...(await dl()));

  // 6. UTM nova sobrescreve o conjunto inteiro
  await p.goto("http://site-teste.local/?utm_source=google&utm_medium=cpc&utm_campaign=Busca_Plano");
  await track("page_view");
  ev = (await dl())[0];
  check(ev.utm_source === "google" && ev.utm_campaign === "busca_plano" && ev.utm_content === "", "UTM nova sobrescreve (content antigo apagado)");
  await p.goto("http://site-teste.local/sobre");
  check((await p.evaluate(() => window.varUtm())).utm_campaign === "busca_plano", "variável GTM vê a UTM nova");
  todos.push(...(await dl()));

  // 7. generate_lead sem campanha recebe organico_sem_utm (contexto limpo, sem cookie)
  const p2 = await (await browser.newContext()).newPage();
  await p2.route("http://site-teste.local/**", (r) => r.fulfill({ contentType: "text/html", body: page }));
  await p2.goto("http://site-teste.local/");
  await p2.evaluate(() => window.mayaTrack("generate_lead", { lead_source: "assistente_virtual" }));
  const lead2 = (await p2.evaluate(() => window.dataLayer))[0];
  check(lead2.utm_campaign === "organico_sem_utm" && lead2.lead_source === "assistente_virtual", "lead sem campanha vira organico_sem_utm");
  check(JSON.stringify(await p2.evaluate(() => window.varUtm())) === "{}", "variável GTM sem UTM retorna objeto vazio");
  todos.push(lead2);

  // event_id: formato UUID v4 e único em todos os pushes
  const ids = todos.map((e) => e.event_id);
  check(ids.every((i) => UUID.test(i)), `event_id no formato UUID v4 (${ids.length} pushes)`);
  check(new Set(ids).size === ids.length, "event_id único em todos os pushes");
  // nenhum push com nome, telefone ou e-mail
  const texto = JSON.stringify(todos).toLowerCase();
  // step_name "nome"/"telefone" é o NOME da pergunta (permitido); o que não pode é o dado.
  const valores = ["maria", "98888", "988887777", "@teste.com"].filter((s) => texto.includes(s));
  const chaves = todos.flatMap(Object.keys).filter((k) => ["nome", "telefone", "email", "whatsapp"].includes(k));
  const achados = valores.concat(chaves);
  check(achados.length === 0, "nenhum push contém nome, telefone ou e-mail" + (achados.length ? " (achou: " + achados.join(", ") + ")" : ""));

  await browser.close();
  console.log(falhas ? `${falhas} falha(s)` : "todos os testes passaram");
  process.exitCode = falhas ? 1 : 0;
})();
