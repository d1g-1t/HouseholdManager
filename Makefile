.PHONY: help setup docker-setup clean test lint format migrate run docker-up docker-down docker-logs docker-clean

.DEFAULT_GOAL := help

DOCKER_COMPOSE := docker compose

help:
	@echo "HouseholdManager - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup         - Complete Docker setup (recommended)"
	@echo "  make docker-setup  - Alias for setup"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up     - Start all services"
	@echo "  make docker-down   - Stop all services"
	@echo "  make docker-logs   - Show logs"
	@echo "  make docker-clean  - Remove all containers and volumes"
	@echo "  make docker-shell  - Open shell in web container"
	@echo ""
	@echo "Development:"
	@echo "  make migrate       - Run migrations"
	@echo "  make shell         - Django shell"
	@echo "  make superuser     - Create superuser"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo ""

setup: docker-setup

docker-setup: docker-build docker-up docker-wait docker-migrate docker-complete

docker-build:
	@echo "Building Docker images..."
	@$(DOCKER_COMPOSE) build

docker-up:
	@echo "Starting services..."
	@$(DOCKER_COMPOSE) up -d
	@echo "Services started."

docker-wait:
	@echo "Waiting for database..."
	@sleep 5

docker-migrate:
	@echo "Running migrations..."
	@$(DOCKER_COMPOSE) exec -T web python manage.py migrate --noinput
	@echo "Migrations complete."

docker-complete:
	@echo ""
	@echo "========================================"
	@echo "  Setup completed successfully!"
	@echo "========================================"
	@echo ""
	@echo "Services:"
	@echo "  - API:     http://localhost:8000/api/docs"
	@echo "  - Admin:   http://localhost:8000/admin"
	@echo "  - Flower:  http://localhost:5555"
	@echo ""
	@echo "Create superuser: make superuser"
	@echo ""

docker-down:
	@$(DOCKER_COMPOSE) down

docker-logs:
	@$(DOCKER_COMPOSE) logs -f

docker-clean:
	@$(DOCKER_COMPOSE) down -v --remove-orphans
	@docker system prune -f

docker-shell:
	@$(DOCKER_COMPOSE) exec web sh

migrate:
	@$(DOCKER_COMPOSE) exec -T web python manage.py migrate

shell:
	@$(DOCKER_COMPOSE) exec web python manage.py shell

superuser:
	@$(DOCKER_COMPOSE) exec web python manage.py createsuperuser

test:
	@$(DOCKER_COMPOSE) exec -T web python -m pytest

lint:
	@$(DOCKER_COMPOSE) exec -T web python -m ruff check apps household_manager

format:
	@$(DOCKER_COMPOSE) exec -T web python -m black apps household_manager
	@$(DOCKER_COMPOSE) exec -T web python -m isort apps household_manager

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage 2>/dev/null || true