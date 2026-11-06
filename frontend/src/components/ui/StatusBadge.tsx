import type { ReactNode } from "react";

export type Tone = "neutral" | "accent" | "warning" | "error" | "success";

const TONES: Record<Tone, string> = {
  neutral: "bg-paper-2 text-ink-2 border-rule",
  accent: "bg-accent-soft text-accent-strong border-transparent",
  warning: "bg-warning-soft text-warning border-transparent",
  error: "bg-error-soft text-error border-transparent",
  success: "bg-accent-soft text-success border-transparent",
};

/** Rótulo de estado em texto (sem bolinhas decorativas). */
export function StatusBadge({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span
      className={`inline-flex items-center whitespace-nowrap rounded-pill border px-2 py-0.5 text-xs font-medium ${TONES[tone]}`}
    >
      {children}
    </span>
  );
}
