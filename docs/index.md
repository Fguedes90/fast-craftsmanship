# Fast Craftsmanship

Welcome to the Fast Craftsmanship documentation!

## What is Fast Craftsmanship?

Fast Craftsmanship is a CLI tool designed to accelerate development tasks while adhering to best practices in software engineering. It provides a set of commands for creating project structures, managing GitHub repositories, and implementing domain-driven design patterns following functional programming principles.

## Features

- **GitHub Integration**: Manage GitHub repositories, workflows, and settings directly from CLI
- **Project Setup**: Create new projects with standardized structure and configurations
- **Code Generation**: Generate boilerplate code for domains, repositories, and services
- **Functional Programming**: Built with Railway Oriented Programming principles using the Expression library
- **Domain-Driven Design**: Support for DDD patterns and practices

## Installation

```bash
pip install fast-craftsmanship
```

## Quick Start

```bash
# Create a new project
fcship project create my-awesome-project

# Set up GitHub integration
fcship github setup setup-workflows my-repo-name

# Create a domain model
fcship domain create User
```

## Command Overview

- `fcship github`: GitHub repository and workflow management
- `fcship project`: Project creation and setup
- `fcship domain`: Domain model generation
- `fcship service`: Service layer generation
- `fcship verify`: Code verification and analysis

For detailed information about each command, please refer to the [Commands](commands/index.md) section.