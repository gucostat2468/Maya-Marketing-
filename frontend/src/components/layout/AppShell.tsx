import { useQuery } from "@tanstack/react-query";
import { Menu, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Outlet, useLocation } from "react-router";

import { api } from "../../api/client";
import { StatusBadge } from "../ui/StatusBadge";
import { Sidebar } from "./Sidebar";

function BackendStatus() {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    refetchInterval: 15_000,
    retry: false,
  });
  if (health.isPending) return <StatusBadge>Conectando ao backend</StatusBadge>;
  if (health.isError) return <StatusBadge tone="error">Backend local fora do ar</StatusBadge>;
  return health.data.workspace === "demo" ? (
    <StatusBadge tone="warning">Ambiente de demonstração</StatusBadge>
  ) : (
    <StatusBadge tone="accent">Dados reais</StatusBadge>
  );
}

function OfflineNotice() {
  const health = useQuery({ queryKey: ["health"], queryFn: api.health, retry: false });
  if (!health.isError) return null;
  return (
    <div role="alert" className="border-b border-rule bg-error-soft px-6 py-3 text-sm text-ink">
      O backend local não está respondendo. Abra um terminal na pasta do projeto e execute{" "}
      <code className="rounded-control bg-paper px-1.5 py-0.5">scripts\dev.ps1</code>. Nada é
      perdido: os dados ficam no banco local.
    </div>
  );
}

export function AppShell() {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const modules = useQuery({ queryKey: ["modules"], queryFn: api.modules, staleTime: Infinity });
  const moduleMap = useMemo(
    () => new Map((modules.data ?? []).map((m) => [m.key, m])),
    [modules.data],
  );

  useEffect(() => setMenuOpen(false), [location.pathname]);

  return (
    <div className="min-h-dvh lg:pl-[var(--sidebar-width)]">
      <aside className="fixed inset-y-0 left-0 hidden w-[var(--sidebar-width)] lg:block">
        <Sidebar modules={moduleMap} />
      </aside>

      {menuOpen ? (
        <div className="fixed inset-0 z-[var(--z-drawer)] lg:hidden">
          <button
            type="button"
            aria-label="Fechar menu"
            className="absolute inset-0 bg-ink/40"
            onClick={() => setMenuOpen(false)}
          />
          <div className="relative h-full w-[min(85vw,var(--sidebar-width))]">
            <Sidebar modules={moduleMap} onNavigate={() => setMenuOpen(false)} />
          </div>
        </div>
      ) : null}

      <div className="flex min-w-0 flex-col">
        <header className="sticky top-0 z-[var(--z-sticky)] flex h-14 items-center gap-3 border-b border-rule bg-paper/95 px-4 backdrop-blur lg:px-8">
          <button
            type="button"
            className="inline-flex size-11 items-center justify-center rounded-control text-ink-2 hover:bg-paper-2 lg:hidden"
            aria-label={menuOpen ? "Fechar menu" : "Abrir menu"}
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((v) => !v)}
          >
            {menuOpen ? <X size={20} aria-hidden="true" /> : <Menu size={20} aria-hidden="true" />}
          </button>
          <p className="text-sm text-muted lg:hidden">Maya-marketing</p>
          <div className="ml-auto flex items-center gap-2">
            <BackendStatus />
          </div>
        </header>
        <OfflineNotice />
        <main className="mx-auto w-full max-w-[var(--container)] px-4 py-8 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
