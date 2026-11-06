# Maya-marketing

**Equipe de agentes de marketing digital da Maya Protege**, que trabalha aqui no
claude.ai/code (nuvem) ou no VS Code. Você faz o pedido em português, o **Diretor de
Marketing** distribui o trabalho para os especialistas e devolve o material pronto para você
aprovar e publicar.

## A equipe

| Área | Agente | O que entrega |
|---|---|---|
| Coordenação | **Diretor de Marketing** (`/diretor`) | Recebe o pedido, distribui, revisa e entrega |
| Mídia paga | **Gestor de Meta Ads** | Estrutura, públicos, orçamento, testes A/B, otimização |
| Mídia paga | **Gestor de Google Ads** | Campanhas, palavras-chave, negativas, lances, otimização |
| Growth | **Estrategista de Growth** | Briefing, plano de canais e orçamento, landing pages, experimentos |
| Conteúdo e marca | **Social Media** | Linhas editoriais, calendário, análise orgânica |
| Conteúdo e marca | **Copywriter** | Textos de anúncio, títulos, CTAs, variações A/B |
| Conteúdo e marca | **Diretor de Arte** | Peças em PNG no tamanho exato de cada formato |
| Conteúdo e marca | **Guardião da Marca** | Revisão final: marca, promessas, políticas, LGPD |
| Dados e mensuração | **Analista de Mensuração** (`/gtm`) | GTM, GA4, pixel, conversões, captura de origem do lead |
| Dados e mensuração | **Especialista em UTM** (`/utm`) | Links rastreáveis e padrão de UTMs |
| Dados e mensuração | **Analista de Campanhas** (`/analisar-campanhas`) | CPC, CTR, CPL, CPA, ROAS, ROI e qual campanha performa melhor |
| Integração comercial | **Analista de Funil** | Lead qualificado, SLA com vendas, devolutiva de vendas |

## Painel da Equipe

**https://claude.ai/artifact/RTWS1SWJ2E4Sri5ynRqwUx**: mostra ao vivo o que cada agente está
fazendo, o passo a passo de cada tarefa, os arquivos gerados e o que espera sua aprovação
(com botões Aprovar e Pedir ajuste). Você conversa com a equipe no chat do Claude Code; o
painel é onde você acompanha.

## Como usar no claude.ai/code

1. Abra claude.ai/code e inicie uma sessão com o repositório **Maya-Marketing-**, no branch
   `claude/maya-marketing-fase-1` (até ele ser mesclado na `main`).
2. Escreva o pedido normalmente, por exemplo: *"Crie uma campanha de leads no Meta Ads para o
   produto X em São Paulo, R$ 50 por dia"*. Ou use um atalho:
   - `/diretor` para qualquer pedido amplo;
   - `/analisar-campanhas` e anexe os CSVs exportados do Meta/Google;
   - `/utm` para gerar ou auditar links;
   - `/gtm` para rastreamento e conversões.
3. As entregas aparecem em `entregas/AAAA-MM-DD-<tema>/`. Peça para a sessão fazer commit e
   push para guardar: a sessão na nuvem é temporária.

**Antes da primeira campanha**, preencha a tabela "A confirmar" em
[`marca/marca.md`](marca/marca.md) (produtos, regiões, público, tom, proibições) e envie os
arquivos oficiais do logotipo. Sem isso, a equipe se recusa a afirmar qualquer coisa sobre
os produtos, de propósito.

## Ferramentas testadas que os agentes usam

| Ferramenta | Função | Testes |
|---|---|---|
| `ferramentas/analisar_campanhas.py` | Lê CSVs do Meta e do Google (formato BR), calcula métricas, ranking com margem de confiança e diagnósticos | 12 |
| `ferramentas/utm.py` | Gera, padroniza e audita UTMs | 5 |
| `marketing/gtm/captura-origem.html` | Script do GTM que guarda a origem do lead e preenche campos ocultos | 7 (navegador real) |
| `ferramentas/renderizar_peca.cjs` | Exporta peças HTML em PNG no tamanho exato | verificado |

```bash
python3 -m unittest discover -s ferramentas/tests -t .
node ferramentas/tests/gtm/teste_captura_origem.cjs
```

## Limites, de propósito

- A equipe **não publica, não ativa campanhas e não gasta**: entrega pronto e você aprova.
- Sem acesso às contas de Meta, Google Ads e GTM: os dados entram por exportação CSV.
- Números só saem das ferramentas, nunca de "cálculo de cabeça" do modelo.

---

## Anexo: aplicativo local (Fase 1, pausado)

O backend e o frontend abaixo foram a primeira fundação do projeto. Estão funcionais e
testados, mas pausados: o foco passou a ser a equipe de agentes.



## 1. O que você precisa instalar (uma única vez)

| Programa | Versão | Para quê | Onde baixar |
| --- | --- | --- | --- |
| Python | 3.11 ou superior (testado na 3.13) | backend e cálculos | python.org/downloads (marque **"Add python.exe to PATH"** na instalação) |
| Node.js | 20 LTS ou superior (testado na 22) | interface | nodejs.org (versão LTS) |
| Git | qualquer recente | versionamento | git-scm.com |
| VS Code | qualquer recente | edição | code.visualstudio.com |

Para conferir se deu certo, abra o **PowerShell** (menu Iniciar, digite "PowerShell") e rode:

```powershell
py --version     # deve mostrar Python 3.11 ou superior
node --version   # deve mostrar v20 ou superior
```

## 2. Primeira instalação do projeto

1. Abra o VS Code.
2. Menu **File → Open Folder...** e escolha a pasta `Maya-Marketing-`.
3. Menu **Terminal → New Terminal** (abre um PowerShell na pasta do projeto).
4. Rode:

```powershell
.\scripts\setup.ps1
```

> Se aparecer o erro *"a execução de scripts foi desabilitada neste sistema"*, rode uma vez
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, responda **S** e tente de novo.

## 3. Executar no dia a dia

```powershell
.\scripts\dev.ps1
```

Isso abre duas janelas (backend e frontend) e o navegador em `http://127.0.0.1:5173`.
Para encerrar, feche as duas janelas do PowerShell.

**Como validar que funcionou:** no canto superior direito aparece o selo **"Dados reais"**.
Se aparecer **"Backend local fora do ar"**, a janela do backend fechou ou deu erro: leia a
mensagem nela.

## 4. Testes

```powershell
.\scripts\test.ps1
```

Roda o linter Python (ruff), 23 testes do backend (pytest), a checagem de tipos, 8 testes do
frontend (vitest) e o build de produção.

## 5. Onde ficam os dados

| O quê | Local (Windows) |
| --- | --- |
| Banco de dados real | `%LOCALAPPDATA%\MayaMarketing\maya.db` |
| Banco de demonstração | `%LOCALAPPDATA%\MayaMarketing\maya-demo.db` (arquivo separado) |
| Logs | `%LOCALAPPDATA%\MayaMarketing\logs\maya.log` |
| Backups | `%LOCALAPPDATA%\MayaMarketing\backups\real\` |
| Credenciais de APIs | Gerenciador de Credenciais do Windows (nunca no banco ou no código) |

Para mudar a pasta, crie `backend\.env` com `MAYA_DATA_DIR=D:\MinhaPasta`.
Para abrir o ambiente de demonstração: `MAYA_WORKSPACE=demo` no mesmo arquivo.

O caminho exato aparece na tela **Configurações**.

## 6. Backup e restauração

- **Criar:** tela Configurações → **Criar backup agora**. São mantidos os 30 mais recentes.
- **Restaurar:** na lista, **Restaurar** → digite `RESTAURAR` → **Confirmar restauração**.
  Antes de restaurar, a Maya salva automaticamente o estado atual (`...-pre-restauracao.db`),
  e a trilha de auditoria é preservada.
- **Proteção extra:** copie periodicamente a pasta de backups para um disco externo.

## 7. Manutenção

| Tarefa | Comando (na pasta `backend`) |
| --- | --- |
| Criar uma migration após mudar um modelo | `.\.venv\Scripts\alembic revision --autogenerate -m "descricao"` |
| Aplicar migrations manualmente | `.\.venv\Scripts\alembic upgrade head` (o backend já faz ao iniciar) |
| Atualizar dependências Python | `.\.venv\Scripts\pip install -r requirements-dev.txt --upgrade` |
| Documentação interativa da API | abra `http://127.0.0.1:8765/docs` com o backend rodando |

## 8. Estrutura

```
backend/            API local (FastAPI), banco (SQLite + SQLAlchemy + Alembic), regras de negócio
  app/core/         configuração, logs com mascaramento de dados pessoais, cofre de credenciais
  app/db/           conexão, base dos modelos, execução de migrations
  app/domain/       cálculos determinísticos (catálogo de métricas)
  app/models/       tabelas
  app/services/     casos de uso (dashboard, backup, catálogo de conectores)
  app/api/routes/   endpoints HTTP
  migrations/       histórico versionado do esquema
  tests/            testes automatizados
frontend/           interface (React + TypeScript + Vite + Tailwind)
  src/styles/       tokens de design (cores, fontes) e regras-base
  src/components/   design system (ui/) e estrutura de navegação (layout/)
  src/pages/        telas
docs/               arquitetura, decisões técnicas (ADRs) e roadmap
scripts/            instalação, execução e testes no Windows
```

## 9. Documentação

- [Arquitetura](docs/ARCHITECTURE.md)
- [Decisões técnicas (ADRs)](docs/adr/)
- [Roadmap e estado de cada módulo](docs/ROADMAP.md)
