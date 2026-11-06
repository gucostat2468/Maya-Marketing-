import type { Kpi } from "../../api/types";
import { displayMetric, formatValue } from "../../lib/format";

const CURRENCY_INPUTS = new Set(["spend", "acquisition_cost_total", "revenue"]);

function formatInput(key: string | undefined, value: number): string {
  return formatValue(value, key && CURRENCY_INPUTS.has(key) ? "currency" : "count");
}

const INPUT_LABELS: Record<string, string> = {
  spend: "investimento em mídia",
  acquisition_cost_total: "custo total de aquisição",
  impressions: "impressões",
  reach: "alcance",
  clicks: "cliques",
  engagements: "engajamento",
  followers_net: "crescimento líquido de seguidores",
  leads: "leads",
  qualified_leads: "leads qualificados",
  sales: "vendas",
  revenue: "receita atribuída",
};

function changeText(kpi: Kpi): string | null {
  const { change } = kpi;
  if (change.status !== "ok" || change.absolute === null) return null;
  if (change.relative === null) return "Período anterior igual a zero";
  const pct = new Intl.NumberFormat("pt-BR", {
    style: "percent",
    maximumFractionDigits: 1,
    signDisplay: "exceptZero",
  }).format(change.relative);
  return `${pct} vs. período anterior`;
}

/**
 * Indicador com rastreabilidade: o valor (ou a ausência dele) e, ao abrir,
 * a fórmula, o numerador, o denominador e o motivo quando não há número.
 */
export function KpiTile({ kpi }: { kpi: Kpi }) {
  const { current } = kpi;
  const hasValue = current.status === "ok";
  const delta = changeText(kpi);

  return (
    <article className="flex min-w-0 flex-col gap-2 rounded-card border border-rule bg-paper p-4">
      <h3 className="line-clamp-2 min-h-[2lh] text-sm font-medium text-ink-2">
        {kpi.label}
      </h3>
      <p
        className={`num text-xl leading-tight ${hasValue ? "text-ink" : "text-muted"}`}
        data-status={current.status}
      >
        {displayMetric(current, kpi.unit)}
      </p>
      <p className="min-h-[1lh] text-xs text-muted">{delta}</p>
      <details className="group border-t border-rule pt-2 text-xs text-ink-2">
        <summary className="cursor-pointer select-none rounded-control text-muted hover:text-ink">
          Como é calculado
        </summary>
        <dl className="mt-2 grid grid-cols-[auto_1fr] gap-x-3 gap-y-1">
          <dt className="font-medium">Fórmula</dt>
          <dd>{kpi.formula ?? "Soma direta dos dados da fonte"}</dd>
          {kpi.formula ? (
            <>
              <dt className="font-medium">Numerador</dt>
              <dd className="num">
                {current.numerator === null
                  ? "sem dados"
                  : formatInput(kpi.numerator_key, current.numerator)}
              </dd>
              <dt className="font-medium">Denominador</dt>
              <dd className="num">
                {current.denominator === null
                  ? "sem dados"
                  : formatInput(kpi.denominator_key, current.denominator)}
              </dd>
            </>
          ) : null}
          {current.reason ? (
            <>
              <dt className="font-medium">Situação</dt>
              <dd>{current.reason}</dd>
            </>
          ) : null}
          {current.missing_inputs.length > 0 ? (
            <>
              <dt className="font-medium">Falta</dt>
              <dd>{current.missing_inputs.map((k) => INPUT_LABELS[k] ?? k).join(", ")}</dd>
            </>
          ) : null}
        </dl>
        {kpi.caveat ? <p className="mt-2 text-warning">{kpi.caveat}</p> : null}
      </details>
    </article>
  );
}
