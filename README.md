# Maya-marketing

Plataforma **local** de inteligência de marketing da Maya Protege: aquisição, campanhas,
crescimento social, leads, funil comercial e aprendizado contínuo. Roda no seu computador
Windows, sem hospedagem, sem servidor remoto e sem domínio. Os dados ficam só na sua máquina.

> **Estado atual: Fase 1 (Fundação) concluída.** O painel funciona, mas ainda **não há dados
> reais**: nenhum indicador é inventado. Veja [`docs/ROADMAP.md`](docs/ROADMAP.md).

---

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
