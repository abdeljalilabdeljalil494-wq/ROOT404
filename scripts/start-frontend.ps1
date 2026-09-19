# ROOT 404 — start the Vite dev server on Windows PowerShell.
# Usage:  .\scripts\start-frontend.ps1
# Installs node_modules first if they do not exist yet.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "==> frontend\node_modules not found - running npm.cmd ci" -ForegroundColor Yellow
    Push-Location frontend
    npm.cmd ci
    if ($LASTEXITCODE -ne 0) { throw "npm.cmd ci failed" }
    Pop-Location
}

Write-Host "==> Starting Vite dev server on http://localhost:5173" -ForegroundColor Cyan
Push-Location frontend
npm.cmd run dev
