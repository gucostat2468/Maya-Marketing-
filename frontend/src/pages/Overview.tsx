import { useQuery } from "@tanstack/react-query";
import { Database } from "lucide-react";
import { Link, useSearchParams } from "react-router";

import { api } from "../api/client";
import type { Kpi } from "../api/types";
import { Field, Input, Select } from "../components/ui/Field";
import { KpiTile } from "../components/ui/KpiTile";
import { PageHeader, SectionHeading } from "../components/ui/PageHeader";
import { EmptyState, ErrorState, Skeleton } from "../components/ui/States";
import { TrendChart } from "../components/ui/TrendChart";
import { formatDate } from "../lib/format";
import { PERIOD_PRESETS, toApiParams } from "../lib/period";

const GROUPS: { key: string; title: string; keys: string[] }[] = [
  { key: "invest", title: "Investimento e eficiência", keys: ["spend", "cpl", "cpql", "cpc"] },
  { key: "leads", title: "Leads", keys: ["leads", "qualified_leads", "click_to_lead_rate"] },
  { key: "sales", title: "Resultado comercial", keys: ["sales", "cpa", "revenue", "roas"] },
  {
    key: "reach",
    title: "Alcance e audiência",
    keys: ["reach", "impressions", "ctr", "engagements", "followers_net"],
  },
];

function Filters() {
  const [search, setSearch] = useSearchParams();
  const options = useQuery({ queryKey: ["filter-options"], queryFn: api.filterOptions });
  const preset = search.get("periodo") ?? "30";

  const update = (key: string, value: string) => {
    const next = new URLSearchParams(search);
    if (value) next.set(key, value);
    else next.delete(key);
    setSearch(next, { replace: true });
  };

  const noCampaigns = (options.data?.campaigns.length ?? 0) === 0;

  return (
    <form
      className="grid grid-cols-1 gap-x-4 sm:grid-cols-2 xl:grid-cols-4"
      aria-label="Filtros do painel"
      onSubmit={(e) => e.preventDefault()}
    >
      <Field label="Período" htmlFor="f-periodo">
        <Select id="f-periodo" name="periodo" value={preset} onChange={(e) => update("periodo", e.target.value)}>
          {PERIOD_PRESETS.map((p) => (
            <option key={p.value} value={p.value}>
              {p.label}
            </option>
          ))}
        </Select>
      </Field>
      {preset === "custom" ? (
        <div className="grid grid-cols-2 gap-x-3">
          <Field label="Início" htmlFor="f-inicio">
            <Input id="f-inicio" name="inicio" type="date" value={search.get("inicio") ?? ""} onChange={(e) => update("inicio", e.target.value)} />
          </Field>
          <Field label="Fim" htmlFor="f-fim">
            <Input id="f-fim" name="fim" type="date" value={search.get("fim") ?? ""} onChange={(e) => update("fim", e.target.value)} />
          </Field>
        </div>
      ) : null}
      <Field label="Plataforma" htmlFor="f-plataforma">
        <Select id="f-plataforma" name="platform" value={search.get("platform") ?? ""} onChange={(e) => update("platform", e.target.value)}>
          <option value="">Todas</option>
          {options.data?.platforms.map((p) => (
            <option key={p.value} value={p.value}>
              {p.label}
            </option>
          ))}
        </Select>
      </Field>
      <Field
        label="Campanha"
        htmlFor="f-campanha"
        hint={noCampaigns ? "Disponível após importar campanhas" : undefined}
      >
        <Select id="f-campanha" name="campaign" disabled={noCampaigns} value={search.get("campaign") ?? ""} onChange={(e) => update("campaign", e.target.value)}>
          <option value="">Todas</option>
          {options.data?.campaigns.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </Select>
      </Field>
    </form>
  );
}

function KpiSkeleton() {
  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(13rem,1fr))] gap-3" aria-label="Carregando indicadores">
      {Array.from({ length: 8 }, (_, i) => (
        <Skeleton key={i} className="h-36" />
      ))}
    </div>
  );
}

export function Overview() {
  const [search] = useSearchParams();
  const params = toApiParams(search);
  const customIncomplete = search.get("periodo") === "custom" && !params.get("start");
  const summary = useQuery({
    queryKey: ["dashboard", params.toString()],
    queryFn: () => api.dashboard(params),
    enabled: !customIncomplete,
  });

  const byKey = new Map<string, Kpi>((summary.data?.kpis ?? []).map((k) => [k.key, k]));
  const period = summary.data?.period;
  const previous = summary.data?.comparison_period;

  return (
    <div className="flex flex-col gap-8">
      <PageHeader
        title="Visão Geral"
        description="Investimento, leads, resultado comercial e audiência no mesmo painel. Cada número mostra de onde vem."
      />
      <Filters />

      {customIncomplete ? (
        <p className="text-sm text-muted">Escolha a data de início e de fim para ver o período.</p>
      ) : summary.isPending ? (
        <KpiSkeleton />
      ) : summary.isError ? (
        <ErrorState message={summary.error.message} onRetry={() => void summary.refetch()} />
      ) : (
        <>
          {period && previous ? (
            <p className="text-sm text-muted">
              {formatDate(period.start)} a {formatDate(period.end)} ({period.days} dias), comparado
              com {formatDate(previous.start)} a {formatDate(previous.end)}.
            </p>
          ) : null}

          {!summary.data.coverage.has_data ? (
            <EmptyState
              icon={<Database size={22} aria-hidden="true" />}
              title="Nenhum dado real conectado ainda"
              action={
                <Link
                  to="/integracoes"
                  className="inline-flex h-9 items-center rounded-control bg-accent px-3.5 text-sm font-medium text-accent-ink no-underline hover:bg-accent-strong"
                >
                  Ver integrações
                </Link>
              }
            >
              {summary.data.coverage.message} Enquanto isso, os indicadores aparecem como
              &ldquo;Sem dados&rdquo;, e nunca como zero.
            </EmptyState>
          ) : null}

          {GROUPS.map((group) => (
            <section key={group.key} className="flex flex-col gap-3" aria-labelledby={`g-${group.key}`}>
              <h2 id={`g-${group.key}`} className="text-lg text-ink">
                {group.title}
              </h2>
              <div className="grid grid-cols-[repeat(auto-fill,minmax(13rem,1fr))] gap-3">
                {group.keys.map((key) => {
                  const kpi = byKey.get(key);
                  return kpi ? <KpiTile key={key} kpi={kpi} /> : null;
                })}
              </div>
            </section>
          ))}

          <section className="flex flex-col gap-3">
            <SectionHeading title="Evolução diária" />
            <TrendChart
              data={[]}
              label="Investimento diário"
              emptyTitle="Sem série histórica"
              emptyText="A evolução diária de investimento e leads aparece aqui depois que os primeiros relatórios forem importados."
            />
          </section>
        </>
      )}
    </div>
  );
}
