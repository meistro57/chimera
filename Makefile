# Chimera Multi-AI Chat - Development Commands

.PHONY: help dev dev-db dev-backend dev-frontend build up down clean logs test migrate db-upgrade

help:
	@echo "Chimera Multi-AI Chat Development Commands"
	@echo ""
	@echo "Development:"
	@echo "  dev          - Start full development environment"
	@echo "  dev-db       - Start only database services"
	@echo "  dev-backend  - Start backend development server"
	@echo "  dev-frontend - Start frontend development server"
	@echo ""
        @echo "Production:"
        @echo "  build        - Build all Docker images"
        @echo "  up           - Start production environment"
        @echo "  down         - Stop all services"
        @echo ""
        @echo "Database:"
        @echo "  db-upgrade   - Apply Alembic migrations (alembic upgrade head)"
        @echo "  migrate      - Run database migrations"
        @echo "  migrate-auto - Generate and run auto-migration"
        @echo ""
	@echo "Utilities:"
	@echo "  logs         - Show logs from all services"
	@echo "  clean        - Clean up Docker volumes and images"
	@echo "  test         - Run tests"

# Development commands
dev: dev-db
	@echo "Starting development environment..."
	@echo "Database services are starting..."
	@echo ""
	@echo "Next steps:"
	@echo "1. Wait for database to be ready (check with 'make logs')"
	@echo "2. Run 'make dev-backend' in a new terminal"
	@echo "3. Run 'make dev-frontend' in another terminal"

dev-db:
	docker compose -f docker-compose.dev.yml up -d
	@echo "Database services started. Use 'make logs' to monitor."

dev-backend:
	@echo "Starting backend development server..."
	cd backend && python -m venv venv || true
	cd backend && . venv/bin/activate && pip install -r requirements.txt
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm install
	cd frontend && npm run dev

# Production commands
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down
	docker compose -f docker-compose.dev.yml down

# Database commands
db-upgrade:
        cd backend && python -m venv venv || true
        cd backend && . venv/bin/activate && pip install -r requirements.txt
        cd backend && . venv/bin/activate && alembic -c alembic.ini upgrade head

migrate:
        cd backend && . venv/bin/activate && alembic upgrade head

migrate-auto:
	cd backend && . venv/bin/activate && alembic revision --autogenerate -m "Auto migration"
	cd backend && . venv/bin/activate && alembic upgrade head

# Utility commands
logs:
	docker compose -f docker-compose.dev.yml logs -f

clean:
	docker compose down -v
	docker compose -f docker-compose.dev.yml down -v
	docker system prune -f

test:
	@echo "Running backend unit tests..."
	cd backend && . venv/bin/activate && python -m pytest tests/ -v --tb=short
	@echo "Running backend integration tests..."
	$(MAKE) backend-test-integration
	@echo "Running frontend tests..."
	cd frontend && npm run test

backend-test:
	cd backend && . venv/bin/activate && python -m pytest -v

backend-test-integration:
	cd backend && . venv/bin/activate && python -m pytest tests/test_*integration*.py -v --tb=short

frontend-test:
	cd frontend && npm run test

backend-lint:
	cd backend && . venv/bin/activate && python -m flake8 app/

frontend-lint:
	cd frontend && npm run lint