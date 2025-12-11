# ============================================
# Upwork Job Scraper - Makefile
# ============================================
# Project automation commands for development and deployment

.PHONY: help install setup test lint format clean run docker-build docker-run

# Default target
.DEFAULT_GOAL := help

# Conda environment name
CONDA_ENV := CrawlerMode
CONDA_RUN := conda run -n $(CONDA_ENV)

# ============================================
# Help
# ============================================

help: ## Show this help message
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Upwork Job Scraper - Available Commands"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ============================================
# Setup & Installation
# ============================================

install: ## Install all dependencies via Poetry
	$(CONDA_RUN) poetry install
	@echo "✅ Dependencies installed"

install-playwright: ## Install Playwright browsers
	$(CONDA_RUN) poetry run playwright install chromium
	@echo "✅ Playwright chromium installed"

setup: install install-playwright check-env ## Complete project setup (install + browsers + env check)
	@echo "✅ Project setup complete!"

check-env: ## Check if .env file exists
	@if [ ! -f .env ]; then \
		echo "⚠️  .env file not found!"; \
		echo "   Run: cp .env.example .env"; \
		echo "   Then edit .env with your API key"; \
		exit 1; \
	else \
		echo "✅ .env file exists"; \
	fi

check-profile: ## Check if profile.yaml exists
	@if [ ! -f profile.yaml ]; then \
		echo "⚠️  profile.yaml not found!"; \
		echo "   Already created or run: cp profile.yaml.example profile.yaml"; \
		exit 1; \
	else \
		echo "✅ profile.yaml exists"; \
	fi

# ============================================
# Running the Scraper
# ============================================

run: check-env check-profile ## Run scraper with default settings from .env
	$(CONDA_RUN) poetry run python -m src.main

run-quick: check-env ## Quick test run (1 page, no cover letters)
	$(CONDA_RUN) poetry run python -m src.main --pages 1 --skip-cover-letters

run-visible: check-env check-profile ## Run with visible browser (for debugging)
	$(CONDA_RUN) poetry run python -m src.main --no-headless --pages 1

dry-run: check-env ## Show configuration without running
	$(CONDA_RUN) poetry run python -m src.main --dry-run

# Custom run commands
run-python: check-env check-profile ## Search for Python jobs (5 pages)
	$(CONDA_RUN) poetry run python -m src.main --query "Python Developer" --pages 5

run-webscraping: check-env check-profile ## Search for web scraping jobs
	$(CONDA_RUN) poetry run python -m src.main --query "Web Scraping" --pages 3

run-automation: check-env check-profile ## Search for automation jobs
	$(CONDA_RUN) poetry run python -m src.main --query "Python Automation" --pages 3

# ============================================
# Testing
# ============================================

test: ## Run all tests
	$(CONDA_RUN) poetry run pytest

test-unit: ## Run only unit tests
	$(CONDA_RUN) poetry run pytest tests/unit/

test-integration: ## Run only integration tests
	$(CONDA_RUN) poetry run pytest tests/integration/

test-verbose: ## Run tests with verbose output
	$(CONDA_RUN) poetry run pytest -v

test-coverage: ## Run tests with coverage report
	$(CONDA_RUN) poetry run pytest --cov=src --cov-report=html --cov-report=term
	@echo "📊 Coverage report generated at: htmlcov/index.html"

test-watch: ## Run tests in watch mode (requires pytest-watch)
	$(CONDA_RUN) poetry run ptw

# ============================================
# Code Quality
# ============================================

lint: ## Run linting (ruff)
	$(CONDA_RUN) poetry run ruff check src/ tests/

lint-fix: ## Auto-fix linting issues
	$(CONDA_RUN) poetry run ruff check --fix src/ tests/

format: ## Format code with black
	$(CONDA_RUN) poetry run black src/ tests/

format-check: ## Check code formatting without changes
	$(CONDA_RUN) poetry run black --check src/ tests/

typecheck: ## Run type checking with mypy
	$(CONDA_RUN) poetry run mypy src/

quality: lint format typecheck ## Run all code quality checks

# ============================================
# Docker
# ============================================

docker-build: ## Build Docker image
	docker-compose build

docker-run: ## Run scraper in Docker
	docker-compose run scraper

docker-run-dev: ## Run in dev mode (with source mounting)
	docker-compose --profile dev up scraper-dev

docker-shell: ## Open shell in Docker container
	docker-compose run scraper /bin/bash

docker-clean: ## Remove Docker images and containers
	docker-compose down --volumes --remove-orphans
	docker system prune -f

# ============================================
# Database (if using Redis/PostgreSQL)
# ============================================

db-up: ## Start database services (Redis, PostgreSQL)
	docker-compose up -d redis postgres

db-down: ## Stop database services
	docker-compose down

db-logs: ## View database logs
	docker-compose logs -f redis postgres

# ============================================
# Cleaning
# ============================================

clean: ## Remove cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	@echo "✅ Cache cleaned"

clean-output: ## Remove all output files
	rm -rf output/
	@echo "✅ Output directory cleaned"

clean-all: clean clean-output ## Remove all cache and output files
	@echo "✅ Full cleanup complete"

# ============================================
# Utilities
# ============================================

update: ## Update all dependencies
	$(CONDA_RUN) poetry update

update-lock: ## Update poetry.lock file
	$(CONDA_RUN) poetry lock

shell: ## Open Poetry shell
	$(CONDA_RUN) poetry shell

deps: ## Show dependency tree
	$(CONDA_RUN) poetry show --tree

deps-outdated: ## Show outdated dependencies
	$(CONDA_RUN) poetry show --outdated

env-info: ## Show environment information
	@echo "Conda Environment: $(CONDA_ENV)"
	@$(CONDA_RUN) python --version
	@$(CONDA_RUN) poetry --version

logs: ## Show recent scraper logs (if using logging to file)
	@tail -f logs/*.log 2>/dev/null || echo "No log files found"

# ============================================
# Development Shortcuts
# ============================================

dev-setup: setup ## Alias for setup
	@echo "Ready for development!"

dev-run: run-quick ## Quick development run
	@echo "Development run complete"

dev-test: test-coverage ## Run tests with coverage
	@echo "Tests complete"

watch-test: test-watch ## Alias for test-watch

# ============================================
# Project Info
# ============================================

info: ## Show project information
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Project Information"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Name: Upwork Job Scraper"
	@echo "  Author: Gopal Kisi"
	@echo "  Conda Env: $(CONDA_ENV)"
	@echo "  Python: $$($(CONDA_RUN) python --version 2>&1)"
	@echo "  Poetry: $$($(CONDA_RUN) poetry --version 2>&1)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ============================================
# CI/CD Simulation
# ============================================

ci: lint format-check typecheck test ## Simulate CI pipeline locally
	@echo "✅ CI checks passed!"
