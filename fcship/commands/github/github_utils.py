#!/usr/bin/env python3
"""
GitHub API utilities for repository and CI/CD setup.
"""

import os

from expression import Error, Ok, Result, effect
from github import Github, Repository
from github.GithubException import GithubException

from fcship.tui.input import get_password_input


@effect.result
def get_github_token() -> Result[str, str]:
    """
    Get GitHub token from environment or prompt user.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        yield Ok(token)
        return

    # Ask user for token
    token = yield from get_password_input(
        "GitHub token not found in environment. Please enter your GitHub token: "
    )

    if not token:
        yield Error("GitHub token is required")
        return

    yield Ok(token)
    return


@effect.result
def get_github_client() -> Result[Github, str]:
    """
    Get authenticated GitHub client.
    """
    token_result = yield from get_github_token()
    if token_result.is_error():
        yield Error(token_result.error)
        return

    try:
        client = Github(token_result.value)
        # Test authentication
        _ = client.get_user().login
        yield Ok(client)
        return
    except GithubException as e:
        yield Error(f"GitHub authentication failed: {e!s}")
        return
    except Exception as e:
        yield Error(f"Failed to create GitHub client: {e!s}")
        return


@effect.result
def create_repository(
    name: str,
    description: str = "",
    private: bool = False,
    auto_init: bool = True,
    license_template: str | None = "mit",
    gitignore_template: str | None = "Python",
) -> Result[Repository.Repository, str]:
    """
    Create a new GitHub repository.
    """
    client_result = yield from get_github_client()
    if client_result.is_error():
        yield Error(client_result.error)
        return

    client = client_result.value
    user = client.get_user()

    try:
        repo = user.create_repo(
            name=name,
            description=description,
            private=private,
            auto_init=auto_init,
            license_template=license_template,
            gitignore_template=gitignore_template,
        )
        yield Ok(repo)
        return
    except GithubException as e:
        yield Error(f"Failed to create repository: {e!s}")
        return
    except Exception as e:
        yield Error(f"An error occurred: {e!s}")
        return


@effect.result
def set_branch_protection(
    repo_name: str,
    branch_name: str = "main",
    required_approvals: int = 1,
    require_status_checks: bool = True,
    status_checks: list[str] = None,
    require_signed_commits: bool = False,
) -> Result[str, str]:
    """
    Set branch protection rules.
    """
    client_result = yield from get_github_client()
    if client_result.is_error():
        yield Error(client_result.error)
        return

    client = client_result.value

    try:
        user = client.get_user().login
        repo = client.get_repo(f"{user}/{repo_name}")
        branch = repo.get_branch(branch_name)

        # Configure protection settings
        branch.edit_protection(
            required_approving_review_count=required_approvals,
            enforce_admins=True,
            dismiss_stale_reviews=True,
            require_code_owner_reviews=False,
            required_linear_history=True,
            allow_force_pushes=False,
            allow_deletions=False,
            require_signed_commits=require_signed_commits,
            required_status_checks=status_checks or [],
        )

        yield Ok(f"Branch protection set for {branch_name}")
        return
    except GithubException as e:
        yield Error(f"Failed to set branch protection: {e!s}")
        return
    except Exception as e:
        yield Error(f"An error occurred: {e!s}")
        return


@effect.result
def setup_repository_secret(
    repo_name: str,
    secret_name: str,
    secret_value: str,
) -> Result[str, str]:
    """
    Add a secret to a GitHub repository.
    """
    client_result = yield from get_github_client()
    if client_result.is_error():
        yield Error(client_result.error)
        return

    client = client_result.value

    try:
        user = client.get_user().login
        repo = client.get_repo(f"{user}/{repo_name}")

        # Create or update secret
        repo.create_secret(secret_name, secret_value)

        yield Ok(f"Secret {secret_name} created/updated")
        return
    except GithubException as e:
        yield Error(f"Failed to set secret: {e!s}")
        return
    except Exception as e:
        yield Error(f"An error occurred: {e!s}")
        return


@effect.result
def setup_environment(
    repo_name: str,
    environment_name: str,
    require_approvals: bool = True,
    required_reviewers: list[str] = None,
) -> Result[str, str]:
    """
    Set up a deployment environment.
    """
    client_result = yield from get_github_client()
    if client_result.is_error():
        yield Error(client_result.error)
        return

    client = client_result.value

    try:
        user = client.get_user().login
        repo = client.get_repo(f"{user}/{repo_name}")

        # Create environment
        environment = repo.create_environment(environment_name)

        # Configure environment protection rules
        if require_approvals:
            reviewers = required_reviewers or [user]
            environment.protection_rules.set_required_reviewers(reviewers)

        yield Ok(f"Environment {environment_name} created")
        return
    except GithubException as e:
        yield Error(f"Failed to set up environment: {e!s}")
        return
    except Exception as e:
        yield Error(f"An error occurred: {e!s}")
        return


@effect.result
def create_workflow_file(
    repo_name: str,
    workflow_name: str,
    workflow_content: str,
) -> Result[str, str]:
    """
    Create a GitHub Actions workflow file.
    """
    client_result = yield from get_github_client()
    if client_result.is_error():
        yield Error(client_result.error)
        return

    client = client_result.value

    try:
        user = client.get_user().login
        repo = client.get_repo(f"{user}/{repo_name}")

        # Create workflow file path
        file_path = f".github/workflows/{workflow_name}"

        # Create or update the workflow file
        try:
            # Try to get the file to check if it exists
            existing_file = repo.get_contents(file_path)
            repo.update_file(
                path=file_path,
                message=f"Update {workflow_name} workflow",
                content=workflow_content,
                sha=existing_file.sha,
            )
        except GithubException:
            # File doesn't exist, create it
            repo.create_file(
                path=file_path, message=f"Create {workflow_name} workflow", content=workflow_content
            )

        yield Ok(f"Workflow file {workflow_name} created/updated")
        return
    except GithubException as e:
        yield Error(f"Failed to create workflow file: {e!s}")
        return
    except Exception as e:
        yield Error(f"An error occurred: {e!s}")
        return


@effect.result
def create_dependabot_config(
    repo_name: str,
    package_managers: list[str] = None,
) -> Result[str, str]:
    """
    Create Dependabot configuration file.
    """
    if not package_managers:
        package_managers = ["pip"]

    config_content = """
version: 2
updates:
"""
    for pkg_manager in package_managers:
        config_content += f"""
  - package-ecosystem: "{pkg_manager}"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
"""

    client_result = yield from get_github_client()
    if client_result.is_error():
        yield Error(client_result.error)
        return

    client = client_result.value

    try:
        user = client.get_user().login
        repo = client.get_repo(f"{user}/{repo_name}")

        # Create dependabot config file path
        file_path = ".github/dependabot.yml"

        # Create or update the dependabot config file
        try:
            # Try to get the file to check if it exists
            existing_file = repo.get_contents(file_path)
            repo.update_file(
                path=file_path,
                message="Update dependabot configuration",
                content=config_content,
                sha=existing_file.sha,
            )
        except GithubException:
            # File doesn't exist, create it
            repo.create_file(
                path=file_path, message="Create dependabot configuration", content=config_content
            )

        yield Ok("Dependabot configuration created/updated")
        return
    except GithubException as e:
        yield Error(f"Failed to create dependabot configuration: {e!s}")
        return
    except Exception as e:
        yield Error(f"An error occurred: {e!s}")
        return


@effect.result
def setup_codeql_analysis(
    repo_name: str,
    languages: list[str] = None,
) -> Result[str, str]:
    """
    Set up CodeQL analysis workflow.
    """
    if not languages:
        languages = ["python"]

    languages_str = ", ".join([f"'{lang}'" for lang in languages])

    workflow_content = f"""name: "CodeQL"

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 12 * * 1'

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [{languages_str}]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: ${{{{ matrix.language }}}}

    - name: Autobuild
      uses: github/codeql-action/autobuild@v2

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
"""

    result = yield from create_workflow_file(repo_name, "codeql-analysis.yml", workflow_content)
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok("CodeQL analysis workflow created")
    return


@effect.result
def setup_workflow_templates(repo_name: str) -> Result[dict[str, bool], str]:
    """
    Set up common workflow files from templates.
    """
    result = {
        "ci.yml": False,
        "release.yml": False,
        "bump-version.yml": False,
    }

    # CI workflow
    ci_workflow = """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      - name: Lint with ruff
        run: |
          ruff check .
      - name: Test with pytest
        run: |
          pytest tests/ --cov=. --cov-report=xml
      - name: Upload coverage report
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
"""

    ci_result = yield from create_workflow_file(repo_name, "ci.yml", ci_workflow)
    if ci_result.is_ok():
        result["ci.yml"] = True

    # Release workflow
    release_workflow = """name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
          pip install -e ".[dev]"
      
      - name: Run tests
        run: |
          pytest tests/
      
      - name: Build package
        run: |
          python -m build
      
      - name: Create Release
        id: create_release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            dist/*.whl
            dist/*.tar.gz
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Publish to PyPI
        if: startsWith(github.ref, 'refs/tags/')
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
"""

    release_result = yield from create_workflow_file(repo_name, "release.yml", release_workflow)
    if release_result.is_ok():
        result["release.yml"] = True

    # Version bump workflow
    bump_workflow = """name: Bump Version

on:
  workflow_dispatch:
    inputs:
      version_type:
        description: 'Type of version bump'
        required: true
        default: 'patch'
        type: choice
        options:
          - patch
          - minor
          - major

jobs:
  bump-version:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install python-semantic-release

      - name: Configure Git
        run: |
          git config --global user.name "GitHub Actions Bot"
          git config --global user.email "actions@github.com"
      
      - name: Extract current version
        id: get_version
        run: |
          CURRENT_VERSION=$(grep -m 1 -oP 'version = "\\K[^"]+' pyproject.toml)
          echo "Current version: $CURRENT_VERSION"
          echo "current_version=$CURRENT_VERSION" >> $GITHUB_OUTPUT
      
      - name: Bump version
        id: bump_version
        run: |
          CURRENT_VERSION=${{ steps.get_version.outputs.current_version }}
          
          IFS='.' read -r -a version_parts <<< "$CURRENT_VERSION"
          MAJOR="${version_parts[0]}"
          MINOR="${version_parts[1]}"
          PATCH="${version_parts[2]}"
          
          if [[ "${{ github.event.inputs.version_type }}" == "major" ]]; then
            MAJOR=$((MAJOR + 1))
            MINOR=0
            PATCH=0
          elif [[ "${{ github.event.inputs.version_type }}" == "minor" ]]; then
            MINOR=$((MINOR + 1))
            PATCH=0
          else
            PATCH=$((PATCH + 1))
          fi
          
          NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
          echo "New version: $NEW_VERSION"
          echo "new_version=$NEW_VERSION" >> $GITHUB_OUTPUT
          
          # Update version in pyproject.toml
          sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
      
      - name: Commit and push changes
        run: |
          git add pyproject.toml
          git commit -m "bump: version ${{ steps.bump_version.outputs.new_version }}"
          git push
      
      - name: Create tag
        run: |
          git tag -a "v${{ steps.bump_version.outputs.new_version }}" -m "Release v${{ steps.bump_version.outputs.new_version }}"
          git push --tags
"""

    bump_result = yield from create_workflow_file(repo_name, "bump-version.yml", bump_workflow)
    if bump_result.is_ok():
        result["bump-version.yml"] = True

    yield Ok(result)
    return
