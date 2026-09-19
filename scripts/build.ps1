# ROOT 404 — production build of the frontend on Windows PowerShell.
# Usage:  .\scripts\build.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Push-Location frontend
npm.cmd run build
$code = $LASTEXITCODE
Pop-Location
exit $code
