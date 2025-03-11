# Project Commands

The `project` command group helps you create and manage project structures according to best practices.

## Overview

The `project` commands provide tools for:

- Creating new projects with standard structure
- Setting up project configuration 
- Adding components to existing projects
- Migrating existing code to follow best practices

## Commands

### Create Project

```bash
fcship project create NAME [OPTIONS]
```

Creates a new project with a standardized structure.

| Option | Description |
| ------ | ----------- |
| `--template TEXT` | Project template to use (default, minimal, api, cli, library, domain) |
| `--output-dir TEXT` | Directory where the project should be created |
| `--description TEXT` | Short description for the project |
| `--author TEXT` | Author name for the project |
| `--package-name TEXT` | Python package name (defaults to project name) |
| `--no-git / --git` | Do not initialize a git repository (default: initialize git) |

**Examples:**

Create a standard Python project:
```bash
fcship project create my-awesome-project
```

Create a project with a specific template and description:
```bash
fcship project create my-api-service --template api --description "REST API service for data processing"
```

Create a CLI tool with custom package name and author:
```bash
fcship project create devtool --template cli --package-name dev_toolkit --author "Your Name" --description "Development toolkit CLI"
```

Create a project in a specific directory without git initialization:
```bash
fcship project create my-library --template library --output-dir ~/projects --no-git
```

### Add Component

```bash
fcship project add NAME COMPONENT [OPTIONS]
```

Adds a component to an existing project.

| Option | Description |
| ------ | ----------- |
| `--output-dir TEXT` | Directory where the component should be added |
| `--db-type TEXT` | Database type for db component (sqlite, postgres, mysql) |
| `--api-type TEXT` | API framework for api component (fastapi, flask, django) |
| `--test-framework TEXT` | Test framework for tests component (pytest, unittest) |

**Components:**

- `cli`: Command line interface
- `api`: REST API
- `db`: Database integration
- `docs`: Documentation structure
- `tests`: Test framework
- `ci`: CI/CD configuration

**Examples:**

Add a CLI component to an existing project:
```bash
fcship project add my-project cli
```

Add a database component with PostgreSQL:
```bash
fcship project add my-project db --db-type postgres
```

Add a REST API using FastAPI:
```bash
fcship project add my-project api --api-type fastapi
```

Add test framework with pytest:
```bash
fcship project add my-project tests --test-framework pytest
```

### Init Project

```bash
fcship project init [OPTIONS]
```

Initializes a project in the current directory. Useful for adding project structure to existing code.

| Option | Description |
| ------ | ----------- |
| `--template TEXT` | Project template to use (default, minimal, api, cli, library, domain) |
| `--name TEXT` | Project name (defaults to directory name) |
| `--description TEXT` | Short description for the project |
| `--author TEXT` | Author name for the project |
| `--package-name TEXT` | Python package name (defaults to project name) |

**Examples:**

Initialize a project in the current directory with default template:
```bash
fcship project init
```

Initialize a project with a specific template:
```bash
fcship project init --template domain --name my-domain-project
```

Initialize a project with custom package name and description:
```bash
fcship project init --package-name custom_package --description "My existing project with new structure"
```

## Project Templates

Fast Craftsmanship includes several project templates:

| Template | Description |
| -------- | ----------- |
| `default` | Standard Python project with package structure |
| `minimal` | Minimal Python package with basic configuration |
| `api` | FastAPI-based REST API project |
| `cli` | Command-line application using Typer |
| `library` | Reusable Python library package |
| `domain` | Domain-driven design project structure |

### Default Template

The default template creates a standard Python project structure with:

- Source code package
- Tests directory
- Documentation
- CI/CD configuration
- Project configuration files

### API Template

The API template creates a project structure optimized for REST APIs:

- FastAPI application structure
- API routes and endpoints
- Request/response models
- Database integration
- API documentation
- Docker configuration

### CLI Template

The CLI template creates a project structure for command-line applications:

- Typer-based CLI structure
- Command groups and subcommands
- Configuration handling
- Rich TUI components
- Packaging for distribution

### Library Template

The library template creates a structure for reusable Python packages:

- Clean API design
- Comprehensive documentation
- Example usage
- Test coverage
- PyPI publishing configuration

### Domain Template

The domain template creates a structure following Domain-Driven Design principles:

- Domain model layer
- Application service layer
- Infrastructure layer
- Interfaces layer
- Bounded contexts

## Workflow Examples

### Creating and Setting Up a New API Project

```bash
# Create a new API project
fcship project create user-service --template api --description "User management service"

# Navigate to the project directory
cd user-service

# Add database integration
fcship project add user-service db --db-type postgres

# Add CI/CD configuration
fcship project add user-service ci

# Initialize git repository
git init
git add .
git commit -m "Initial project structure"

# Set up GitHub repository
fcship github setup init-repo user-service --description "User management service"
```

### Migrating an Existing Project

```bash
# Navigate to existing project
cd existing-project

# Initialize project structure
fcship project init --template default --name existing-project

# Add documentation structure
fcship project add existing-project docs

# Add test framework
fcship project add existing-project tests --test-framework pytest

# Set up CI/CD
fcship project add existing-project ci
```

### Creating a CLI Tool

```bash
# Create a new CLI project
fcship project create devtool --template cli --description "Development toolkit"

# Navigate to the project directory
cd devtool

# Add documentation
fcship project add devtool docs

# Set up for distribution
fcship project add devtool ci
```

## Project Structure

The default project structure follows these conventions:

```
my-project/
├── .github/workflows/      # CI/CD configuration
├── docs/                   # Documentation
├── my_project/             # Source code package
│   ├── __init__.py
│   ├── cli.py             # Command line interface
│   ├── core/              # Core functionality
│   └── utils/             # Utility functions
├── tests/                  # Test files
│   ├── __init__.py
│   └── test_core.py
├── .gitignore              # Git ignore file
├── LICENSE                 # License file
├── README.md               # README file
├── CHANGELOG.md            # Changelog
└── pyproject.toml          # Project configuration
```

## Customizing Project Templates

You can create custom project templates by placing template files in:

```
~/.config/fcship/templates/project/
```

Each template should be a directory containing template files for a project type.

### Custom Template Structure

A custom template directory should have the following structure:

```
my-custom-template/
├── __template__.json       # Template metadata
├── {{project_name}}/       # Project root directory
│   ├── src/                # Source files with template variables
│   └── ...                 # Other project files
```

The `__template__.json` file defines metadata for your template:

```json
{
  "name": "my-custom-template",
  "description": "My custom project template",
  "variables": {
    "project_name": {
      "description": "Name of the project",
      "default": "my-project"
    },
    "author": {
      "description": "Author name",
      "default": "Your Name"
    }
  }
}
```

Template files can use Jinja2-style variables:

```python
"""{{ project_name }} package."""

__version__ = "0.1.0"
__author__ = "{{ author }}"
```

## Best Practices

- Choose the appropriate template for your project type
- Add components incrementally as needed
- Initialize git repository early
- Set up CI/CD configuration from the start
- Keep documentation updated as the project evolves
- Use consistent naming conventions across the project