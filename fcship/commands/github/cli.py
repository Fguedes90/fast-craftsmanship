"""CLI interface for GitHub commands."""
import typer
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from expression import Result, Ok, Error, effect, tagged_union
from typing import Literal
from fcship.tui.display import DisplayContext, success_message, error_message
from rich.console import Console

from fcship.commands.github.main import (
    list_repositories,
    delete_repository,
    list_branches,
    list_issues, 
    download_issue_body,
    create_pull_request,
    list_pull_requests,
    create_issue,
    create_release,
    Release,
    list_workflow_runs,
    display_workflow_run_details,
    display_workflow_logs,
    rerun_workflow,
    watch_workflow_run
)

@tagged_union
class GithubError:
    """Tagged union for GitHub command errors."""
    tag: Literal["auth_error", "operation_error", "validation_error"]
    auth_error: Optional[str] = None
    operation_error: Optional[str] = None
    validation_error: Optional[str] = None
    
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
    repo_name: Optional[str] = None
    display_ctx: DisplayContext = field(default_factory=lambda: DisplayContext(console=Console()))

@effect.result[str, GithubError]()
def get_github_token() -> Result[str, GithubError]:
    """Get GitHub token from environment variable."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        yield Error(GithubError.AuthError(
            "GITHUB_TOKEN environment variable not set. "
            "Please set it with your GitHub Personal Access Token."
        ))
        return
    
    yield Ok(token)

@effect.result[GithubContext, GithubError]()
def create_github_context(repo_name: Optional[str] = None):
    """Create GitHub context with token and optional repo name."""
    token_result = yield from get_github_token()
    if token_result.is_error():
        yield Error(token_result.error)
        return
    
    yield Ok(GithubContext(
        token=token_result.ok,
        repo_name=repo_name,
        display_ctx=DisplayContext(console=Console())
    ))

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
            yield from error_message(display_ctx, "Unknown Error", "An unknown GitHub error occurred")
    
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
        context_result.ok.token, 
        context_result.ok.repo_name,
        context_result.ok.display_ctx
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
        context_result.ok.token, 
        context_result.ok.repo_name,
        context_result.ok.display_ctx
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
        context_result.ok.display_ctx
    )
    if result.is_error():
        yield Error(result.error)
        return
    
    yield Ok(None)

@effect.result[None, str]()
def github_pr_create(
    repo_name: str, 
    title: str, 
    body: str, 
    head: str, 
    base: str = "main"
):
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
        context_result.ok.display_ctx
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
        context_result.ok.token, 
        context_result.ok.repo_name,
        context_result.ok.display_ctx
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
        context_result.ok.token, 
        context_result.ok.repo_name,
        state,
        context_result.ok.display_ctx
    )
    if result.is_error():
        yield Error(result.error)
        return
    
    yield Ok(None)

@effect.result[None, str]()
def github_issue_create(
    repo_name: str, 
    title: str, 
    body: str, 
    labels: List[str] = None
):
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
        context_result.ok.display_ctx
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
    prerelease: bool = False
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
    
    release = Release(
        tag_name=tag_name,
        name=name,
        body=body,
        draft=draft,
        prerelease=prerelease
    )
    
    result = yield from create_release(
        context_result.ok.token, 
        context_result.ok.repo_name,
        release,
        context_result.ok.display_ctx
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
        context_result.ok.display_ctx
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
        context_result.ok.token, 
        context_result.ok.repo_name,
        run_id,
        context_result.ok.display_ctx
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
        context_result.ok.display_ctx
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
    
    result = yield from rerun_workflow(
        context_result.ok.token, 
        context_result.ok.repo_name,
        run_id
    )
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
        context_result.ok.token, 
        context_result.ok.repo_name,
        run_id,
        context_result.ok.display_ctx
    )
    if result.is_error():
        yield Error(result.error)
        return
    
    yield Ok(None)

# CLI commands
github_app = typer.Typer(name="github", help="GitHub integration commands")
actions_app = typer.Typer(name="actions", help="GitHub Actions debugging commands")

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
    issue_number: int = typer.Argument(..., help="Issue number")
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
    labels: List[str] = typer.Option(None, help="Issue labels (comma-separated)")
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
    state: str = typer.Option("open", help="PR state: open, closed, or all")
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
    base: str = typer.Option("main", help="Base branch name (default: main)")
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
    prerelease: bool = typer.Option(False, help="Mark as pre-release")
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
    confirm: bool = typer.Option(False, "--confirm", help="Confirm deletion")
):
    """Delete a GitHub repository (requires confirmation)."""
    for step in github_repo_delete(repo_name, confirm):
        result = step
    
    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)

# Add the GitHub Actions sub-commands
github_app.add_typer(actions_app)

@actions_app.command("list")
def cli_actions_list(
    repo_name: str = typer.Argument(..., help="Repository name"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of runs to show"),
    branch: str = typer.Option(None, "--branch", "-b", help="Filter by branch"),
    status: str = typer.Option(None, "--status", "-s", help="Filter by status (queued, in_progress, completed, all)")
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
    run_id: int = typer.Argument(..., help="Workflow run ID")
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
    failed_only: bool = typer.Option(True, "--failed-only/--all", help="Show only failed steps logs")
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
    run_id: int = typer.Argument(..., help="Workflow run ID")
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
    run_id: int = typer.Argument(..., help="Workflow run ID")
):
    """Watch a GitHub Actions workflow run in real time."""
    for step in github_actions_watch(repo_name, run_id):
        result = step
    
    if result.is_error():
        typer.echo(f"Error: {result.error}")
        raise typer.Exit(1)