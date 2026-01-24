.PHONY: linter linter-check mypy install test help

# Default target
help:
	@echo "Available targets:"
	@echo "  linter        - Run all linters and formatters (modifies code)"
	@echo "  linter-check  - Check code with all linters (no modifications)"
	@echo "  mypy          - Run type checking with mypy"
	@echo "  install       - Install dependencies with Poetry"
	@echo "  test          - Run tests with pytest"

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

# Run type checking with mypy
mypy:
	@echo "Running type checking with mypy..."
	poetry run mypy app/

# Run tests
test:
	poetry run pytest
