# Roadmap da Maya-marketing

Legenda: **Funcional** (implementado e testado) · **Parcial** (fundação funcional, recursos
a caminho) · **Planejado** (ainda não existe; a tela mostra isso claramente).

## Estado por módulo

| # | Módulo | Estado | Fase | O que já existe |
| --- | --- | --- | --- | --- |
| 01 | Visão Geral (Dashboard Executivo) | Parcial | 1 → 2 | 16 indicadores com fórmula e origem, filtro de período e plataforma pela URL, comparação com o período anterior, aviso de ausência de dados. Sem dados reais até a Fase 2 |
| 02 | Google Ads Intelligence | Planejado | 2 / 4 | Conector catalogado |
| 03 | Meta Ads Intelligence | Planejado | 2 / 4 | Conector catalogado |
| 04 | Social Growth | Planejado | 2 / 4 | Conector catalogado |
| 05 | Leads | Planejado | 3 | — |
| 06 | Funil Comercial | Planejado | 3 | — |
| 07 | Inteligência de Campanhas | Planejado | 2 / 6 | Cálculo de CPL, CPQL, CPA, CAC, ROAS e conversão já implementado e testado no domínio |
| 08 | Criador de Campanhas | Planejado | 5 | — |
| 09 | Criativos | Planejado | 5 / 6 | — |
| 10 | Central de Inteligência / Maya Intelligence | Planejado | 6 | FTS5 verificado e disponível |
| 11 | Integrações | Parcial | 1 → 4 | Catálogo de 9 conectores com estado real; cofre de credenciais |
| 12 | Relatórios | Planejado | 2+ | — |
| 13 | Configurações | Funcional | 1 | Ambiente, caminhos, versão do esquema, backup, restauração com confirmação, auditoria |

## Fases

- [x] **Fase 1, Fundação:** estrutura, backend, banco, migrations, design system, navegação,
      dashboard inicial, logs, backup/restauração, documentação, testes.
- [ ] **Fase 1.5, Shell desktop:** Tauri + backend como *sidecar*, testado no Windows (ADR 0002).
- [ ] **Fase 2, Inteligência de dados:** modelos de campanhas, anúncios e métricas; importação
      CSV (Google Ads, Meta Ads, social) com validação e deduplicação; dashboards com dados reais;
      Pandas. *Pré-requisito do usuário: exportar um relatório real de cada plataforma para
      definirmos o mapeamento de colunas.*
- [ ] **Fase 3, Leads e qualificação:** cadastro, origem/UTMs, pontuação explicável, funil,
      histórico, LGPD (retenção, exportação, exclusão).
- [ ] **Fase 4, Integrações de marketing:** OAuth oficial Google Ads, GA4, Meta, Instagram.
      *Pré-requisitos: developer token do Google Ads, app na Meta for Developers.*
- [ ] **Fase 5, Criador de campanhas:** editor, templates versionados por formato, exportação.
- [ ] **Fase 6, Memória e inteligência:** 5 camadas de memória, RAG com FTS5, diagnósticos,
      recomendações, camada de provedores de IA.
- [ ] **Fase 7, Integração comercial:** adaptador de CRM (após definir o fornecedor),
      atribuição, CAC e ROAS com vendas reais.
