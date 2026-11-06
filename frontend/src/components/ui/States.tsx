import type { ReactNode } from "react";

import { Button } from "./Button";

interface EmptyStateProps {
  title: string;
  children: ReactNode;
  action?: ReactNode;
  icon?: ReactNode;
}

/** Estado vazio: diz o que pertence aqui e qual ação preenche. */
export function EmptyState({ title, children, action, icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-start gap-3 rounded-card border border-dashed border-rule-strong bg-paper-2 p-6">
      {icon ? <div className="text-muted">{icon}</div> : null}
      <h3 className="text-base text-ink">{title}</h3>
      <div className="max-w-prose text-sm text-ink-2">{children}</div>
      {action}
    </div>
  );
}

/** Estado de erro: o que quebrou e o que fazer. */
export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div
      role="alert"
      className="flex flex-col items-start gap-3 rounded-card border border-transparent bg-error-soft p-5"
    >
      <h3 className="text-base text-error">Não foi possível carregar esta área</h3>
      <p className="text-sm text-ink-2">{message}</p>
      {onRetry ? <Button onClick={onRetry}>Tentar novamente</Button> : null}
    </div>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div aria-hidden="true" className={`skeleton ${className}`} />;
}
