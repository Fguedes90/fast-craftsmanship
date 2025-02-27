.PHONY: help test test-cov lint format clean install dev-install release-patch release-minor release-major semantic-release

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test:  ## Run all tests
	pytest tests

test-cov:  ## Run tests with coverage report
	pytest --cov=fcship tests/

lint:  ## Lint code with ruff
	ruff check fcship/

format:  ## Format code with ruff
	ruff check --fix --unsafe-fixes fcship/

check-all: lint test  ## Run linting and tests

clean:  ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:  ## Install the package
	pip install -e .

dev-install:  ## Install the package with development dependencies
	pip install -e ".[dev]"

docs:  ## Generate documentation (placeholder - add your documentation command)
	@echo "Add your documentation generation command here"

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