import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { Kpi } from "../api/types";
import { KpiTile } from "../components/ui/KpiTile";

const kpi: Kpi = {
  key: "cpl",
  label: "Custo por lead (CPL)",
  unit: "currency",
  group: "eficiencia",
  formula: "investimento ÷ leads",
  numerator_key: "spend",
  denominator_key: "leads",
  caveat: "CPL baixo não significa leads bons.",
  higher_is_better: false,
  current: {
    key: "cpl",
    status: "no_data",
    value: null,
    numerator: null,
    denominator: null,
    missing_inputs: ["spend", "leads"],
    reason: "Sem dados de: investimento em mídia, leads gerados.",
  },
  previous: {
    key: "cpl",
    status: "no_data",
    value: null,
    numerator: null,
    denominator: null,
    missing_inputs: [],
    reason: null,
  },
  change: { status: "no_data", absolute: null, relative: null },
};

describe("KpiTile", () => {
  it("mostra 'Sem dados' e explica o que falta", () => {
    render(<KpiTile kpi={kpi} />);
    expect(screen.getByText("Sem dados")).toBeTruthy();
    expect(screen.getByText("investimento ÷ leads")).toBeTruthy();
    expect(screen.getByText("investimento em mídia, leads")).toBeTruthy();
    expect(screen.queryByText(/R\$\s?0/)).toBeNull();
  });

  it("mostra valor, insumos com unidade e variação quando há dados", () => {
    render(
      <KpiTile
        kpi={{
          ...kpi,
          current: { ...kpi.current, status: "ok", value: 2, numerator: 100, denominator: 50, missing_inputs: [], reason: null },
          change: { status: "ok", absolute: -0.5, relative: -0.2 },
        }}
      />,
    );
    expect(screen.getAllByText(/R\$\s?2,00/).length).toBe(1);
    expect(screen.getByText(/R\$\s?100,00/)).toBeTruthy();
    expect(screen.getByText("50")).toBeTruthy();
    expect(screen.getByText(/-20\s?% vs\. período anterior/)).toBeTruthy();
  });
});
