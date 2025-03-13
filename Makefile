.PHONY: help test test-cov lint format clean clean-install install dev-install docs serve-docs build-docs tui release-patch release-minor release-major semantic-release setup-dev

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup-dev: clean  ## Setup development environment with uv (clean install)
	uv venv
	. .venv/bin/activate && uv pip install -e ".[dev,docs]" --force-reinstall

test:  ## Run all tests
	pytest tests

test-cov:  ## Run tests with coverage report
	pytest --cov=fcship tests/ --cov-report=html

lint:  ## Lint code with ruff
	ruff check ./fcship ./tests

format:  ## Format code with ruff
	ruff format ./fcship ./tests
	ruff check --fix --unsafe-fixes ./fcship ./tests

check-all: lint test  ## Run linting and tests

clean:  ## Clean up build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf ./backend/
	rm -rf ./.coverage*
	rm -rf ./site
	rm -rf ./.venv
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".Python" -delete
	find . -type f -name "*.so" -delete
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type f -name "*.class" -delete

clean-install: clean  ## Clean and reinstall the package with all dependencies
	uv venv
	. .venv/bin/activate && uv pip install -e ".[dev,docs]"

install:  ## Install the package
	uv pip install -e .

dev-install:  ## Install the package with development dependencies
	uv pip install -e ".[dev,docs]"

docs:  ## Build and serve documentation
	mkdocs serve

build-docs:  ## Build documentation only
	mkdocs build

serve-docs:  ## Serve documentation with live reload
	mkdocs serve --dev-addr localhost:8000

tui:  ## Launch the interactive Terminal UI
	python -m fcship.cli menu

release-patch:  ## Create a new patch release (0.0.x)
	@echo "Creating a new patch release..."
	python scripts/semantic_release.py --bump patch

release-minor:  ## Create a new minor release (0.x.0)
	@echo "Creating a new minor release..."
	python scripts/semantic_release.py --bump minor

release-major:  ## Create a new major release (x.0.0)
	@echo "Creating a new major release..."
	python scripts/semantic_release.py --bump major

semantic-release:  ## Analyze commits and create a release automatically
	@echo "Analyzing commits and creating release..."
	python scripts/semantic_release.py