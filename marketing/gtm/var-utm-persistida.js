function () {
  /*
   * GTM > Variáveis > Nova > JavaScript personalizado. Nome: var - utm_persistida
   * Mesma lógica de marketing/gtm/maya-track.js (cookie maya_utm + localStorage, 30 dias):
   * UTM na URL -> minúscula, sem acento, grava e retorna (sobrescreve o conjunto inteiro);
   * sem UTM na URL -> retorna o que estava gravado; nada gravado -> retorna {} (objeto vazio).
   * Retorna um objeto {utm_source, utm_medium, utm_campaign, utm_content, utm_term}.
   * ES5 (o GTM não aceita let/const/arrow em JavaScript personalizado).
   */
  var KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"];
  var COOKIE = "maya_utm";
  var DAYS = 30;

  function clean(v) {
    v = String(v == null ? "" : v).replace(/^\s+|\s+$/g, "").toLowerCase();
    if (v.normalize) v = v.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    return v.slice(0, 150);
  }

  var found = false, u = {}, q = window.location.search.replace(/^\?/, "").split("&");
  for (var i = 0; i < q.length; i++) {
    var p = q[i].split("="), k = "", val = "";
    try { k = decodeURIComponent(p[0] || "").toLowerCase(); } catch (e) {}
    if (KEYS.indexOf(k) !== -1 && p[1]) {
      try { val = decodeURIComponent(p[1].replace(/\+/g, " ")); } catch (e2) { val = p[1]; }
      val = clean(val);
      if (val) { u[k] = val; found = true; }
    }
  }

  if (found) {
    for (var j = 0; j < KEYS.length; j++) if (!u[KEYS[j]]) u[KEYS[j]] = "";
    var exp = new Date().getTime() + DAYS * 864e5;
    var h = window.location.hostname;
    var dom = (h === "localhost" || /^[0-9.]+$/.test(h)) ? "" : "; domain=" + h.replace(/^www\./, "");
    document.cookie = COOKIE + "=" + encodeURIComponent(JSON.stringify(u)) + "; expires=" +
      new Date(exp).toUTCString() + "; path=/" + dom + "; SameSite=Lax" +
      (window.location.protocol === "https:" ? "; Secure" : "");
    try { window.localStorage.setItem(COOKIE, JSON.stringify({ exp: exp, utm: u })); } catch (e3) {}
    return u;
  }

  var m = document.cookie.match(new RegExp("(?:^|; )" + COOKIE + "=([^;]*)"));
  if (m) { try { return JSON.parse(decodeURIComponent(m[1])); } catch (e4) {} }
  try {
    var ls = JSON.parse(window.localStorage.getItem(COOKIE));
    if (ls && ls.exp > new Date().getTime()) return ls.utm;
  } catch (e5) {}
  return {};
}
