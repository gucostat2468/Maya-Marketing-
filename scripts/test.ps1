# Executa todos os testes e verificações (backend e frontend).
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location "$root\backend"
& .\.venv\Scripts\python.exe -m ruff check app tests migrations
& .\.venv\Scripts\python.exe -m pytest
Pop-Location
Push-Location "$root\frontend"
npm run typecheck
npm test
npm run build
Pop-Location
