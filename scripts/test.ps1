# ROOT 404 — run the backend test suite on Windows PowerShell.
# Usage:  .\scripts\test.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path "backend\.venv\Scripts\python.exe")) {
    throw "backend\.venv not found - run .\scripts\setup.ps1 first"
}

Push-Location backend
.\.venv\Scripts\python.exe -m pytest
$code = $LASTEXITCODE
Pop-Location
exit $code
