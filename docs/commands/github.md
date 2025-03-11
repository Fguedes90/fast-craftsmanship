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
- `GITHUB_TOKEN` environment variable set with a valid Personal Access Token

## Repository Management

### List Repositories

```bash
fcship github repos
```

Lists all repositories the authenticated user has access to.

### Create Repository

```bash
fcship github setup init-repo REPO_NAME [OPTIONS]
```

Creates a new GitHub repository with best practices.

| Option | Description |
| ------ | ----------- |
| `--description TEXT` | Repository description |
| `--private / --no-private` | Creates a private repository (default: public) |
| `--auto-init / --no-auto-init` | Initialize with README, LICENSE, and .gitignore (default: True) |
| `--license-template TEXT` | License template to use (e.g., mit, apache-2.0) (default: mit) |
| `--gitignore-template TEXT` | Gitignore template to use (e.g., Python, Node) (default: Python) |

**Examples:**

Create a basic public repository:
```bash
fcship github setup init-repo my-awesome-project
```

Create a private repository with description:
```bash
fcship github setup init-repo my-private-project --private --description "My private Python project"
```

Create a repository with custom license and gitignore:
```bash
fcship github setup init-repo my-js-project --gitignore-template Node --license-template apache-2.0
```

### Delete Repository

```bash
fcship github repo-delete REPO_NAME [--confirm]
```

Deletes a GitHub repository.

| Option | Description |
| ------ | ----------- |
| `--confirm` | Skip confirmation prompt |

**Example:**
```bash
fcship github repo-delete old-project --confirm
```

## Branch Management

### List Branches

```bash
fcship github branches REPO_NAME
```

Lists all branches in a repository.

**Example:**
```bash
fcship github branches my-awesome-project
```

### Protect Branch

```bash
fcship github setup protect-branch REPO_NAME [BRANCH_NAME] [OPTIONS]
```

Sets up branch protection rules.

| Option | Description |
| ------ | ----------- |
| `BRANCH_NAME` | Name of branch to protect (default: main) |
| `--required-approvals INTEGER` | Number of required approvals for PRs (default: 1) |
| `--require-status-checks / --no-require-status-checks` | Require status checks to pass (default: True) |
| `--require-signed-commits / --no-require-signed-commits` | Require signed commits (default: False) |

**Examples:**

Protect the main branch with default settings:
```bash
fcship github setup protect-branch my-awesome-project
```

Protect a feature branch with custom settings:
```bash
fcship github setup protect-branch my-awesome-project develop --required-approvals 2 --require-signed-commits
```

## Workflow Management

### Setup Workflows

```bash
fcship github setup setup-workflows REPO_NAME [OPTIONS]
```

Sets up common CI/CD workflows for the repository.

| Option | Description |
| ------ | ----------- |
| `--ci / --no-ci` | Set up CI workflow (default: True) |
| `--release / --no-release` | Set up release workflow (default: True) |
| `--version-bump / --no-version-bump` | Set up version bump workflow (default: True) |
| `--deploy / --no-deploy` | Set up deployment workflow (default: False) |
| `--dependabot / --no-dependabot` | Set up Dependabot (default: True) |

**Examples:**

Set up all default workflows:
```bash
fcship github setup setup-workflows my-awesome-project
```

Set up only CI and deployment workflows:
```bash
fcship github setup setup-workflows my-awesome-project --no-release --no-version-bump --deploy
```

### List Workflow Runs

```bash
fcship github actions list REPO_NAME [OPTIONS]
```

Lists recent workflow runs for a repository.

| Option | Description |
| ------ | ----------- |
| `--limit, -n INTEGER` | Maximum number of runs to display (default: 10) |
| `--branch, -b TEXT` | Filter by branch |
| `--status, -s TEXT` | Filter by status (queued, in_progress, completed, all) |

**Examples:**

List the 10 most recent workflow runs:
```bash
fcship github actions list my-awesome-project
```

List workflow runs for a specific branch:
```bash
fcship github actions list my-awesome-project --branch feature/new-feature
```

List only completed workflow runs with a higher limit:
```bash
fcship github actions list my-awesome-project --status completed --limit 20
```

### View Workflow Run Details

```bash
fcship github actions details REPO_NAME RUN_ID
```

Shows detailed information about a specific workflow run.

**Example:**
```bash
fcship github actions details my-awesome-project 1234567890
```

### View Workflow Run Logs

```bash
fcship github actions logs REPO_NAME RUN_ID [OPTIONS]
```

Shows logs for a specific workflow run.

| Option | Description |
| ------ | ----------- |
| `--failed-only / --all` | Show only failed steps logs (default: True) |

**Examples:**

View only failed steps logs:
```bash
fcship github actions logs my-awesome-project 1234567890
```

View all logs:
```bash
fcship github actions logs my-awesome-project 1234567890 --all
```

### Rerun Workflow

```bash
fcship github actions rerun REPO_NAME RUN_ID
```

Reruns a specific workflow run.

**Example:**
```bash
fcship github actions rerun my-awesome-project 1234567890
```

### Watch Workflow Run

```bash
fcship github actions watch REPO_NAME RUN_ID
```

Monitors a workflow run in real-time, showing status updates.

**Example:**
```bash
fcship github actions watch my-awesome-project 1234567890
```

## Environment and Secrets Management

### Setup Environments

```bash
fcship github setup setup-environments REPO_NAME [OPTIONS]
```

Creates deployment environments for the repository.

| Option | Description |
| ------ | ----------- |
| `--environments TEXT` | Environments to set up (default: ["staging", "production"]) |
| `--require-approvals / --no-require-approvals` | Require approvals for deployments (default: True) |

**Examples:**

Set up default environments:
```bash
fcship github setup setup-environments my-awesome-project
```

Set up custom environments without approval requirements:
```bash
fcship github setup setup-environments my-awesome-project --environments dev,test,prod --no-require-approvals
```

### Setup Secrets

```bash
fcship github setup setup-secrets REPO_NAME [OPTIONS]
```

Sets up repository secrets for use in GitHub Actions workflows.

| Option | Description |
| ------ | ----------- |
| `--pypi-token / --no-pypi-token` | Set up PyPI API token secret (default: True) |
| `--sonar-token / --no-sonar-token` | Set up SonarCloud token secret (default: False) |
| `--dockerhub / --no-dockerhub` | Set up DockerHub credentials (default: False) |
| `--gcp / --no-gcp` | Set up Google Cloud Platform credentials (default: False) |
| `--aws / --no-aws` | Set up AWS credentials (default: False) |

**Examples:**

Set up PyPI token (default):
```bash
fcship github setup setup-secrets my-awesome-project
```

Set up multiple credential types:
```bash
fcship github setup setup-secrets my-awesome-project --dockerhub --sonar-token
```

## Issue and Pull Request Management

### List Issues

```bash
fcship github issues REPO_NAME
```

Lists open issues for a repository.

**Example:**
```bash
fcship github issues my-awesome-project
```

### View Issue Details

```bash
fcship github issue REPO_NAME ISSUE_NUMBER
```

Shows detailed information about a specific issue.

**Example:**
```bash
fcship github issue my-awesome-project 42
```

### Create Issue

```bash
fcship github issue-create REPO_NAME [OPTIONS]
```

Creates a new issue in a repository.

| Option | Description |
| ------ | ----------- |
| `--title TEXT` | Issue title [required] |
| `--body TEXT` | Issue body |
| `--labels TEXT` | Issue labels (comma-separated) |

**Examples:**

Create a simple issue:
```bash
fcship github issue-create my-awesome-project --title "Fix login bug"
```

Create an issue with body and labels:
```bash
fcship github issue-create my-awesome-project --title "Improve documentation" --body "We need better examples" --labels documentation,enhancement
```

### List Pull Requests

```bash
fcship github prs REPO_NAME [OPTIONS]
```

Lists pull requests for a repository.

| Option | Description |
| ------ | ----------- |
| `--state TEXT` | PR state: open, closed, or all (default: open) |

**Examples:**

List open pull requests:
```bash
fcship github prs my-awesome-project
```

List all pull requests:
```bash
fcship github prs my-awesome-project --state all
```

### Create Pull Request

```bash
fcship github pr-create REPO_NAME [OPTIONS]
```

Creates a new pull request.

| Option | Description |
| ------ | ----------- |
| `--title TEXT` | Pull request title [required] |
| `--body TEXT` | Pull request body |
| `--head TEXT` | Head branch name [required] |
| `--base TEXT` | Base branch name (default: main) |

**Examples:**

Create a basic pull request:
```bash
fcship github pr-create my-awesome-project --title "Add new feature" --head feature/new-feature
```

Create a detailed pull request to a development branch:
```bash
fcship github pr-create my-awesome-project --title "Fix critical bug" --body "This PR fixes issue #42" --head bugfix/login --base develop
```

## Release Management

### Create Release

```bash
fcship github release REPO_NAME [OPTIONS]
```

Creates a new release for a repository.

| Option | Description |
| ------ | ----------- |
| `--tag-name TEXT` | Tag name for the release [required] |
| `--name TEXT` | Release name/title [required] |
| `--body TEXT` | Release description |
| `--draft / --no-draft` | Create as draft release (default: False) |
| `--prerelease / --no-prerelease` | Mark as pre-release (default: False) |

**Examples:**

Create a standard release:
```bash
fcship github release my-awesome-project --tag-name v1.0.0 --name "Version 1.0.0"
```

Create a pre-release with detailed notes:
```bash
fcship github release my-awesome-project --tag-name v0.9.0 --name "Beta Release" --body "This is a beta release with experimental features" --prerelease
```

Create a draft release:
```bash
fcship github release my-awesome-project --tag-name v1.1.0 --name "Version 1.1.0" --draft
```

## Complete Setup

### Setup All

```bash
fcship github setup setup-all REPO_NAME [OPTIONS]
```

Performs a complete repository setup with best practices.

| Option | Description |
| ------ | ----------- |
| `--description TEXT` | Repository description |
| `--private / --no-private` | Whether the repository should be private (default: False) |
| `--license-template TEXT` | License template to use (default: mit) |
| `--setup-pypi / --no-setup-pypi` | Set up PyPI publishing (default: True) |
| `--setup-docker / --no-setup-docker` | Set up Docker image publishing (default: False) |
| `--deployment-environments TEXT` | Environments to set up (default: ["staging", "production"]) |

**Examples:**

Complete setup with default options:
```bash
fcship github setup setup-all my-awesome-project
```

Complete setup for a private Docker-based project:
```bash
fcship github setup setup-all my-docker-project --private --setup-docker --no-setup-pypi --description "My Docker application"
```

## Workflow Examples

### Setting up a new Python project with CI/CD

```bash
# Create repository
fcship github setup init-repo my-python-project --description "My awesome Python project"

# Set up branch protection
fcship github setup protect-branch my-python-project --required-approvals 1

# Set up workflows
fcship github setup setup-workflows my-python-project

# Set up environments
fcship github setup setup-environments my-python-project

# Add PyPI token for publishing
fcship github setup setup-secrets my-python-project --pypi-token
```

### Setting up a Docker-based project

```bash
# Create repository
fcship github setup init-repo my-docker-app --description "Docker-based application" --gitignore-template Node

# Set up workflows with Docker support
fcship github setup setup-workflows my-docker-app --deploy

# Set up environments with custom names
fcship github setup setup-environments my-docker-app --environments dev,staging,production

# Add Docker Hub credentials
fcship github setup setup-secrets my-docker-app --no-pypi-token --dockerhub
```

### Monitoring and managing workflow runs

```bash
# List recent workflow runs
fcship github actions list my-awesome-project --limit 5

# Get details of a specific run
fcship github actions details my-awesome-project 1234567890

# View logs of failed steps
fcship github actions logs my-awesome-project 1234567890

# Rerun a failed workflow
fcship github actions rerun my-awesome-project 1234567890

# Watch a workflow run in real-time
fcship github actions watch my-awesome-project 1234567890
```