import { useQuery } from "@tanstack/react-query";

import { api } from "../api/client";
import type { IntegrationInfo } from "../api/types";
import { PageHeader } from "../components/ui/PageHeader";
import { ErrorState, Skeleton } from "../components/ui/States";
import { StatusBadge, type Tone } from "../components/ui/StatusBadge";

const STATUS: Record<IntegrationInfo["status"], { label: string; tone: Tone }> = {
  planned: { label: "Planejada", tone: "neutral" },
  not_configured: { label: "Não configurada", tone: "neutral" },
  configured: { label: "Configurada, sem teste", tone: "warning" },
  connected: { label: "Conectada", tone: "success" },
  error: { label: "Com erro", tone: "error" },
};

const AUTH: Record<string, string> = {
  oauth2: "OAuth 2.0",
  csv: "Arquivo CSV",
  api_key: "Chave de API",
  none: "A definir",
};

export function Integrations() {
  const integrations = useQuery({ queryKey: ["integrations"], queryFn: api.integrations });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Integrações"
        description="Estado real de cada conector. Nenhuma integração aparece como conectada sem autenticação e teste de conexão bem-sucedidos."
      />
      {integrations.isPending ? (
        <div className="flex flex-col gap-2" aria-label="Carregando integrações">
          {Array.from({ length: 6 }, (_, i) => (
            <Skeleton key={i} className="h-12" />
          ))}
        </div>
      ) : integrations.isError ? (
        <ErrorState message={integrations.error.message} onRetry={() => void integrations.refetch()} />
      ) : (
        <div className="overflow-x-auto">
          <table className="table-stack w-full border-collapse text-sm sm:min-w-[44rem]">
            <thead>
              <tr className="border-b border-rule-strong text-left text-ink-2">
                <th scope="col" className="whitespace-nowrap py-2 pr-4 font-medium">Conector</th>
                <th scope="col" className="whitespace-nowrap py-2 pr-4 font-medium">Plataforma</th>
                <th scope="col" className="whitespace-nowrap py-2 pr-4 font-medium">Acesso</th>
                <th scope="col" className="whitespace-nowrap py-2 pr-4 font-medium">Fase</th>
                <th scope="col" className="whitespace-nowrap py-2 font-medium">Estado</th>
              </tr>
            </thead>
            <tbody>
              {integrations.data.map((item) => (
                <tr key={item.code} className="border-b border-rule align-top">
                  <td className="py-3 pr-4">
                    <p className="font-medium text-ink">{item.name}</p>
                    {item.notes ? <p className="mt-0.5 max-w-[60ch] text-xs text-muted">{item.notes}</p> : null}
                  </td>
                  <td data-label="Plataforma" className="py-3 pr-4 text-ink-2">{item.platform ?? "Diversas"}</td>
                  <td data-label="Acesso" className="py-3 pr-4 text-ink-2">{AUTH[item.auth_type] ?? item.auth_type}</td>
                  <td data-label="Fase" className="num py-3 pr-4 text-ink-2">{item.planned_phase}</td>
                  <td data-label="Estado" className="py-3">
                    <StatusBadge tone={STATUS[item.status].tone}>{STATUS[item.status].label}</StatusBadge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="max-w-[70ch] text-sm text-muted">
        Credenciais (tokens e chaves) serão guardadas no Gerenciador de Credenciais do Windows,
        nunca no banco de dados, no código ou nos logs.
      </p>
    </div>
  );
}
