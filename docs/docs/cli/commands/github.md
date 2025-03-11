# GitHub Integration Commands

The GitHub commands help you interact with GitHub repositories, actions, issues, and pull requests directly from the command line.

## Available Commands

### Repository Management

```bash
# Initialize a new GitHub repository
craftsmanship github init

# Clone a GitHub repository
craftsmanship github clone username/repo

# Fork a GitHub repository
craftsmanship github fork username/repo
```

### GitHub Actions

```bash
# List GitHub Actions workflows
craftsmanship github actions list

# View recent workflow runs
craftsmanship github actions runs

# Create a new GitHub Actions workflow
craftsmanship github actions create python-ci
```

### Pull Requests

```bash
# Create a new pull request
craftsmanship github pr create

# List open pull requests
craftsmanship github pr list

# Checkout a pull request locally
craftsmanship github pr checkout 123
```

### Issues

```bash
# Create a new issue
craftsmanship github issue create

# List open issues
craftsmanship github issue list

# Close an issue
craftsmanship github issue close 456
```

## Authentication

GitHub commands require authentication. You can authenticate using:

```bash
# Set up GitHub authentication
craftsmanship github login
```

This will store your GitHub token securely for future use.

## CI/CD Templates

The GitHub commands provide templates for common CI/CD configurations:

```bash
# Add Python CI/CD workflow
craftsmanship github actions add python-ci

# Add Docker build workflow
craftsmanship github actions add docker-build

# Add custom workflow
craftsmanship github actions add custom --template my-template.yml
```

## Usage Examples

```bash
# Set up a complete GitHub repository with CI/CD
craftsmanship github init
craftsmanship github actions add python-ci

# Create a pull request for current branch
craftsmanship github pr create --title "Add user authentication" --body "Implements #123"
```