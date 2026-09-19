# ROOT 404 — start the full Docker Compose stack on Windows PowerShell.
# Usage:  .\scripts\docker-up.ps1
#
# Requires: Docker Desktop RUNNING and a .env file (see .env.example).

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker is not reachable. Start Docker Desktop and try again."
}
if (-not (Test-Path ".env")) {
    Write-Warning "No .env found. Copy .env.example to .env and generate SECRET_KEY + POSTGRES_PASSWORD first:"
    Write-Host '  Copy-Item .env.example .env'
    Write-Host '  python -c "import secrets; print(secrets.token_urlsafe(48))"'
    throw "Missing .env"
}

docker compose up -d --build
if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }
docker compose ps
Write-Host ""
Write-Host "Frontend : http://localhost:8080" -ForegroundColor Green
Write-Host "API      : http://localhost:8000/api/health" -ForegroundColor Green
Write-Host "Swagger  : http://localhost:8000/api/docs" -ForegroundColor Green
Write-Host "Stop with: docker compose down"
