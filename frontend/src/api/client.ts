import type {
  AuditEntry,
  BackupInfo,
  DashboardSummary,
  FilterOptions,
  Health,
  IntegrationInfo,
  ModuleInfo,
  SystemInfo,
} from "./types";

export const API_URL: string = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8765/api";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number | null,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new ApiError(
      "Não foi possível falar com o backend local. Verifique se ele está em execução.",
      null,
    );
  }
  if (!response.ok) {
    let detail = `Erro ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      /* resposta sem JSON: mantém a mensagem padrão */
    }
    throw new ApiError(detail, response.status);
  }
  return (await response.json()) as T;
}

export const api = {
  health: () => request<Health>("/health"),
  system: () => request<SystemInfo>("/system"),
  modules: () => request<ModuleInfo[]>("/modules"),
  integrations: () => request<IntegrationInfo[]>("/integrations"),
  dashboard: (params: URLSearchParams) =>
    request<DashboardSummary>(`/dashboard/summary?${params.toString()}`),
  filterOptions: () => request<FilterOptions>("/dashboard/filters"),
  backups: () => request<BackupInfo[]>("/backups"),
  createBackup: () => request<BackupInfo>("/backups", { method: "POST" }),
  restoreBackup: (name: string, confirmation: string) =>
    request<{ restored: string; safety_backup: string }>(
      `/backups/${encodeURIComponent(name)}/restore`,
      { method: "POST", body: JSON.stringify({ confirmation }) },
    ),
  audit: () => request<AuditEntry[]>("/audit?limit=20"),
};
