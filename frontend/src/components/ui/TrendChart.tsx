import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { EmptyState } from "./States";

export interface TrendPoint {
  date: string;
  value: number | null;
}

/**
 * Gráfico de evolução. Lacunas (null) aparecem como interrupção da linha,
 * nunca como queda a zero. Sem pontos, mostra o estado vazio.
 */
export function TrendChart({
  data,
  label,
  emptyTitle,
  emptyText,
}: {
  data: TrendPoint[];
  label: string;
  emptyTitle: string;
  emptyText: string;
}) {
  if (data.length === 0) {
    return <EmptyState title={emptyTitle}>{emptyText}</EmptyState>;
  }
  return (
    <figure className="h-64 w-full" aria-label={label}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="var(--color-rule)" vertical={false} />
          <XAxis dataKey="date" tick={{ fill: "var(--color-muted)", fontSize: 12 }} />
          <YAxis tick={{ fill: "var(--color-muted)", fontSize: 12 }} width={48} />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="value"
            name={label}
            stroke="var(--color-accent)"
            strokeWidth={2}
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </figure>
  );
}
