# Arquitetura da Maya-marketing

## Visão geral

```
┌───────────────────────────── Computador Windows ─────────────────────────────┐
│                                                                               │
│  Interface (React + TS)         HTTP local           Backend (FastAPI)        │
│  navegador hoje,          ───────────────────►   127.0.0.1:8765 apenas        │
│  Tauri na Fase 1.5        ◄───────────────────   ┌─────────────────────────┐  │
│  127.0.0.1:5173                JSON              │ api/routes  (HTTP)       │  │
│                                                  │ services    (casos de uso)│ │
│                                                  │ domain      (cálculos)    │ │
│                                                  │ models + db (SQLAlchemy)  │ │
│                                                  └──────────┬──────────────┘  │
│                                                             │                 │
│              %LOCALAPPDATA%\MayaMarketing\                  ▼                 │
│              maya.db · maya-demo.db · logs\ · backups\   SQLite (WAL, FKs)    │
│                                                                               │
│              Gerenciador de Credenciais do Windows  ◄── core/secrets (keyring)│
└───────────────────────────────────────────────────────────────────────────────┘
                     Fase 4+: conectores ──► Google Ads API, Meta Marketing API...
```

## Camadas do backend

| Camada | Responsabilidade | Regra |
| --- | --- | --- |
| `api/routes` | Receber requisições, validar parâmetros, devolver JSON | Sem regra de negócio |
| `services` | Orquestrar casos de uso (dashboard, backup, catálogo) | Pode usar banco e domínio |
| `domain` | Cálculos puros e determinísticos | **Sem banco, sem rede, sem IA**: 100% testável |
| `models` / `db` | Tabelas, conexão, migrations | Nenhuma lógica de negócio |
| `core` | Configuração, logs, credenciais | Transversal |

## Princípios que o código garante

1. **Ausente ≠ zero.** `domain/metrics.py` usa `None` para "sem dados" e nunca o converte em 0.
   Denominador zero gera status `undefined`, não um número.
2. **Rastreabilidade.** Cada indicador devolvido pela API carrega fórmula, numerador,
   denominador, insumos ausentes e motivo. A interface exibe isso em "Como é calculado".
3. **CAC ≠ CPA; ROAS ≠ lucro.** São indicadores separados, com ressalvas explícitas no catálogo.
   O CAC não é calculado sem o custo total de aquisição informado.
4. **Demonstração isolada fisicamente.** Real e demonstração usam arquivos de banco diferentes.
5. **Sem duplicidade de importação.** A tabela `imports` tem hash SHA-256 único por arquivo.
6. **Credenciais fora do banco.** Tokens ficam no cofre do Windows (`keyring`); a API só
   informa se existem.
7. **Logs sem dados pessoais.** Um filtro mascara e-mail, telefone, CPF e tokens antes de gravar.
8. **Auditoria preservada.** Ações relevantes vão para `audit_log`, que sobrevive à restauração.
9. **Honestidade de estado.** `services/modules.py` registra o estado real de cada módulo;
   a interface nunca mostra como pronto o que não existe.

## Modelo de dados

### Fase 1 (implementado)

| Tabela | Finalidade |
| --- | --- |
| `platforms` | Plataformas de origem (Google Ads, Meta Ads, Instagram, GA4, CRM...) |
| `integrations` | Catálogo de conectores e seu estado real. Não guarda segredos |
| `imports` | Cada arquivo importado, com hash único, contagem e período |
| `audit_log` | Trilha de auditoria |
| `app_settings` | Configurações chave-valor |

### Planejado (migrations incrementais, sem reescrever as tabelas acima)

```
Platforms ─< Accounts ─< Campaigns ─< AdGroups ─< Ads >─ Creatives
                              │            │          │
                              └──────── MarketingMetrics (fato diário: data × anúncio)
Platforms ─< SocialMetrics (fato diário por perfil)

Leads >─ LeadSources (UTMs, click ids, campanha/anúncio de origem)
  ├─< LeadEvents (mudanças de status, com data)  ─> FunnelStages
  ├─< LeadScores (pontuação 0-100, critérios, confiança, versão das regras)
  └─< Opportunities ─< Sales ─< RevenueRecords
                         └─< AttributionRecords (first/last touch; observada vs. estimada)

KnowledgeDocuments ─< KnowledgeRules   (FTS5 para busca textual)
LearningRecords · Recommendations · Experiments · BrandAssets · BrandGuidelines
Integrations ─< SyncLogs
```

A cadeia `Ads → LeadSources → Leads → Opportunities → Sales` permite reconstruir a jornada
do lead da origem até o resultado comercial.

## Frontend

- **Roteamento por hash** (`#/leads`): funciona igual no navegador e dentro do Tauri.
- **Estado na URL**: filtros do painel ficam no endereço (dá para favoritar uma visão).
- **TanStack Query**: cache e estados de carregamento, erro e vazio padronizados.
- **Design system**: tokens em `src/styles/tokens.css` (paleta Maya Protege em OKLCH);
  a paleta padrão do Tailwind foi removida, então só cores da marca existem.
  Componentes em `src/components/ui`. Cada região que carrega dados tem 4 estados:
  carregando (skeleton), vazio, erro e completo.
- **Acessibilidade**: foco visível em todo elemento interativo, contraste mínimo de 3:1
  em bordas de campo, tabelas empilhadas no celular, movimento reduzido respeitado.

## Integrações (preparação)

Cada conector futuro implementa a mesma interface: autenticar, validar, sincronizar
(incremental quando a API permitir), registrar `SyncLogs`, tratar limites de taxa e
deduplicar. Nenhum conector será marcado como `connected` sem autenticação e teste reais.
O CRM terá um adaptador genérico: nada específico de fornecedor antes da definição.

## IA

Cálculos, validações, deduplicação e agregações são sempre locais e determinísticos.
A IA (Fase 6) entra por uma camada de provedores intercambiáveis, só para interpretação,
textos e resumos. Dados pessoais não são enviados a provedores externos sem autorização.
