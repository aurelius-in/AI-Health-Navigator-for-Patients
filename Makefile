.PHONY: help install setup test run clean docker-build docker-up docker-down lint format

# Default target
help:
	@echo "AI Health Navigator - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install     - Install all dependencies (backend + frontend)"
	@echo "  setup       - Setup database and load initial data"
	@echo "  setup-dev   - Setup development environment"
	@echo ""
	@echo "Development:"
	@echo "  run         - Run the full application (backend + frontend)"
	@echo "  run-backend - Run only the backend API"
	@echo "  run-frontend- Run only the frontend"
	@echo "  test        - Run all tests"
	@echo "  test-backend- Run backend tests only"
	@echo "  test-frontend- Run frontend tests only"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint        - Run linting for all code"
	@echo "  lint-backend- Run backend linting"
	@echo "  lint-frontend- Run frontend linting"
	@echo "  format      - Format all code"
	@echo "  format-backend- Format backend code"
	@echo "  format-frontend- Format frontend code"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build- Build all Docker images"
	@echo "  docker-up   - Start all services with Docker Compose"
	@echo "  docker-down - Stop all Docker services"
	@echo "  docker-logs - Show Docker logs"
	@echo ""
	@echo "Database:"
	@echo "  db-migrate  - Run database migrations"
	@echo "  db-reset   - Reset database and load sample data"
	@echo "  db-seed    - Load sample data"
	@echo ""
	@echo "Monitoring:"
	@echo "  monitoring  - Start monitoring services (Prometheus, Grafana)"
	@echo "  logs        - Show application logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean       - Clean all build artifacts and caches"
	@echo "  clean-docker- Clean Docker containers and images"

# Installation
install: install-backend install-frontend

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	cd backend && pip install -e .

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Setup
setup: setup-backend setup-frontend

setup-backend:
	@echo "Setting up backend..."
	cd backend && python scripts/setup_database.py
	cd backend && python scripts/load_medical_data.py

setup-frontend:
	@echo "Setting up frontend..."
	cd frontend && npm run build

setup-dev: install setup
	@echo "Development environment setup complete!"

# Running the application
run: run-backend run-frontend

run-backend:
	@echo "Starting backend API..."
	cd backend && python main.py serve

run-frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

# Testing
test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	cd backend && python -m pytest tests/ -v --cov=ai_health_navigator

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test

# Code quality
lint: lint-backend lint-frontend

lint-backend:
	@echo "Linting backend code..."
	cd backend && flake8 ai_health_navigator/ tests/
	cd backend && mypy ai_health_navigator/

lint-frontend:
	@echo "Linting frontend code..."
	cd frontend && npm run lint

format: format-backend format-frontend

format-backend:
	@echo "Formatting backend code..."
	cd backend && black ai_health_navigator/ tests/
	cd backend && isort ai_health_navigator/ tests/

format-frontend:
	@echo "Formatting frontend code..."
	cd frontend && npm run format

# Docker commands
docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "Showing Docker logs..."
	docker-compose logs -f

# Database commands
db-migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

db-reset:
	@echo "Resetting database..."
	cd backend && python scripts/setup_database.py --reset

db-seed:
	@echo "Loading sample data..."
	cd backend && python scripts/setup_database.py --seed

# Monitoring
monitoring:
	@echo "Starting monitoring services..."
	docker-compose up -d prometheus grafana elasticsearch kibana

logs:
	@echo "Showing application logs..."
	docker-compose logs -f api frontend

# Cleanup
clean: clean-backend clean-frontend

clean-backend:
	@echo "Cleaning backend..."
	cd backend && find . -type d -name "__pycache__" -exec rm -rf {} +
	cd backend && find . -type f -name "*.pyc" -delete
	cd backend && find . -type f -name "*.pyo" -delete
	cd backend && rm -rf .pytest_cache/
	cd backend && rm -rf .coverage
	cd backend && rm -rf htmlcov/
	cd backend && rm -rf dist/
	cd backend && rm -rf build/
	cd backend && rm -rf *.egg-info/

clean-frontend:
	@echo "Cleaning frontend..."
	cd frontend && rm -rf node_modules/
	cd frontend && rm -rf dist/
	cd frontend && rm -rf build/
	cd frontend && rm -rf .cache/
	cd frontend && rm -rf coverage/

clean-docker:
	@echo "Cleaning Docker..."
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

# Development shortcuts
dev: setup-dev run
dev-docker: docker-build docker-up
dev-test: test lint format
