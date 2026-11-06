import { NavLink } from "react-router";

import type { ModuleInfo } from "../../api/types";
import { BrandMark } from "./BrandMark";
import { NAV_GROUPS } from "./nav";

/** Navegação lateral em verde profundo. O estado de cada módulo vem do backend. */
export function Sidebar({
  modules,
  onNavigate,
}: {
  modules: Map<string, ModuleInfo>;
  onNavigate?: () => void;
}) {
  return (
    <nav aria-label="Navegação principal" className="on-deep flex h-full flex-col bg-deep text-deep-ink">
      <div className="flex h-16 shrink-0 items-center px-5">
        <NavLink to="/" aria-label="Maya-marketing, ir para a Visão Geral" onClick={onNavigate}>
          <BrandMark />
        </NavLink>
      </div>
      <div className="flex-1 overflow-y-auto px-3 pb-6">
        {NAV_GROUPS.map((group) => (
          <div key={group.title} className="mt-5 first:mt-1">
            <p className="px-2 pb-1.5 text-xs text-deep-muted">{group.title}</p>
            <ul className="flex flex-col gap-0.5">
              {group.items.map((item) => {
                const mod = modules.get(item.key);
                const Icon = item.icon;
                return (
                  <li key={item.key}>
                    <NavLink
                      to={item.path}
                      end={item.path === "/"}
                      onClick={onNavigate}
                      className={({ isActive }) =>
                        `flex min-h-9 items-center gap-2.5 rounded-control px-2 py-1.5 text-sm transition-colors duration-[var(--dur-micro)] ${
                          isActive
                            ? "bg-deep-2 text-deep-ink"
                            : "text-deep-muted hover:bg-deep-2 hover:text-deep-ink"
                        }`
                      }
                    >
                      {({ isActive }) => (
                        <>
                          <Icon
                            size={16}
                            aria-hidden="true"
                            className={isActive ? "text-emerald" : ""}
                          />
                          <span className="min-w-0 flex-1 truncate">{item.label}</span>
                          {mod?.status === "planned" ? (
                            <span className="shrink-0 text-xs text-deep-muted">
                              fase {mod.phase}
                            </span>
                          ) : null}
                        </>
                      )}
                    </NavLink>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
      <p className="border-t border-deep-2 px-5 py-3 text-xs text-deep-muted">
        Dados locais neste computador
      </p>
    </nav>
  );
}
