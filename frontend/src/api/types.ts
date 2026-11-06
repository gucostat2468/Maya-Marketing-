// Contratos da API local (espelham as respostas do backend FastAPI).

export type MetricStatus = "ok" | "no_data" | "undefined";
export type Unit = "currency" | "count" | "percent" | "ratio";

export interface MetricResult {
  key: string;
  status: MetricStatus;
  value: number | null;
  numerator: number | null;
  denominator: number | null;
  missing_inputs: string[];
  reason: string | null;
}

export interface Change {
  status: MetricStatus;
  absolute: number | null;
  relative: number | null;
}

export interface Kpi {
  key: string;
  label: string;
  unit: Unit;
  group: string;
  formula: string | null;
  numerator_key?: string;
  denominator_key?: string;
  caveat: string | null;
  higher_is_better: boolean | null;
  current: MetricResult;
  previous: MetricResult;
  change: Change;
}

export interface PeriodInfo {
  start: string;
  end: string;
  days: number;
}

export interface DashboardSummary {
  period: PeriodInfo;
  comparison_period: PeriodInfo;
  filters: Record<string, string>;
  coverage: {
    has_data: boolean;
    imports_completed: number;
    integrations_connected: number;
    message: string | null;
  };
  kpis: Kpi[];
}

export interface Option {
  value: string;
  label: string;
}

export interface FilterOptions {
  platforms: Option[];
  campaigns: Option[];
  ad_groups: Option[];
  ads: Option[];
  objectives: Option[];
  channels: Option[];
}

export type ModuleStatus = "available" | "partial" | "planned";

export interface ModuleInfo {
  key: string;
  label: string;
  path: string;
  phase: number;
  status: ModuleStatus;
  summary: string;
  next: string;
}

export interface IntegrationInfo {
  code: string;
  name: string;
  platform: string | null;
  auth_type: string;
  status: "not_configured" | "configured" | "connected" | "error" | "planned";
  planned_phase: number;
  supports_csv: boolean;
  last_sync_at: string | null;
  last_error: string | null;
  notes: string | null;
}

export interface SystemInfo {
  version: string;
  workspace: "real" | "demo";
  data_dir: string;
  db_path: string;
  db_size_bytes: number;
  log_dir: string;
  backup_dir: string;
  sqlite_version: string;
  fts5_available: boolean;
  schema_revision: string;
}

export interface BackupInfo {
  name: string;
  size_bytes: number;
  created_at: string;
}

export interface AuditEntry {
  id: number;
  at: string;
  actor: string;
  action: string;
  entity: string | null;
  entity_id: string | null;
  detail: Record<string, unknown> | null;
}

export interface Health {
  status: string;
  version: string;
  workspace: "real" | "demo";
}
