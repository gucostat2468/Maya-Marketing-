import { useQuery } from "@tanstack/react-query";
import { Construction } from "lucide-react";

import { api } from "../api/client";
import { PageHeader } from "../components/ui/PageHeader";
import { EmptyState, ErrorState, Skeleton } from "../components/ui/States";
import { StatusBadge } from "../components/ui/StatusBadge";

/**
 * Página de um módulo ainda não implementado. Mostra o estado real (vindo do
 * backend) em vez de uma interface de aparência pronta sem função.
 */
export function PlannedModule({ moduleKey }: { moduleKey: string }) {
  const modules = useQuery({ queryKey: ["modules"], queryFn: api.modules, staleTime: Infinity });
  if (modules.isPending) return <Skeleton className="h-40" />;
  if (modules.isError) return <ErrorState message={modules.error.message} onRetry={() => void modules.refetch()} />;
  const mod = modules.data.find((m) => m.key === moduleKey);
  if (!mod) return <ErrorState message="Módulo desconhecido." />;

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={mod.label}
        description={mod.summary}
        actions={<StatusBadge tone="warning">Planejado para a fase {mod.phase}</StatusBadge>}
      />
      <EmptyState icon={<Construction size={22} aria-hidden="true" />} title="Este módulo ainda não foi construído">
        <p>
          Para não exibir uma tela com aparência de pronta e sem função real, esta área fica
          vazia até a implementação. Próxima entrega: {mod.next}
        </p>
      </EmptyState>
    </div>
  );
}
