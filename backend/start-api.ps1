# Démarre l'API CyberCafé (évite Activate.ps1 et gère un port libre)
param(
    [int]$Port = 8010
)

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Error "venv introuvable. Exécutez: python -m venv .venv puis pip install -r requirements.txt"
    exit 1
}

Write-Host "API sur http://127.0.0.1:$Port/docs" -ForegroundColor Green
Write-Host "Pour Electron: `$env:CYBERCAFE_API='http://127.0.0.1:$Port/api/v1'" -ForegroundColor Yellow
& $python -m uvicorn app.main:app --host 127.0.0.1 --port $Port --reload
