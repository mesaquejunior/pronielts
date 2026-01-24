.PHONY: linter linter-check mypy install test coverage run migrate migrate-create help

# Default target
help:
	@echo "Available targets:"
	@echo "  linter        - Run all linters and formatters (modifies code)"
	@echo "  linter-check  - Check code with all linters (no modifications)"
	@echo "  mypy          - Run type checking with mypy"
	@echo "  install       - Install dependencies with Poetry"
	@echo "  test          - Run tests with pytest"
	@echo "  coverage      - Run tests with coverage report"
	@echo "  run           - Run backend API server (dev mode)"
	@echo "  migrate       - Apply database migrations (alembic upgrade head)"
	@echo "  migrate-create - Create new migration (usage: make migrate-create msg='description')"

# Install dependencies
install:
	poetry install

# Run all linters and formatters (modifies code)
linter:
	@echo "Running isort..."
	poetry run isort app/
	@echo "\nRunning black..."
	poetry run black app/
	@echo "\nRunning ruff with auto-fix..."
	poetry run ruff check --fix app/
	@echo "\nRunning deptry..."
	poetry run deptry .
	@echo "\n✅ All linters completed successfully!"

# Check code with all linters (no modifications)
linter-check:
	@echo "Checking with isort..."
	poetry run isort --check-only --diff app/
	@echo "\nChecking with black..."
	poetry run black --check --diff app/
	@echo "\nChecking with ruff..."
	poetry run ruff check app/
	@echo "\nChecking with deptry..."
	poetry run deptry .
	@echo "\n✅ All linter checks passed!"

# Run backend api server
run:
	poetry run uvicorn app.main:app --reload

# Apply database migrations
migrate:
	poetry run alembic upgrade head
	@echo "\n✅ Migrations applied successfully!"

# Create new migration
migrate-create:
	poetry run alembic revision --autogenerate -m "$(msg)"

# Run type checking with mypy
mypy:
	@echo "Running type checking with mypy..."
	poetry run mypy app/

# Run tests
test:
	poetry run pytest

# Run tests with coverage report (fails below 80%)
coverage:
	poetry run pytest --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=80
	@echo "\n✅ Coverage report generated at htmlcov/index.html"
