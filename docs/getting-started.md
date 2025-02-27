# Getting Started

This guide will help you get started with Fast Craftsmanship, a CLI tool designed to accelerate development tasks while following best practices.

## Installation

### Prerequisites

- Python 3.12 or higher
- pip or uv (recommended)

### Install with pip

```bash
pip install fast-craftsmanship
```

### Install with uv (recommended)

```bash
uv pip install fast-craftsmanship
```

### Development Installation

If you want to contribute or modify the tool:

```bash
git clone https://github.com/Fguedes90/fast-craftsmanship.git
cd fast-craftsmanship
uv pip install -e ".[dev]"
```

## Verify Installation

After installing, verify that the tool is working correctly:

```bash
fcship --version
```

This should display the version number of Fast Craftsmanship.

## Basic Commands

### Create a New Project

```bash
fcship project create my-project
```

This creates a new project with a standardized structure.

### Set Up GitHub Integration

Fast Craftsmanship can set up your GitHub repository with CI/CD workflows:

```bash
# Create a new GitHub repository
fcship github create my-project

# Set up CI/CD workflows
fcship github setup setup-workflows my-project
```

### Generate Domain Models

Create domain models following DDD principles:

```bash
fcship domain create User name:str email:str
```

### Run Tests and Verification

```bash
fcship verify
```

## CLI Command Structure

Fast Craftsmanship commands follow a consistent structure:

```
fcship <command> <subcommand> [options] [arguments]
```

For example:

```bash
fcship github create my-repository --private --description "My private repository"
```

## Getting Help

You can get help on any command by using the `--help` flag:

```bash
# General help
fcship --help

# Help for a specific command
fcship github --help

# Help for a specific subcommand
fcship github create --help
```

## Next Steps

Now that you've installed Fast Craftsmanship and learned the basics, you can:

- Explore the [Commands Reference](commands/index.md) for detailed information on all available commands
- Learn about [Functional Programming](functional/index.md) principles used in Fast Craftsmanship
- Check out the [Development Guide](development/contributing.md) if you want to contribute to the project