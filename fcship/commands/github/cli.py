"""CLI interface for GitHub commands."""

import os

from dataclasses import dataclass, field
from typing import Literal

import typer

from expression import Error, Ok, Result, effect, tagged_union
from rich.console import Console

from fcship.commands.github.main import (
    Release,
    create_issue,
    create_pull_request,
    create_release,
    delete_repository,
    display_workflow_logs,
    display_workflow_run_details,
    download_issue_body,
    list_branches,
    list_issues,
    list_pull_requests,
    list_repositories,
    list_workflow_runs,
    rerun_workflow,
    watch_workflow_run,
)
from fcship.commands.github.setup import (
    init_repo as setup_init_repo,
)
from fcship.commands.github.setup import (
    protect_branch as setup_protect_branch,
)
from fcship.commands.github.setup import (
    setup_all as setup_all_features,
)
from fcship.commands.github.setup import (
    setup_environments,
    setup_secrets,
    setup_workflows,
)
from fcship.tui.display import DisplayContext, error_message


@tagged_union
class GithubError:
    """Tagged union for GitHub command errors."""

    tag: Literal["auth_error", "operation_error", "validation_error"]
    auth_error: str | None = None
    operation_error: str | None = None
    validation_error: str | None = None

    @staticmethod
    def AuthError(message: str) -> "GithubError":
        """Creates an authentication error."""
        return GithubError(tag="auth_error", auth_error=message)

    @staticmethod
    def OperationError(message: str) -> "GithubError":
        """Creates an operation error."""
        return GithubError(tag="operation_error", operation_error=message)

    @staticmethod
    def ValidationError(message: str) -> "GithubError":
        """Creates a validation error."""
        return GithubError(tag="validation_error", validation_error=message)


@dataclass(frozen=True)
class GithubContext:
    """Immutable context for GitHub operations."""

    token: str
    repo_name: str | None = None
    display_ctx: DisplayContext = field(default_factory=lambda: DisplayContext(console=Console()))


@effect.result[str, GithubError]()
def get_github_token() -> Result[str, GithubError]:
    """Get GitHub token from environment variable."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        yield Error(
            GithubError.AuthError(
                "GITHUB_TOKEN environment variable not set. "
                "Please set it with your GitHub Personal Access Token."
            )
        )
        return

    yield Ok(token)


@effect.result[GithubContext, GithubError]()
def create_github_context(repo_name: str | None = None):
    """Create GitHub context with token and optional repo name."""
    token_result = yield from get_github_token()
    if token_result.is_error():
        yield Error(token_result.error)
        return

    yield Ok(
        GithubContext(
            token=token_result.ok,
            repo_name=repo_name,
            display_ctx=DisplayContext(console=Console()),
        )
    )


@effect.result[str, GithubError]()
def handle_github_error(error: GithubError, ctx: DisplayContext = None):
    """Handle GitHub errors with proper UI feedback."""
    display_ctx = ctx or DisplayContext(console=Console())

    match error:
        case GithubError(tag="auth_error") if error.auth_error is not None:
            yield from error_message(display_ctx, "Authentication Error", error.auth_error)
        case GithubError(tag="operation_error") if error.operation_error is not None:
            yield from error_message(display_ctx, "GitHub Operation Error", error.operation_error)
        case GithubError(tag="validation_error") if error.validation_error is not None:
            yield from error_message(display_ctx, "Validation Error", error.validation_error)
        case _:
            yield from error_message(
                display_ctx, "Unknown Error", "An unknown GitHub error occurred"
            )

    yield Error(error)


@effect.result[None, str]()
def github_repos():
    """List GitHub repositories for the authenticated user."""
    context_result = yield from create_github_context()
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    result = yield from list_repositories(context_result.ok.token, context_result.ok.display_ctx)
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(None)


@effect.result[None, str]()
def github_branches(repo_name: str):
    """List branches for a GitHub repository."""
    if not repo_name:
        yield Error("Repository name is required")
        return

    context_result = yield from create_github_context(repo_name)
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    result = yield from list_branches(
        context_result.ok.token, context_result.ok.repo_name, context_result.ok.display_ctx
    )
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(None)


@effect.result[None, str]()
def github_issues(repo_name: str):
    """List issues for a GitHub repository."""
    if not repo_name:
        yield Error("Repository name is required")
        return

    context_result = yield from create_github_context(repo_name)
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    result = yield from list_issues(
        context_result.ok.token, context_result.ok.repo_name, context_result.ok.display_ctx
    )
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(None)


@effect.result[None, str]()
def github_issue(repo_name: str, issue_number: int):
    """Get details of a specific GitHub issue."""
    if not repo_name:
        yield Error("Repository name is required")
        return

    if issue_number <= 0:
        yield Error("Issue number must be positive")
        return

    context_result = yield from create_github_context(repo_name)
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    result = yield from download_issue_body(
        context_result.ok.token,
        context_result.ok.repo_name,
        issue_number,
        context_result.ok.display_ctx,
    )
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(None)


@effect.result[None, str]()
def github_pr_create(repo_name: str, title: str, body: str, head: str, base: str = "main"):
    """Create a pull request on GitHub."""
    if not repo_name:
        yield Error("Repository name is required")
        return

    if not title:
        yield Error("Pull request title is required")
        return

    if not head:
        yield Error("Head branch is required")
        return

    context_result = yield from create_github_context(repo_name)
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    result = yield from create_pull_request(
        context_result.ok.token,
        context_result.ok.repo_name,
        title,
        body,
        head,
        base,
        context_result.ok.display_ctx,
    )
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(None)


@effect.result[None, str]()
def github_repo_delete(repo_name: str, confirm: bool = False):
    """Delete a GitHub repository."""
    if not repo_name:
        yield Error("Repository name is required")
        return

    if not confirm:
        yield Error("Please confirm deletion with --confirm flag")
        return

    context_result = yield from create_github_context(repo_name)
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    result = yield from delete_repository(
        context_result.ok.token, context_result.ok.repo_name, context_result.ok.display_ctx
    )
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(None)


# Additional function implementations for the new GitHub features
@effect.result[None, str]()
def github_prs(repo_name: str, state: str = "open"):
    """List pull requests for a GitHub repository."""
    if not repo_name:
        yield Error("Repository name is required")
        return

    if state not in ["open", "closed", "all"]:
        yield Error("State must be one of: open, closed, all")
        return

    context_result = yield from create_github_context(repo_name)
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    result = yield from list_pull_requests(
        context_result.ok.token, context_result.ok.repo_name, state, context_result.ok.display_ctx
    )
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(None)


@effect.result[None, str]()
def github_issue_create(repo_name: str, title: str, body: str, labels: list[str] = None):
    """Create an issue on GitHub."""
    if not repo_name:
        yield Error("Repository name is required")
        return

    if not title:
        yield Error("Issue title is required")
        return

    context_result = yield from create_github_context(repo_name)
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    result = yield from create_issue(
        context_result.ok.token,
        context_result.ok.repo_name,
        title,
        body,
        labels,
        context_result.ok.display_ctx,
    )
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(None)


@effect.result[None, str]()
def github_release_create(
    repo_name: str,
    tag_name: str,
    name: str,
    body: str,
    draft: bool = False,
    prerelease: bool = False,
):
    """Create a release on GitHub."""
    if not repo_name:
        yield Error("Repository name is required")
        return

    if not tag_name:
        yield Error("Tag name is required")
        return

    if not name:
        yield Error("Release name is required")
        return

    context_result = yield from create_github_context(repo_name)
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    release = Release(tag_name=tag_name, name=name, body=body, draft=draft, prerelease=prerelease)

    result = yield from create_release(
        context_result.ok.token, context_result.ok.repo_name, release, context_result.ok.display_ctx
    )
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(None)


# Additional function implementations for GitHub Actions debugging
@effect.result[None, str]()
def github_actions_list(repo_name: str, limit: int = 10, branch: str = None, status: str = None):
    """List GitHub Actions workflow runs."""
    if not repo_name:
        yield Error("Repository name is required")
        return

    context_result = yield from create_github_context(repo_name)
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    result = yield from list_workflow_runs(
        context_result.ok.token,
        context_result.ok.repo_name,
        limit,
        branch,
        status,
        context_result.ok.display_ctx,
    )
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(None)


@effect.result[None, str]()
def github_actions_details(repo_name: str, run_id: int):
    """Show details about a specific GitHub Actions workflow run."""
    if not repo_name:
        yield Error("Repository name is required")
        return

    if run_id <= 0:
        yield Error("Run ID must be positive")
        return

    context_result = yield from create_github_context(repo_name)
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    result = yield from display_workflow_run_details(
        context_result.ok.token, context_result.ok.repo_name, run_id, context_result.ok.display_ctx
    )
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(None)


@effect.result[None, str]()
def github_actions_logs(repo_name: str, run_id: int, failed_only: bool = True):
    """Show logs for a GitHub Actions workflow run."""
    if not repo_name:
        yield Error("Repository name is required")
        return

    if run_id <= 0:
        yield Error("Run ID must be positive")
        return

    context_result = yield from create_github_context(repo_name)
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    result = yield from display_workflow_logs(
        context_result.ok.token,
        context_result.ok.repo_name,
        run_id,
        failed_only,
        context_result.ok.display_ctx,
    )
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(None)


@effect.result[None, str]()
def github_actions_rerun(repo_name: str, run_id: int):
    """Rerun a specific GitHub Actions workflow run."""
    if not repo_name:
        yield Error("Repository name is required")
        return

    if run_id <= 0:
        yield Error("Run ID must be positive")
        return

    context_result = yield from create_github_context(repo_name)
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    result = yield from rerun_workflow(context_result.ok.token, context_result.ok.repo_name, run_id)
    if result.is_error():
        yield Error(result.error)
        return

    console = context_result.ok.display_ctx.console
    console.print(f"[green]{result.ok}[/green]")
    yield Ok(None)


@effect.result[None, str]()
def github_actions_watch(repo_name: str, run_id: int):
    """Watch a GitHub Actions workflow run in real-time."""
    if not repo_name:
        yield Error("Repository name is required")
        return

    if run_id <= 0:
        yield Error("Run ID must be positive")
        return

    context_result = yield from create_github_context(repo_name)
    if context_result.is_error():
        yield from handle_github_error(context_result.error)
        return

    result = yield from watch_workflow_run(
        context_result.ok.token, context_result.ok.repo_name, run_id, context_result.ok.display_ctx
    )
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(None)


# CLI commands
github_app = typer.Typer(name="github", help="GitHub integration commands")
actions_app = typer.Typer(name="actions", help="GitHub Actions debugging commands")
setup_app = typer.Typer(name="setup", help="GitHub repository setup commands")


@github_app.command("repos")
def cli_github_repos():
    """List all your GitHub repositories."""
    for step in github_repos():
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@github_app.command("branches")
def cli_github_branches(repo_name: str = typer.Argument(..., help="Repository name")):
    """List branches in a GitHub repository."""
    for step in github_branches(repo_name):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@github_app.command("issues")
def cli_github_issues(repo_name: str = typer.Argument(..., help="Repository name")):
    """List open issues in a GitHub repository."""
    for step in github_issues(repo_name):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@github_app.command("issue")
def cli_github_issue(
    repo_name: str = typer.Argument(..., help="Repository name"),
    issue_number: int = typer.Argument(..., help="Issue number"),
):
    """View a specific GitHub issue."""
    for step in github_issue(repo_name, issue_number):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@github_app.command("issue-create")
def cli_github_issue_create(
    repo_name: str = typer.Argument(..., help="Repository name"),
    title: str = typer.Option(..., help="Issue title"),
    body: str = typer.Option("", help="Issue body"),
    labels: list[str] = typer.Option(None, help="Issue labels (comma-separated)"),
):
    """Create an issue on GitHub."""
    for step in github_issue_create(repo_name, title, body, labels):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@github_app.command("prs")
def cli_github_prs(
    repo_name: str = typer.Argument(..., help="Repository name"),
    state: str = typer.Option("open", help="PR state: open, closed, or all"),
):
    """List pull requests in a GitHub repository."""
    for step in github_prs(repo_name, state):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@github_app.command("pr-create")
def cli_github_pr_create(
    repo_name: str = typer.Argument(..., help="Repository name"),
    title: str = typer.Option(..., help="Pull request title"),
    body: str = typer.Option("", help="Pull request body"),
    head: str = typer.Option(..., help="Head branch name"),
    base: str = typer.Option("main", help="Base branch name (default: main)"),
):
    """Create a pull request on GitHub."""
    for step in github_pr_create(repo_name, title, body, head, base):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@github_app.command("release")
def cli_github_release(
    repo_name: str = typer.Argument(..., help="Repository name"),
    tag_name: str = typer.Option(..., help="Tag name for the release"),
    name: str = typer.Option(..., help="Release name/title"),
    body: str = typer.Option("", help="Release description"),
    draft: bool = typer.Option(False, help="Create as draft release"),
    prerelease: bool = typer.Option(False, help="Mark as pre-release"),
):
    """Create a GitHub release."""
    for step in github_release_create(repo_name, tag_name, name, body, draft, prerelease):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@github_app.command("repo-delete")
def cli_github_repo_delete(
    repo_name: str = typer.Argument(..., help="Repository name to delete"),
    confirm: bool = typer.Option(False, "--confirm", help="Confirm deletion"),
):
    """Delete a GitHub repository (requires confirmation)."""
    for step in github_repo_delete(repo_name, confirm):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


# Add the GitHub Actions and setup sub-commands
github_app.add_typer(actions_app)
github_app.add_typer(setup_app)


@actions_app.command("list")
def cli_actions_list(
    repo_name: str = typer.Argument(..., help="Repository name"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of runs to show"),
    branch: str = typer.Option(None, "--branch", "-b", help="Filter by branch"),
    status: str = typer.Option(
        None, "--status", "-s", help="Filter by status (queued, in_progress, completed, all)"
    ),
):
    """List recent GitHub Actions workflow runs."""
    for step in github_actions_list(repo_name, limit, branch, status):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@actions_app.command("details")
def cli_actions_details(
    repo_name: str = typer.Argument(..., help="Repository name"),
    run_id: int = typer.Argument(..., help="Workflow run ID"),
):
    """Show details about a GitHub Actions workflow run."""
    for step in github_actions_details(repo_name, run_id):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@actions_app.command("logs")
def cli_actions_logs(
    repo_name: str = typer.Argument(..., help="Repository name"),
    run_id: int = typer.Argument(..., help="Workflow run ID"),
    failed_only: bool = typer.Option(
        True, "--failed-only/--all", help="Show only failed steps logs"
    ),
):
    """Display logs for a GitHub Actions workflow run."""
    for step in github_actions_logs(repo_name, run_id, failed_only):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@actions_app.command("rerun")
def cli_actions_rerun(
    repo_name: str = typer.Argument(..., help="Repository name"),
    run_id: int = typer.Argument(..., help="Workflow run ID"),
):
    """Rerun a GitHub Actions workflow."""
    for step in github_actions_rerun(repo_name, run_id):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@actions_app.command("watch")
def cli_actions_watch(
    repo_name: str = typer.Argument(..., help="Repository name"),
    run_id: int = typer.Argument(..., help="Workflow run ID"),
):
    """Watch a GitHub Actions workflow run in real time."""
    for step in github_actions_watch(repo_name, run_id):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


# Setup commands
@setup_app.command("init-repo")
def cli_setup_init_repo(
    repo_name: str = typer.Argument(..., help="Name of the repository to create"),
    description: str = typer.Option("", help="Repository description"),
    private: bool = typer.Option(False, help="Whether the repository should be private"),
    auto_init: bool = typer.Option(True, help="Initialize with README, LICENSE, and .gitignore"),
    license_template: str | None = typer.Option(
        "mit", help="License template to use (e.g., mit, apache-2.0)"
    ),
    gitignore_template: str | None = typer.Option(
        "Python", help="Gitignore template to use (e.g., Python, Node)"
    ),
):
    """Create a new GitHub repository with best practices."""
    for step in setup_init_repo(
        repo_name, description, private, auto_init, license_template, gitignore_template
    ):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@setup_app.command("protect-branch")
def cli_setup_protect_branch(
    repo_name: str = typer.Argument(..., help="Name of the repository"),
    branch_name: str = typer.Argument("main", help="Name of branch to protect"),
    required_approvals: int = typer.Option(1, help="Number of required approvals for PRs"),
    require_status_checks: bool = typer.Option(True, help="Require status checks to pass"),
    require_signed_commits: bool = typer.Option(False, help="Require signed commits"),
):
    """Set up branch protection rules."""
    for step in setup_protect_branch(
        repo_name, branch_name, required_approvals, require_status_checks, require_signed_commits
    ):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@setup_app.command("setup-secrets")
def cli_setup_secrets(
    repo_name: str = typer.Argument(..., help="Name of the repository"),
    pypi_token: bool = typer.Option(True, help="Set up PyPI API token secret"),
    sonar_token: bool = typer.Option(False, help="Set up SonarCloud token secret"),
    dockerhub: bool = typer.Option(False, help="Set up DockerHub credentials"),
    gcp: bool = typer.Option(False, help="Set up Google Cloud Platform credentials"),
    aws: bool = typer.Option(False, help="Set up AWS credentials"),
):
    """Set up GitHub secrets for CI/CD."""
    for step in setup_secrets(repo_name, pypi_token, sonar_token, dockerhub, gcp, aws):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@setup_app.command("setup-environments")
def cli_setup_environments(
    repo_name: str = typer.Argument(..., help="Name of the repository"),
    environments: list[str] = typer.Option(
        ["staging", "production"], help="Environments to set up"
    ),
    require_approvals: bool = typer.Option(True, help="Require approvals for deployments"),
):
    """Set up GitHub environments for deployments."""
    for step in setup_environments(repo_name, environments, require_approvals):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@setup_app.command("setup-workflows")
def cli_setup_workflows(
    repo_name: str = typer.Argument(..., help="Name of the repository"),
    ci: bool = typer.Option(True, help="Set up CI workflow"),
    release: bool = typer.Option(True, help="Set up release workflow"),
    version_bump: bool = typer.Option(True, help="Set up version bump workflow"),
    deploy: bool = typer.Option(False, help="Set up deployment workflow"),
    codeql: bool = typer.Option(False, help="Set up CodeQL analysis"),
    dependabot: bool = typer.Option(True, help="Set up Dependabot"),
):
    """Set up GitHub Actions workflows."""
    for step in setup_workflows(repo_name, ci, release, version_bump, deploy, codeql, dependabot):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)


@setup_app.command("setup-all")
def cli_setup_all(
    repo_name: str = typer.Argument(..., help="Name of the repository to set up"),
    description: str = typer.Option("", help="Repository description"),
    private: bool = typer.Option(False, help="Whether the repository should be private"),
    license_template: str | None = typer.Option(
        "mit", help="License template to use (e.g., mit, apache-2.0)"
    ),
    setup_pypi: bool = typer.Option(True, help="Set up PyPI publishing"),
    setup_docker: bool = typer.Option(False, help="Set up Docker image publishing"),
    deployment_environments: list[str] = typer.Option(
        ["staging", "production"], help="Environments to set up"
    ),
):
    """Complete GitHub repository setup with best practices."""
    for step in setup_all_features(
        repo_name,
        description,
        private,
        license_template,
        setup_pypi,
        setup_docker,
        deployment_environments,
    ):
        result = step

    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)
