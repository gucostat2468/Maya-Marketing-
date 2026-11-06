# Instala as dependências do backend (Python) e do frontend (Node) pela primeira vez.
# Uso (PowerShell, na pasta do projeto):  .\scripts\setup.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "1/2 Backend: criando ambiente virtual Python..." -ForegroundColor Green
Push-Location "$root\backend"
if (-not (Test-Path ".venv")) { py -3 -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Pop-Location

Write-Host "2/2 Frontend: instalando pacotes Node..." -ForegroundColor Green
Push-Location "$root\frontend"
npm install
Pop-Location

Write-Host "Pronto. Para iniciar: .\scripts\dev.ps1" -ForegroundColor Green
