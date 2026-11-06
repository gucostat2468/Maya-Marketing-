import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ReactNode, useState } from "react";

import { api } from "../api/client";
import type { BackupInfo } from "../api/types";
import { Button } from "../components/ui/Button";
import { Field, Input } from "../components/ui/Field";
import { PageHeader, SectionHeading } from "../components/ui/PageHeader";
import { EmptyState, ErrorState, Skeleton } from "../components/ui/States";
import { StatusBadge } from "../components/ui/StatusBadge";
import { formatBytes, formatDateTime } from "../lib/format";

const AUDIT_LABELS: Record<string, string> = {
  "backup.created": "Backup criado",
  "backup.restored": "Backup restaurado",
};

function SystemPanel() {
  const system = useQuery({ queryKey: ["system"], queryFn: api.system });
  if (system.isPending) return <Skeleton className="h-48" />;
  if (system.isError) return <ErrorState message={system.error.message} onRetry={() => void system.refetch()} />;
  const s = system.data;
  const rows: [string, ReactNode][] = [
    ["Ambiente", s.workspace === "real" ? "Dados reais" : "Demonstração (banco separado)"],
    ["Versão", s.version],
    ["Banco de dados", <code key="db" className="break-all">{s.db_path}</code>],
    ["Tamanho do banco", formatBytes(s.db_size_bytes)],
    ["Versão do esquema", s.schema_revision],
    ["SQLite", `${s.sqlite_version}${s.fts5_available ? ", busca textual FTS5 disponível" : ", FTS5 indisponível"}`],
    ["Logs", <code key="log" className="break-all">{s.log_dir}</code>],
    ["Backups", <code key="bk" className="break-all">{s.backup_dir}</code>],
  ];
  return (
    <dl className="grid grid-cols-1 gap-x-6 gap-y-3 text-sm sm:grid-cols-[12rem_minmax(0,1fr)]">
      {rows.map(([label, value]) => (
        <div key={label} className="contents">
          <dt className="font-medium text-ink-2">{label}</dt>
          <dd className="m-0 text-ink">{value}</dd>
        </div>
      ))}
    </dl>
  );
}

function RestoreRow({ backup, onDone }: { backup: BackupInfo; onDone: (msg: string) => void }) {
  const [open, setOpen] = useState(false);
  const [confirmation, setConfirmation] = useState("");
  const queryClient = useQueryClient();
  const restore = useMutation({
    mutationFn: () => api.restoreBackup(backup.name, confirmation),
    onSuccess: (res) => {
      void queryClient.invalidateQueries();
      setOpen(false);
      setConfirmation("");
      onDone(`Backup restaurado. O estado anterior foi salvo em ${res.safety_backup}.`);
    },
  });
  const id = `confirm-${backup.name}`;

  return (
    <>
      <tr className="border-b border-rule">
        <td className="py-2.5 pr-4"><code className="break-all text-xs">{backup.name}</code></td>
        <td data-label="Criado em" className="num py-2.5 pr-4 text-ink-2">{formatDateTime(backup.created_at)}</td>
        <td data-label="Tamanho" className="num py-2.5 pr-4 text-ink-2">{formatBytes(backup.size_bytes)}</td>
        <td className="py-2.5 text-right">
          <Button variant="ghost" aria-expanded={open} aria-controls={`${id}-row`} onClick={() => setOpen((v) => !v)}>
            {open ? "Cancelar" : "Restaurar"}
          </Button>
        </td>
      </tr>
      {open ? (
        <tr id={`${id}-row`} className="border-b border-rule bg-warning-soft">
          <td colSpan={4} className="p-4">
            <form
              className="flex flex-col gap-2"
              onSubmit={(e) => {
                e.preventDefault();
                restore.mutate();
              }}
            >
              <p className="text-sm text-ink">
                Restaurar substitui todos os dados atuais por este backup. Antes disso, a Maya
                salva automaticamente um backup do estado atual.
              </p>
              <div className="flex flex-wrap items-start gap-3">
                <div className="w-64">
                  <Field label="Digite RESTAURAR para confirmar" htmlFor={id} hint={restore.isError ? <span className="text-error">{restore.error.message}</span> : undefined}>
                    <Input id={id} name="confirmation" autoComplete="off" value={confirmation} onChange={(e) => setConfirmation(e.target.value)} />
                  </Field>
                </div>
                <Button type="submit" className="mt-6" busy={restore.isPending} disabled={confirmation !== "RESTAURAR"}>
                  Confirmar restauração
                </Button>
              </div>
            </form>
          </td>
        </tr>
      ) : null}
    </>
  );
}

function BackupsPanel() {
  const queryClient = useQueryClient();
  const [notice, setNotice] = useState<string | null>(null);
  const backups = useQuery({ queryKey: ["backups"], queryFn: api.backups });
  const create = useMutation({
    mutationFn: api.createBackup,
    onSuccess: (b) => {
      setNotice(`Backup ${b.name} criado.`);
      void queryClient.invalidateQueries({ queryKey: ["backups"] });
      void queryClient.invalidateQueries({ queryKey: ["audit"] });
    },
  });

  return (
    <section className="flex flex-col gap-4" aria-labelledby="backups-title">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="backups-title" className="text-lg text-ink">Backups</h2>
        <Button variant="primary" busy={create.isPending} onClick={() => create.mutate()}>
          Criar backup agora
        </Button>
      </div>
      <p className="max-w-[70ch] text-sm text-muted">
        Cópia consistente do banco, feita pela API de backup do SQLite. Os 30 mais recentes são
        mantidos. Para proteção extra, copie a pasta de backups para um disco externo ou nuvem
        pessoal.
      </p>
      <div aria-live="polite" className="text-sm">
        {notice ? <p className="text-success">{notice}</p> : null}
        {create.isError ? <p className="text-error">{create.error.message}</p> : null}
      </div>
      {backups.isPending ? (
        <Skeleton className="h-24" />
      ) : backups.isError ? (
        <ErrorState message={backups.error.message} onRetry={() => void backups.refetch()} />
      ) : backups.data.length === 0 ? (
        <EmptyState title="Nenhum backup ainda">Crie o primeiro backup antes de importar dados.</EmptyState>
      ) : (
        <div className="overflow-x-auto">
          <table className="table-stack w-full border-collapse text-sm sm:min-w-[36rem]">
            <thead>
              <tr className="border-b border-rule-strong text-left text-ink-2">
                <th scope="col" className="whitespace-nowrap py-2 pr-4 font-medium">Arquivo</th>
                <th scope="col" className="whitespace-nowrap py-2 pr-4 font-medium">Criado em</th>
                <th scope="col" className="whitespace-nowrap py-2 pr-4 font-medium">Tamanho</th>
                <th scope="col" className="py-2 text-right font-medium">
                  <span className="visually-hidden">Ações</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {backups.data.map((b) => (
                <RestoreRow key={b.name} backup={b} onDone={setNotice} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function AuditPanel() {
  const audit = useQuery({ queryKey: ["audit"], queryFn: api.audit });
  return (
    <section className="flex flex-col gap-3">
      <SectionHeading title="Registro de auditoria" aside="Últimas 20 ações" />
      {audit.isPending ? (
        <Skeleton className="h-20" />
      ) : audit.isError ? (
        <ErrorState message={audit.error.message} onRetry={() => void audit.refetch()} />
      ) : audit.data.length === 0 ? (
        <p className="text-sm text-muted">Nenhuma ação registrada ainda.</p>
      ) : (
        <ul className="flex flex-col divide-y divide-rule border-y border-rule text-sm">
          {audit.data.map((a) => (
            <li key={a.id} className="flex flex-wrap items-baseline justify-between gap-2 py-2">
              <span className="text-ink">{AUDIT_LABELS[a.action] ?? a.action}</span>
              <span className="num text-xs text-muted">{formatDateTime(a.at)}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export function Settings() {
  return (
    <div className="flex flex-col gap-10">
      <PageHeader
        title="Configurações"
        description="Onde ficam os dados, a saúde do banco local, os backups e o registro de ações."
        actions={<StatusBadge tone="accent">Executando localmente</StatusBadge>}
      />
      <section className="flex flex-col gap-4">
        <SectionHeading title="Ambiente local" />
        <SystemPanel />
      </section>
      <BackupsPanel />
      <AuditPanel />
    </div>
  );
}
