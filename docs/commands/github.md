# GitHub Commands

Fast Craftsmanship provides a comprehensive set of commands for managing GitHub repositories and workflows.

## Overview

The `github` command group allows you to:

- Create and manage GitHub repositories
- Set up CI/CD workflows
- Configure GitHub environments and secrets
- Manage issues and pull requests
- Monitor workflow runs

## Prerequisites

- A GitHub account
- GitHub CLI (`gh`) installed and authenticated
- Appropriate permissions for the repositories you want to manage

## Basic Commands

### List Repositories

```bash
fcship github list
```

Lists all repositories the authenticated user has access to.

### Create Repository

```bash
fcship github create REPO_NAME [--private] [--description "Description"]
```

Creates a new GitHub repository.

| Option | Description |
| ------ | ----------- |
| `--private` | Creates a private repository (default: public) |
| `--description` | Optional description for the repository |
| `--team` | Team that should be granted access to the repository |

### Delete Repository

```bash
fcship github delete REPO_NAME [--confirm]
```

Deletes a GitHub repository.

| Option | Description |
| ------ | ----------- |
| `--confirm` | Skip confirmation prompt |

## Workflow Commands

### Setup Workflows

```bash
fcship github setup setup-workflows REPO_NAME
```

Sets up common CI/CD workflows for the repository, including:

- Continuous Integration workflow (testing, linting)
- Release workflow (build and publish)
- Version bumping workflow

### List Workflow Runs

```bash
fcship github runs list REPO_NAME [--limit NUM] [--workflow NAME]
```

Lists recent workflow runs for a repository.

| Option | Description |
| ------ | ----------- |
| `--limit` | Maximum number of runs to display (default: 10) |
| `--workflow` | Filter by workflow name or ID |

### View Workflow Run

```bash
fcship github runs view REPO_NAME RUN_ID
```

Shows detailed information about a specific workflow run.

### Watch Workflow Run

```bash
fcship github runs watch REPO_NAME RUN_ID
```

Monitors a workflow run in real-time, showing status updates.

## Environment Commands

### Setup Environments

```bash
fcship github setup setup-environments REPO_NAME
```

Creates staging and production environments for the repository.

### Add Secrets

```bash
fcship github setup setup-secrets REPO_NAME SECRET_NAME SECRET_VALUE
```

Adds repository-level secrets for use in GitHub Actions workflows.

## Examples

### Setting up a new project with CI/CD

```bash
# Create repository
fcship github create my-awesome-project --description "My awesome Python project"

# Set up workflows
fcship github setup setup-workflows my-awesome-project

# Set up environments
fcship github setup setup-environments my-awesome-project

# Add PyPI token for publishing
fcship github setup setup-secrets my-awesome-project PYPI_API_TOKEN your-token-value
```

### Monitoring a workflow run

```bash
# List recent workflow runs
fcship github runs list my-awesome-project

# Watch a specific run in real-time
fcship github runs watch my-awesome-project 1234567890
```