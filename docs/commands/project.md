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
fcship project create NAME [--template TEMPLATE] [--output-dir DIR]
```

Creates a new project with a standardized structure.

| Option | Description |
| ------ | ----------- |
| `--template` | Project template to use (default, minimal, api, cli, library) |
| `--output-dir` | Directory where the project should be created |
| `--description` | Short description for the project |
| `--author` | Author name for the project |
| `--package-name` | Python package name (defaults to project name) |
| `--no-git` | Do not initialize a git repository |

The created project will include:

- Standard directory structure
- Configuration files (pyproject.toml, etc.)
- Documentation structure
- Initial code structure
- Git repository (unless `--no-git` is specified)

### Add Component

```bash
fcship project add NAME COMPONENT [--output-dir DIR]
```

Adds a component to an existing project.

Components can include:

- `cli`: Command line interface
- `api`: REST API
- `db`: Database integration
- `docs`: Documentation structure
- `tests`: Test framework
- `ci`: CI/CD configuration

### Init Project

```bash
fcship project init [--template TEMPLATE]
```

Initializes a project in the current directory. Useful for adding project structure to existing code.

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

## Examples

### Creating a New Project

```bash
# Create a standard project
fcship project create my-awesome-project --description "My awesome project"

# Create a CLI project
fcship project create my-tool --template cli --description "Command-line utility"
```

### Adding Components to a Project

```bash
# Add REST API to an existing project
fcship project add my-project api

# Add database integration
fcship project add my-project db --db-type postgres
```

### Initializing an Existing Project

```bash
# Navigate to an existing project
cd existing-code

# Initialize project structure
fcship project init --template domain
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