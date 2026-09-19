# ROOT 404 — start the FastAPI backend on Windows PowerShell.
# Usage:  .\scripts\start-backend.ps1
# Creates the venv first if it does not exist yet.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path "backend\.venv\Scripts\python.exe")) {
    Write-Host "==> backend\.venv not found - running setup first" -ForegroundColor Yellow
    & "$Root\scripts\setup.ps1"
}

Write-Host "==> Starting FastAPI on http://localhost:8000 (docs: /api/docs)" -ForegroundColor Cyan
Set-Location backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
