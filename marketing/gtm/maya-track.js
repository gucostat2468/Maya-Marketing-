/*
 * Maya Protege: helper de rastreamento para o dev (window.mayaTrack).
 * Colar no site ANTES do snippet do GTM (logo depois do bloco de Consent Mode).
 * ES5, sem dependências.
 *
 * Uso:
 *   mayaTrack('page_view');
 *   mayaTrack('view_quiz_start');                                  // assistente virtual aberto/1a resposta
 *   mayaTrack('quiz_step', {step_number: 1, step_name: 'nome'});   // cada pergunta respondida
 *   mayaTrack('generate_lead', {lead_source: 'formulario'});       // SUCESSO do envio, nunca no clique
 *   mayaTrack('click_whatsapp');                                   // opcional: o GTM já captura o clique
 *
 * O que ele faz em todo push:
 * - utm_source, utm_medium, utm_campaign, utm_content, utm_term: lidos da URL (minúsculos, sem
 *   acento) e gravados no cookie first-party "maya_utm" + localStorage por 30 dias. Sem UTM na
 *   URL, recupera o que foi gravado. UTM nova na URL sobrescreve o conjunto inteiro.
 * - page_url (sem query string e sem #) e event_id (UUID v4 único).
 * - generate_lead com utm_campaign vazia recebe "organico_sem_utm".
 * - Bloqueia o mesmo evento 2x na mesma página (quiz_step: por step_number).
 * - Remove dados pessoais (nome, telefone, whatsapp, e-mail e valores com cara de e-mail ou
 *   telefone). Nada disso deve ir ao GA4 nem ao Meta.
 * Retorna o event_id do push, ou null se o evento foi bloqueado.
 */
(function (w, d) {
  var KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"];
  var COOKIE = "maya_utm";
  var DAYS = 30;
  var PII_KEYS = /^(nome|name|first_name|last_name|full_name|nome_completo|telefone|phone|tel|celular|whatsapp|email|e_mail|mail|cpf)$/i;
  var EMAIL = /[^\s@]+@[^\s@]+\.[^\s@]+/;
  var PHONE = /(\d[\s().-]*){10,}/;

  function clean(v) {
    v = String(v == null ? "" : v).replace(/^\s+|\s+$/g, "").toLowerCase();
    if (v.normalize) v = v.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    return v.slice(0, 150);
  }

  function fromUrl() {
    var out = {}, found = false, q = w.location.search.replace(/^\?/, "").split("&");
    for (var i = 0; i < q.length; i++) {
      var p = q[i].split("=");
      var k = "";
      try { k = decodeURIComponent(p[0] || "").toLowerCase(); } catch (e) {}
      if (KEYS.indexOf(k) !== -1 && p[1]) {
        var val = "";
        try { val = decodeURIComponent(p[1].replace(/\+/g, " ")); } catch (e2) { val = p[1]; }
        val = clean(val);
        if (val) { out[k] = val; found = true; }
      }
    }
    return found ? out : null;
  }

  function cookieDomain() {
    var h = w.location.hostname;
    if (h === "localhost" || /^[0-9.]+$/.test(h)) return "";
    return "; domain=" + h.replace(/^www\./, "");
  }

  function save(utm) {
    var exp = Date.now() + DAYS * 864e5;
    var raw = encodeURIComponent(JSON.stringify(utm));
    d.cookie = COOKIE + "=" + raw + "; expires=" + new Date(exp).toUTCString() + "; path=/" +
      cookieDomain() + "; SameSite=Lax" + (w.location.protocol === "https:" ? "; Secure" : "");
    try { w.localStorage.setItem(COOKIE, JSON.stringify({ exp: exp, utm: utm })); } catch (e) {}
  }

  function load() {
    var m = d.cookie.match(new RegExp("(?:^|; )" + COOKIE + "=([^;]*)"));
    if (m) { try { return JSON.parse(decodeURIComponent(m[1])); } catch (e) {} }
    try {
      var ls = JSON.parse(w.localStorage.getItem(COOKIE));
      if (ls && ls.exp > Date.now()) return ls.utm;
    } catch (e2) {}
    return {};
  }

  function utm() {
    var u = fromUrl();
    if (u) {
      for (var i = 0; i < KEYS.length; i++) if (!u[KEYS[i]]) u[KEYS[i]] = "";
      save(u);
      return u;
    }
    return load() || {};
  }

  function uuid() {
    var c = w.crypto || w.msCrypto, b = [];
    if (c && c.getRandomValues) {
      var a = new Uint8Array(16); c.getRandomValues(a);
      for (var i = 0; i < 16; i++) b.push(a[i]);
    } else {
      for (var j = 0; j < 16; j++) b.push(Math.floor(Math.random() * 256));
    }
    b[6] = (b[6] & 0x0f) | 0x40;
    b[8] = (b[8] & 0x3f) | 0x80;
    var h = "";
    for (var k = 0; k < 16; k++) {
      h += (b[k] + 0x100).toString(16).slice(1);
      if (k === 3 || k === 5 || k === 7 || k === 9) h += "-";
    }
    return h;
  }

  function isPii(key, val) {
    if (PII_KEYS.test(key)) return true;
    return typeof val === "string" && (EMAIL.test(val) || PHONE.test(val));
  }

  var sent = {};

  w.mayaTrack = function (evento, params) {
    evento = clean(evento).replace(/[^a-z0-9_]/g, "_");
    if (!evento) return null;
    params = params || {};

    var dedupe = w.location.pathname + "|" + evento +
      (evento === "quiz_step" ? "|" + params.step_number : "");
    if (sent[dedupe]) return null;
    sent[dedupe] = true;

    var u = utm();
    var push = { event: evento };
    for (var i = 0; i < KEYS.length; i++) push[KEYS[i]] = u[KEYS[i]] || "";
    if (evento === "generate_lead" && !push.utm_campaign) push.utm_campaign = "organico_sem_utm";

    for (var k in params) {
      if (!params.hasOwnProperty(k) || k === "event" || KEYS.indexOf(k) !== -1) continue;
      if (isPii(k, params[k])) continue;
      push[k] = typeof params[k] === "string" ? clean(params[k]) : params[k];
    }
    push.page_url = w.location.protocol + "//" + w.location.host + w.location.pathname;
    push.event_id = uuid();

    w.dataLayer = w.dataLayer || [];
    w.dataLayer.push(push);
    return push.event_id;
  };
})(window, document);
