.PHONY: help install test test-html test-smoke test-auth test-tests test-stats test-lists test-regression test-positive test-negative test-parallel lint fix format format-check clean all \
	docker-build docker-test docker-test-html docker-test-smoke docker-test-auth docker-test-tests docker-test-stats \
	docker-test-lists docker-test-regression docker-test-parallel docker-shell docker-clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

test: ## Run all tests
	mkdir -p logs
	uv run python -m pytest tests/ -v

test-html: ## Run tests and generate HTML report
	mkdir -p logs
	mkdir -p reports
	rm -rf reports/* 2>/dev/null || true
	uv run python -m pytest tests/ -v --html=reports/test_report.html --self-contained-html

test-smoke: ## Run smoke tests
	uv run python -m pytest tests/ -m smoke -v

test-auth: ## Run authentication tests
	uv run python -m pytest tests/test_auth.py -v

test-tests: ## Run test case management tests
	uv run python -m pytest tests/test_test_cases.py -v

test-stats: ## Run statistics tests
	uv run python -m pytest tests/test_stats.py -v

test-lists: ## Run test list tests
	uv run python -m pytest tests/test_lists.py -v

test-regression: ## Run regression tests
	uv run python -m pytest tests/ -m regression -v

test-parallel: ## Run tests in parallel
	uv run python -m pytest tests/ -n auto -v

test-positive: ## Run positive tests only
	uv run python -m pytest tests/ -m positive -v

test-negative: ## Run negative tests only
	uv run python -m pytest tests/ -m negative -v

lint: ## Run linter
	uv run ruff check .

fix: ## Fix linting issues automatically
	uv run ruff check --fix .
	uv run ruff format .

format: ## Format code
	uv run ruff format .

format-check: ## Check formatting without modifying files
	uv run ruff format --check .

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .ruff_cache
	rm -rf .vscode
	rm -rf reports
	rm -rf logs
	@echo "Cleanup complete!"

all: install format lint test

docker-build: ## Build Docker image
	mkdir -p logs
	docker compose build

docker-test: ## Run all tests in Docker
	mkdir -p logs
	docker compose run --rm -v $(CURDIR)/logs:/app/logs tests uv run python -m pytest tests/ -v

docker-test-html: ## Run tests in Docker with HTML report
	mkdir -p logs
	mkdir -p reports
	rm -rf reports/* 2>/dev/null || true
	docker compose run --rm -v $(CURDIR)/logs:/app/logs -v $(CURDIR)/reports:/app/reports tests uv run python -m pytest tests/ -v --html=./reports/test_report.html --self-contained-html

docker-test-smoke: ## Run smoke tests in Docker
	mkdir -p logs
	docker compose run --rm -v $(CURDIR)/logs:/app/logs tests uv run python -m pytest tests/ -m smoke -v

docker-test-auth: ## Run authentication tests in Docker
	mkdir -p logs
	docker compose run --rm -v $(CURDIR)/logs:/app/logs tests uv run python -m pytest tests/test_auth.py -v

docker-test-tests: ## Run test case management tests in Docker
	mkdir -p logs
	docker compose run --rm -v $(CURDIR)/logs:/app/logs tests uv run python -m pytest tests/test_test_cases.py -v

docker-test-stats: ## Run statistics tests in Docker
	mkdir -p logs
	docker compose run --rm -v $(CURDIR)/logs:/app/logs tests uv run python -m pytest tests/test_stats.py -v

docker-test-lists: ## Run test list tests in Docker
	mkdir -p logs
	docker compose run --rm -v $(CURDIR)/logs:/app/logs tests uv run python -m pytest tests/test_lists.py -v

docker-test-regression: ## Run regression tests in Docker
	mkdir -p logs
	docker compose run --rm -v $(CURDIR)/logs:/app/logs tests uv run python -m pytest tests/ -m regression -v

docker-test-parallel: ## Run tests in parallel in Docker
	mkdir -p logs
	docker compose run --rm -v $(CURDIR)/logs:/app/logs tests uv run python -m pytest tests/ -n auto -v

docker-shell: ## Open shell in Docker container
	mkdir -p logs
	docker compose run --rm -v $(CURDIR)/logs:/app/logs tests /bin/bash

docker-clean: ## Remove Docker containers and images
	docker compose down --rmi local --volumes --remove-orphans || true

