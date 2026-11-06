import { isoDate } from "./format";

export const PERIOD_PRESETS = [
  { value: "7", label: "Últimos 7 dias" },
  { value: "30", label: "Últimos 30 dias" },
  { value: "90", label: "Últimos 90 dias" },
  { value: "custom", label: "Personalizado" },
] as const;

/** Converte os parâmetros da URL em parâmetros da API (start/end sempre juntos). */
export function toApiParams(search: URLSearchParams, today = new Date()): URLSearchParams {
  const out = new URLSearchParams();
  const preset = search.get("periodo") ?? "30";
  if (preset === "custom") {
    const start = search.get("inicio");
    const end = search.get("fim");
    if (start && end) {
      out.set("start", start);
      out.set("end", end);
    }
  } else {
    const days = Number(preset) || 30;
    const start = new Date(today);
    start.setDate(start.getDate() - (days - 1));
    out.set("start", isoDate(start));
    out.set("end", isoDate(today));
  }
  for (const key of ["platform", "campaign"]) {
    const value = search.get(key);
    if (value) out.set(key, value);
  }
  return out;
}
