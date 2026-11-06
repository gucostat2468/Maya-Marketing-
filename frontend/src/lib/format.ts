import type { MetricResult, Unit } from "../api/types";

const LOCALE = "pt-BR";
const currency = new Intl.NumberFormat(LOCALE, { style: "currency", currency: "BRL" });
const integer = new Intl.NumberFormat(LOCALE, { maximumFractionDigits: 0 });
const percent = new Intl.NumberFormat(LOCALE, { style: "percent", maximumFractionDigits: 1 });
const decimal = new Intl.NumberFormat(LOCALE, { maximumFractionDigits: 2 });

export function formatValue(value: number, unit: Unit): string {
  switch (unit) {
    case "currency":
      return currency.format(value);
    case "count":
      return integer.format(value);
    case "percent":
      return percent.format(value);
    case "ratio":
      return `${decimal.format(value)}x`;
  }
}

/** Texto exibido para um indicador. Ausente nunca vira "0". */
export function displayMetric(result: MetricResult, unit: Unit): string {
  if (result.status === "ok" && result.value !== null) return formatValue(result.value, unit);
  if (result.status === "undefined") return "Não calculável";
  return "Sem dados";
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${decimal.format(bytes / 1024)} KB`;
  return `${decimal.format(bytes / 1024 / 1024)} MB`;
}

export function formatDate(iso: string): string {
  // Datas "AAAA-MM-DD" são locais; não converter por fuso para não mudar o dia.
  const [y, m, d] = iso.slice(0, 10).split("-");
  return `${d}/${m}/${y}`;
}

export function formatDateTime(iso: string): string {
  return new Intl.DateTimeFormat(LOCALE, { dateStyle: "short", timeStyle: "short" }).format(
    new Date(iso),
  );
}

export function isoDate(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}
