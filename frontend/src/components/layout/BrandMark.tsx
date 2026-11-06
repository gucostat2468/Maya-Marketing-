/**
 * Marca provisória (geométrica) da Maya-marketing.
 * Substitua pelo logotipo oficial da Maya Protege quando ele for cadastrado na Brand Memory.
 */
export function BrandMark() {
  return (
    <span className="flex items-center gap-2.5">
      <svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true">
        <rect width="32" height="32" rx="7" fill="var(--color-deep-2)" />
        <path
          d="M8 23V10l8 7 8-7v13"
          fill="none"
          stroke="var(--color-emerald)"
          strokeWidth="3"
          strokeLinejoin="round"
          strokeLinecap="round"
        />
      </svg>
      <span className="flex flex-col leading-tight">
        <span className="text-[15px] font-semibold text-deep-ink">Maya</span>
        <span className="text-xs text-deep-muted">marketing</span>
      </span>
    </span>
  );
}
