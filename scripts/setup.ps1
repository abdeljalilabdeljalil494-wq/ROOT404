# ROOT 404 — one-time developer setup on Windows PowerShell.
#
# Usage:  .\scripts\setup.ps1
#
# Uses `npm.cmd` (not `npm`) because PowerShell blocks npm.ps1 under the
# default execution policy — see README "Windows (PowerShell) notes".
# This script never changes your system execution policy.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "==> Creating backend virtual environment (backend\.venv)" -ForegroundColor Cyan
Push-Location backend
python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "python -m venv failed" }
.\.venv\Scripts\python.exe -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw "backend dependency installation failed" }
Pop-Location

Write-Host "==> Installing frontend dependencies (npm.cmd ci)" -ForegroundColor Cyan
Push-Location frontend
npm.cmd ci
if ($LASTEXITCODE -ne 0) { throw "npm.cmd ci failed" }
Pop-Location

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "  Backend tests : .\scripts\test.ps1"
Write-Host "  Frontend build: .\scripts\build.ps1"
Write-Host "  Full stack    : docker compose up -d --build   (needs .env, see .env.example)"
