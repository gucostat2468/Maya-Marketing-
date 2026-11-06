# Inicia o backend (FastAPI, porta 8765) e o frontend (Vite, porta 5173) em janelas separadas.
# Uso (PowerShell, na pasta do projeto):  .\scripts\dev.ps1
$root = Split-Path -Parent $PSScriptRoot

Start-Process powershell -ArgumentList "-NoExit", "-Command", `
  "cd '$root\backend'; .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8765 --reload"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev"

Start-Sleep -Seconds 4
Start-Process "http://127.0.0.1:5173"
Write-Host "Maya-marketing iniciada. Feche as duas janelas do PowerShell para encerrar." -ForegroundColor Green
