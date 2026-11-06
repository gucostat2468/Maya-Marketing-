# ADR 0001: Aplicação local com backend Python e interface web

- **Status:** aceita
- **Data:** 2026-11-06

## Contexto

Uso pessoal e operacional no Windows, sem nuvem. Precisamos de análise de dados (Pandas,
estatística, scikit-learn), persistência robusta e uma interface de nível profissional.

## Decisão

- **Backend:** Python 3.11+ com FastAPI, escutando **somente** em `127.0.0.1`.
- **Banco:** SQLite (modo WAL, chaves estrangeiras ativas) com SQLAlchemy 2 e Alembic.
- **Interface:** React + TypeScript + Vite + Tailwind CSS v4, Recharts para gráficos.
- **Dados fora do repositório:** `%LOCALAPPDATA%\MayaMarketing`.

## Alternativas consideradas

- *Tudo em Rust/Tauri, sem Python:* perderíamos o ecossistema de análise de dados.
- *Electron:* consome muito mais memória que Tauri.
- *PostgreSQL local:* exige instalar e manter um serviço; SQLite basta para um usuário.

## Consequências

- Duas linguagens (Python e TypeScript), compensado pela separação clara de papéis.
- SQLite não suporta `ALTER COLUMN`: migrations usam o modo *batch* do Alembic.
- Pandas/NumPy/scikit-learn ainda **não** foram instalados: entram na Fase 2, quando houver
  dados para analisar (evita dependências sem uso).
