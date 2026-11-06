import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost";

const VARIANTS: Record<Variant, string> = {
  primary:
    "bg-accent text-accent-ink hover:bg-accent-strong active:bg-accent-strong border border-transparent",
  secondary:
    "bg-paper text-ink border border-field-edge hover:bg-paper-2 active:bg-paper-3",
  ghost: "bg-transparent text-ink-2 border border-transparent hover:bg-paper-2 active:bg-paper-3",
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  icon?: ReactNode;
  busy?: boolean;
}

/** Botão padrão. Uma única ação primária por tela; demais são secundárias. */
export function Button({
  variant = "secondary",
  icon,
  busy = false,
  children,
  className = "",
  disabled,
  type = "button",
  ...rest
}: ButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled || busy}
      aria-busy={busy || undefined}
      className={`inline-flex h-9 min-w-11 items-center justify-center gap-2 rounded-control px-3.5 text-sm font-medium transition-colors duration-[var(--dur-micro)] disabled:cursor-not-allowed disabled:opacity-55 ${VARIANTS[variant]} ${className}`}
      {...rest}
    >
      {icon}
      {children}
    </button>
  );
}
