.PHONY: help install backend frontend dev build docker-up docker-down seed test lint

help:
	@echo "ROOT 404 - Available commands:"
	@echo "  make install     - Install backend + frontend deps"
	@echo "  make backend     - Run backend API (port 8000)"
	@echo "  make frontend    - Run frontend dev server (port 5173)"
	@echo "  make dev         - Run both backend + frontend concurrently"
	@echo "  make build       - Build frontend for production"
	@echo "  make docker-up   - Start full stack via docker-compose"
	@echo "  make docker-down - Stop docker-compose"
	@echo "  make seed        - Seed demo data via API"
	@echo "  make test        - Run backend tests"
	@echo "  make lint        - Lint frontend"

install:
	cd backend && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
	cd frontend && npm install

backend:
	cd backend && ./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

dev:
	@echo "Starting backend on :8000 and frontend on :5173..."
	@(cd backend && ./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) & \
	(cd frontend && npm run dev -- --host 0.0.0.0 --port 5173) & \
	wait

build:
	cd frontend && npm run build

docker-up:
	docker-compose up --build -d
	@echo "Frontend: http://localhost:5173"
	@echo "Backend:  http://localhost:8000/api/docs"

docker-down:
	docker-compose down

seed:
	curl -X POST http://localhost:8000/api/projects/seed
	curl -X POST http://localhost:8000/api/rooms/seed
	curl -X POST http://localhost:8000/api/piscine/seed
	@echo "Seeded!"

test:
	cd backend && ./venv/bin/pytest tests/ -v

lint:
	cd frontend && npm run build

clean:
	rm -rf backend/venv backend/root404.db backend/__pycache__
	rm -rf frontend/dist frontend/node_modules
	docker-compose down -v || true
