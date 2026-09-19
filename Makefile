# ─────────────────────────────────────────────────────────────────────────────
# ROOT 404 — developer tasks (Linux/macOS).
#
# Windows PowerShell users: the Makefile uses Unix-only paths by design.
# Use the PowerShell scripts in scripts/ instead (or the raw commands
# documented in README.md → "Development setup"):
#
#   .\scripts\setup.ps1    # create venv + install backend & frontend deps
#   .\scripts\test.ps1     # run backend tests
#   .\scripts\build.ps1    # production build of the frontend
# ─────────────────────────────────────────────────────────────────────────────

PYTHON  ?= python3
VENV    := backend/.venv
VPY     := $(VENV)/bin/python
VPIP    := $(VENV)/bin/pip

.PHONY: help setup backend-setup backend-test backend-run \
        frontend-setup frontend-dev frontend-build \
        docker-build docker-up docker-down clean

help:
	@echo "ROOT 404 — available targets:"
	@echo "  make setup          Create venv + install backend and frontend deps"
	@echo "  make backend-setup  Create backend/.venv and install backend deps"
	@echo "  make backend-test   Run the backend test suite (pytest)"
	@echo "  make backend-run    Run FastAPI with auto-reload on :8000"
	@echo "  make frontend-setup Install frontend dependencies (npm ci)"
	@echo "  make frontend-dev   Vite dev server on :5173"
	@echo "  make frontend-build Production build into frontend/dist"
	@echo "  make docker-build   Build all Compose images"
	@echo "  make docker-up      Start the full stack (docker compose up -d)"
	@echo "  make docker-down    Stop the stack"
	@echo "  make clean          Remove venv, node_modules and build output"

setup: backend-setup frontend-setup

backend-setup:
	$(PYTHON) -m venv $(VENV)
	$(VPIP) install --upgrade pip
	$(VPIP) install -r backend/requirements.txt -r backend/requirements-dev.txt

backend-test:
	cd backend && .venv/bin/python -m pytest tests -v

backend-run:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

frontend-setup:
	cd frontend && npm ci

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

docker-build:
	docker compose build

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

clean:
	rm -rf $(VENV) frontend/node_modules frontend/dist
	find . -type d -name "__pycache__" -not -path "./.git/*" -exec rm -rf {} +
