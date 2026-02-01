# =============================================================================
# ApexTrade Makefile
# =============================================================================

.PHONY: help dev prod build down logs migrate test lint clean setup

# Default target
help:
	@echo "ApexTrade Development Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup:"
	@echo "  make setup     - Initial setup (generate secrets, create directories)"
	@echo ""
	@echo "Development:"
	@echo "  make dev       - Start development environment"
	@echo "  make build     - Build all Docker containers"
	@echo "  make down      - Stop all containers"
	@echo "  make logs      - View all container logs"
	@echo "  make logs-api  - View API container logs"
	@echo "  make logs-web  - View frontend container logs"
	@echo ""
	@echo "Production:"
	@echo "  make prod      - Start production environment"
	@echo "  make prod-down - Stop production environment"
	@echo ""
	@echo "Database:"
	@echo "  make migrate   - Run database migrations"
	@echo "  make migrate-new NAME=<name> - Create new migration"
	@echo "  make db-shell  - Open PostgreSQL shell"
	@echo ""
	@echo "Testing:"
	@echo "  make test      - Run all tests"
	@echo "  make test-back - Run backend tests only"
	@echo "  make test-front- Run frontend tests only"
	@echo "  make test-cov  - Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint      - Run all linters"
	@echo "  make lint-back - Run backend linters (ruff, black)"
	@echo "  make lint-front- Run frontend linters (eslint)"
	@echo "  make format    - Format all code"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean     - Remove containers, volumes, and cache"
	@echo "  make shell-api - Open shell in API container"
	@echo "  make shell-web - Open shell in frontend container"

# =============================================================================
# Setup
# =============================================================================
setup:
	@echo "Running initial setup..."
	@chmod +x scripts/*.sh 2>/dev/null || true
	@./scripts/setup.sh

# =============================================================================
# Development
# =============================================================================
dev:
	@echo "Starting development environment..."
	docker-compose up -d
	@echo ""
	@echo "Services started:"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - API:      http://localhost:8000"
	@echo "  - API Docs: http://localhost:8000/docs"
	@echo "  - Grafana:  http://localhost:3001"
	@echo "  - MinIO:    http://localhost:9001"
	@echo ""
	@echo "Run 'make logs' to view logs"

dev-attach:
	docker-compose up

build:
	@echo "Building all containers..."
	docker-compose build --parallel

rebuild:
	@echo "Rebuilding all containers (no cache)..."
	docker-compose build --no-cache --parallel

down:
	@echo "Stopping all containers..."
	docker-compose down

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-web:
	docker-compose logs -f frontend

logs-workers:
	docker-compose logs -f worker-backtest worker-strategy celery-beat

# =============================================================================
# Production
# =============================================================================
prod:
	@echo "Starting production environment..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "Production environment started"

prod-build:
	@echo "Building production containers..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --parallel

prod-down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# =============================================================================
# Database
# =============================================================================
migrate:
	@echo "Running database migrations..."
	docker-compose exec api alembic upgrade head

migrate-new:
	@if [ -z "$(NAME)" ]; then \
		echo "Usage: make migrate-new NAME=<migration_name>"; \
		exit 1; \
	fi
	docker-compose exec api alembic revision --autogenerate -m "$(NAME)"

migrate-down:
	docker-compose exec api alembic downgrade -1

migrate-history:
	docker-compose exec api alembic history

db-shell:
	docker-compose exec postgres psql -U apextrade -d apextrade

db-timescale-shell:
	docker-compose exec timescaledb psql -U apextrade -d apextrade_timeseries

# =============================================================================
# Testing
# =============================================================================
test: test-back test-front

test-back:
	@echo "Running backend tests..."
	docker-compose exec api pytest tests/ -v

test-front:
	@echo "Running frontend tests..."
	docker-compose exec frontend npm run test

test-cov:
	@echo "Running tests with coverage..."
	docker-compose exec api pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-watch:
	docker-compose exec api pytest tests/ -v --watch

# =============================================================================
# Code Quality
# =============================================================================
lint: lint-back lint-front

lint-back:
	@echo "Linting backend code..."
	docker-compose exec api ruff check app/ tests/
	docker-compose exec api black --check app/ tests/

lint-front:
	@echo "Linting frontend code..."
	docker-compose exec frontend npm run lint

format:
	@echo "Formatting code..."
	docker-compose exec api ruff check app/ tests/ --fix
	docker-compose exec api black app/ tests/
	docker-compose exec frontend npm run format

type-check:
	@echo "Running type checks..."
	docker-compose exec api mypy app/
	docker-compose exec frontend npm run type-check

# =============================================================================
# Utilities
# =============================================================================
shell-api:
	docker-compose exec api /bin/bash

shell-web:
	docker-compose exec frontend /bin/sh

shell-redis:
	docker-compose exec redis redis-cli

clean:
	@echo "Cleaning up..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete"

clean-volumes:
	@echo "WARNING: This will delete all data volumes!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	docker-compose down -v
	docker volume rm apextrade-postgres-data apextrade-timescale-data apextrade-redis-data apextrade-minio-data apextrade-prometheus-data apextrade-grafana-data 2>/dev/null || true

# =============================================================================
# Health Checks
# =============================================================================
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | jq . || echo "API: DOWN"
	@curl -s http://localhost:3000 > /dev/null && echo "Frontend: UP" || echo "Frontend: DOWN"
	@docker-compose exec redis redis-cli ping | grep -q PONG && echo "Redis: UP" || echo "Redis: DOWN"
	@docker-compose exec postgres pg_isready -U apextrade > /dev/null && echo "PostgreSQL: UP" || echo "PostgreSQL: DOWN"

status:
	docker-compose ps
