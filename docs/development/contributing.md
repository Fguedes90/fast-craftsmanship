# Contributing to Fast Craftsmanship

Thank you for your interest in contributing to Fast Craftsmanship! This guide will help you set up your development environment and understand our contribution workflow.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Git
- uv (recommended for dependency management)

### Clone the Repository

```bash
git clone https://github.com/Fguedes90/fast-craftsmanship.git
cd fast-craftsmanship
```

### Install Development Dependencies

```bash
uv pip install -e ".[dev]"
```

This installs the package in development mode with all required development dependencies.

## Development Workflow

### Code Style

Fast Craftsmanship follows these code style principles:

1. **Railway Oriented Programming (ROP)** using the Expression library
2. **Pydantic models** for data validation
3. **Functional programming** paradigms

Key guidelines:

- Use `Result` types for error handling (avoid try/except)
- Prefer composable functions over classes where possible
- Use immutable data structures
- Make all functions type-annotated
- Use generator-based functions with `yield from` for sequencing operations

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific tests
pytest tests/commands/test_github.py

# Run tests with coverage
pytest --cov=fcship tests/
```

### Linting

We use Ruff for linting and formatting:

```bash
# Check code style
ruff check fcship/

# Format code
ruff format fcship/
```

## Git Workflow

### Branch Naming

- `feat-*`: New features
- `fix-*`: Bug fixes
- `refactor-*`: Code refactoring
- `docs-*`: Documentation changes
- `test-*`: Adding or modifying tests

### Commit Messages

We follow the conventional commits specification:

```
<type>: <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

Example:
```
feat: add new GitHub workflow commands

Adds new commands for listing, viewing, and watching GitHub workflow runs.
The commands use the GitHub API via pygithub to retrieve workflow information.

Closes #42
```

### Pull Requests

1. Create a new branch from `main` for your changes
2. Make your changes following our code style guidelines
3. Write tests for new functionality
4. Make sure all tests pass
5. Submit a pull request to the `main` branch
6. Wait for review and address any feedback

## Documentation

We use MkDocs with the Material theme for documentation. Documentation files are in the `docs/` directory.

### Running Documentation Locally

```bash
# Install documentation dependencies
uv pip install mkdocs mkdocs-material mkdocstrings-python

# Serve documentation locally
mkdocs serve
```

### Adding Documentation

- Add code docstrings following Google style
- Update markdown files in the `docs/` directory
- Add new pages to the navigation in `mkdocs.yml`

## Creating New Commands

1. Create a new file in the appropriate directory under `fcship/commands/`
2. Use the Result type for error handling
3. Add command registration in the appropriate `__init__.py` file
4. Add tests in the `tests/commands/` directory
5. Add documentation in the `docs/commands/` directory

## Release Process

Fast Craftsmanship uses automated releases via GitHub Actions:

1. Commits to `main` run CI checks
2. Version tags (v*) trigger the release workflow
3. The release workflow builds and publishes to PyPI

## Getting Help

If you need help with contributing, feel free to:

- Open an issue on GitHub
- Ask questions in pull requests
- Reach out to the maintainers

We appreciate your contributions and look forward to your ideas!