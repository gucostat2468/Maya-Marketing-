import { Link } from "react-router";

import { PageHeader } from "../components/ui/PageHeader";

export function NotFound() {
  return (
    <div className="flex flex-col gap-4">
      <PageHeader title="Página não encontrada" description="O endereço não corresponde a nenhuma área da Maya-marketing." />
      <Link to="/" className="text-sm text-accent-strong">
        Voltar para a Visão Geral
      </Link>
    </div>
  );
}
