import { describe, expect, it } from "vitest";

import type { MetricResult } from "../api/types";
import { displayMetric, formatDate, formatValue } from "../lib/format";
import { toApiParams } from "../lib/period";

const base: MetricResult = {
  key: "cpl",
  status: "ok",
  value: 2,
  numerator: 100,
  denominator: 50,
  missing_inputs: [],
  reason: null,
};

describe("formatação", () => {
  it("formata moeda, percentual e razão em pt-BR", () => {
    expect(formatValue(1234.5, "currency")).toMatch(/R\$\s?1\.234,50/);
    expect(formatValue(0.256, "percent")).toMatch(/25,6\s?%/);
    expect(formatValue(3.2, "ratio")).toBe("3,2x");
  });

  it("nunca mostra zero quando o dado está ausente", () => {
    expect(displayMetric({ ...base, status: "no_data", value: null }, "currency")).toBe("Sem dados");
    expect(displayMetric({ ...base, status: "undefined", value: null }, "currency")).toBe(
      "Não calculável",
    );
    expect(displayMetric({ ...base, value: 0 }, "count")).toBe("0");
  });

  it("formata datas sem deslocar o dia por fuso horário", () => {
    expect(formatDate("2026-10-01")).toBe("01/10/2026");
  });
});

describe("período", () => {
  it("converte preset em intervalo inclusivo", () => {
    const params = toApiParams(new URLSearchParams("periodo=7"), new Date(2026, 10, 6));
    expect(params.get("start")).toBe("2026-10-31");
    expect(params.get("end")).toBe("2026-11-06");
  });

  it("período personalizado incompleto não envia datas", () => {
    const params = toApiParams(new URLSearchParams("periodo=custom&inicio=2026-01-01"));
    expect(params.has("start")).toBe(false);
  });

  it("mantém filtros de plataforma", () => {
    const params = toApiParams(new URLSearchParams("platform=meta_ads"));
    expect(params.get("platform")).toBe("meta_ads");
  });
});
