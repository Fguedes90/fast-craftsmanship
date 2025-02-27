import re
import time

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from expression import Error, Ok, effect
from github import Github
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

from fcship.tui.display import (
    DisplayContext,
    display_rule,
    error_message,
    success_message,
    warning_message,
)
from fcship.tui.tables import create_multi_column_table, display_table


@effect.result[None, str]()
def list_repositories(token: str, display_ctx: DisplayContext = None):
    """Lists all repositories for the authenticated user in a formatted table."""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())

    try:
        g = Github(token)
        user = g.get_user()

        # Display header
        yield from display_rule(display_ctx, "GitHub Repositories")

        # Prepare table data
        headers = ["Name", "Description", "Stars", "Language", "Private"]
        rows = []

        for repo in user.get_repos():
            rows.append(
                [
                    repo.name,
                    repo.description or "",
                    str(repo.stargazers_count),
                    repo.language or "N/A",
                    "Yes" if repo.private else "No",
                ]
            )

        # Create and display table
        table_result = yield from create_multi_column_table("Your Repositories", headers, rows)
        if table_result.is_ok():
            yield from display_table(table_result.ok)
            yield from success_message(display_ctx, f"Found {len(rows)} repositories")
        else:
            yield from error_message(display_ctx, "Failed to create repository table")

    except Exception as e:
        yield from error_message(display_ctx, "Error listing repositories", details=str(e))
        return Error(str(e))

    return Ok(None)


@effect.result[None, str]()
def delete_repository(token: str, repo_name: str, display_ctx: DisplayContext = None):
    """Deletes a repository if the name matches exactly."""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())

    try:
        g = Github(token)
        user = g.get_user()

        yield from warning_message(display_ctx, f"Attempting to delete repository '{repo_name}'")

        try:
            repo = user.get_repo(repo_name)
            repo.delete()
            yield from success_message(
                display_ctx, f"Repository '{repo_name}' deleted successfully"
            )
        except Exception as e:
            yield from error_message(
                display_ctx, f"Error deleting repository '{repo_name}'", details=str(e)
            )
            return Error(str(e))

    except Exception as e:
        yield from error_message(display_ctx, "Failed to initialize GitHub client", details=str(e))
        return Error(str(e))

    return Ok(None)


@effect.result[None, str]()
def list_branches(token: str, repo_name: str, display_ctx: DisplayContext = None):
    """Lists all branches of a given repository in a formatted table."""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())

    try:
        g = Github(token)
        user = g.get_user()

        try:
            repo = user.get_repo(repo_name)

            # Display header
            yield from display_rule(display_ctx, f"Branches in {repo_name}")

            # Prepare table data
            headers = ["Branch Name", "Last Commit", "Protected"]
            rows = []

            for branch in repo.get_branches():
                rows.append(
                    [branch.name, branch.commit.sha[:7], "Yes" if branch.protected else "No"]
                )

            # Create and display table
            table_result = yield from create_multi_column_table(
                f"Branches in {repo_name}", headers, rows
            )
            if table_result.is_ok():
                yield from display_table(table_result.ok)
                yield from success_message(display_ctx, f"Found {len(rows)} branches")
            else:
                yield from error_message(display_ctx, "Failed to create branch table")

        except Exception as e:
            yield from error_message(
                display_ctx, f"Error listing branches for repository '{repo_name}'", details=str(e)
            )
            return Error(str(e))

    except Exception as e:
        yield from error_message(display_ctx, "Failed to initialize GitHub client", details=str(e))
        return Error(str(e))

    return Ok(None)


@effect.result[None, str]()
def list_issues(token: str, repo_name: str, display_ctx: DisplayContext = None):
    """Lists all open issues of a given repository in a formatted table."""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())

    try:
        g = Github(token)
        user = g.get_user()

        try:
            repo = user.get_repo(repo_name)

            # Display header
            yield from display_rule(display_ctx, f"Open Issues in {repo_name}")

            # Prepare table data
            headers = ["Number", "Title", "Author", "Labels", "Comments"]
            rows = []

            for issue in repo.get_issues(state="open"):
                labels = ", ".join([label.name for label in issue.labels]) or "None"
                rows.append(
                    [f"#{issue.number}", issue.title, issue.user.login, labels, str(issue.comments)]
                )

            # Create and display table
            table_result = yield from create_multi_column_table(
                f"Open Issues in {repo_name}", headers, rows
            )
            if table_result.is_ok():
                yield from display_table(table_result.ok)
                yield from success_message(display_ctx, f"Found {len(rows)} open issues")
            else:
                yield from error_message(display_ctx, "Failed to create issues table")

        except Exception as e:
            yield from error_message(
                display_ctx, f"Error listing issues for repository '{repo_name}'", details=str(e)
            )
            return Error(str(e))

    except Exception as e:
        yield from error_message(display_ctx, "Failed to initialize GitHub client", details=str(e))
        return Error(str(e))

    return Ok(None)


@effect.result[None, str]()
def download_issue_body(
    token: str, repo_name: str, issue_number: int, display_ctx: DisplayContext = None
):
    """Downloads and displays the body of a specific issue from a given repository."""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())

    try:
        g = Github(token)
        user = g.get_user()

        try:
            repo = user.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)

            # Display header
            yield from display_rule(display_ctx, f"Issue #{issue_number} from {repo_name}")

            # Display issue details
            yield from success_message(display_ctx, f"Title: {issue.title}")
            yield from success_message(display_ctx, f"Author: {issue.user.login}")
            yield from success_message(display_ctx, f"Created: {issue.created_at}")
            yield from success_message(display_ctx, f"Status: {issue.state}")

            # Display issue body
            yield from display_rule(display_ctx, "Issue Body")
            if issue.body:
                yield from success_message(display_ctx, issue.body)
            else:
                yield from warning_message(display_ctx, "No description provided")

        except Exception as e:
            yield from error_message(
                display_ctx,
                f"Error downloading issue #{issue_number} from repository '{repo_name}'",
                details=str(e),
            )
            return Error(str(e))

    except Exception as e:
        yield from error_message(display_ctx, "Failed to initialize GitHub client", details=str(e))
        return Error(str(e))

    return Ok(None)


@effect.result[None, str]()
def create_pull_request(
    token: str,
    repo_name: str,
    title: str,
    body: str,
    head: str,
    base: str,
    display_ctx: DisplayContext = None,
):
    """Creates a pull request in a given repository with visual feedback."""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())

    try:
        g = Github(token)
        user = g.get_user()

        try:
            repo = user.get_repo(repo_name)

            # Display header
            yield from display_rule(display_ctx, f"Creating Pull Request in {repo_name}")

            # Show PR details before creation
            yield from success_message(display_ctx, f"Title: {title}")
            yield from success_message(display_ctx, f"From: {head} → {base}")

            # Create PR
            pull = repo.create_pull(title=title, body=body, head=head, base=base)

            # Display success message with PR details
            yield from success_message(display_ctx, "Pull request created successfully!")
            yield from success_message(display_ctx, f"PR #{pull.number}: {pull.html_url}")

        except Exception as e:
            yield from error_message(
                display_ctx,
                f"Error creating pull request in repository '{repo_name}'",
                details=str(e),
            )
            return Error(str(e))

    except Exception as e:
        yield from error_message(display_ctx, "Failed to initialize GitHub client", details=str(e))
        return Error(str(e))

    return Ok(None)


@dataclass(frozen=True)
class Release:
    """Immutable container for GitHub release information"""

    tag_name: str
    name: str
    body: str
    draft: bool = False
    prerelease: bool = False


@effect.result[None, str]()
def create_release(
    token: str, repo_name: str, release: Release, display_ctx: DisplayContext = None
):
    """Creates a new release for a repository"""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())

    try:
        g = Github(token)
        user = g.get_user()

        try:
            repo = user.get_repo(repo_name)

            # Display header
            yield from display_rule(display_ctx, f"Creating Release for {repo_name}")

            # Show release details
            yield from success_message(display_ctx, f"Tag: {release.tag_name}")
            yield from success_message(display_ctx, f"Name: {release.name}")

            # Create release
            github_release = repo.create_git_release(
                tag=release.tag_name,
                name=release.name,
                message=release.body,
                draft=release.draft,
                prerelease=release.prerelease,
            )

            # Display success message
            yield from success_message(display_ctx, "Release created successfully!")
            yield from success_message(display_ctx, f"Release URL: {github_release.html_url}")

        except Exception as e:
            yield from error_message(
                display_ctx, f"Error creating release for repository '{repo_name}'", details=str(e)
            )
            return Error(str(e))

    except Exception as e:
        yield from error_message(display_ctx, "Failed to initialize GitHub client", details=str(e))
        return Error(str(e))

    return Ok(None)


@effect.result[None, str]()
def list_pull_requests(
    token: str, repo_name: str, state: str = "open", display_ctx: DisplayContext = None
):
    """Lists all pull requests of a given repository in a formatted table."""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())

    try:
        g = Github(token)
        user = g.get_user()

        try:
            repo = user.get_repo(repo_name)

            # Display header
            state_display = state.capitalize()
            yield from display_rule(display_ctx, f"{state_display} Pull Requests in {repo_name}")

            # Prepare table data
            headers = ["Number", "Title", "Author", "Base → Head", "Comments"]
            rows = []

            for pr in repo.get_pulls(state=state):
                rows.append(
                    [
                        f"#{pr.number}",
                        pr.title,
                        pr.user.login,
                        f"{pr.base.ref} ← {pr.head.ref}",
                        str(pr.comments),
                    ]
                )

            # Create and display table
            table_result = yield from create_multi_column_table(
                f"{state_display} Pull Requests in {repo_name}", headers, rows
            )
            if table_result.is_ok():
                yield from display_table(table_result.ok)
                yield from success_message(display_ctx, f"Found {len(rows)} {state} pull requests")
            else:
                yield from error_message(display_ctx, "Failed to create pull requests table")

        except Exception as e:
            yield from error_message(
                display_ctx,
                f"Error listing pull requests for repository '{repo_name}'",
                details=str(e),
            )
            return Error(str(e))

    except Exception as e:
        yield from error_message(display_ctx, "Failed to initialize GitHub client", details=str(e))
        return Error(str(e))

    return Ok(None)


@effect.result[None, str]()
def create_issue(
    token: str,
    repo_name: str,
    title: str,
    body: str,
    labels: list[str] = None,
    display_ctx: DisplayContext = None,
):
    """Creates a new issue in a repository"""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())

    try:
        g = Github(token)
        user = g.get_user()

        try:
            repo = user.get_repo(repo_name)

            # Display header
            yield from display_rule(display_ctx, f"Creating Issue for {repo_name}")

            # Show issue details
            yield from success_message(display_ctx, f"Title: {title}")
            if labels:
                yield from success_message(display_ctx, f"Labels: {', '.join(labels)}")

            # Create issue
            issue = repo.create_issue(title=title, body=body, labels=labels)

            # Display success message
            yield from success_message(display_ctx, "Issue created successfully!")
            yield from success_message(display_ctx, f"Issue #{issue.number}: {issue.html_url}")

        except Exception as e:
            yield from error_message(
                display_ctx, f"Error creating issue for repository '{repo_name}'", details=str(e)
            )
            return Error(str(e))

    except Exception as e:
        yield from error_message(display_ctx, "Failed to initialize GitHub client", details=str(e))
        return Error(str(e))

    return Ok(None)


# GitHub Actions - Debugging Functions


@dataclass(frozen=True)
class WorkflowRunSummary:
    """Immutable container for workflow run summary information"""

    id: int
    name: str
    status: str
    conclusion: str
    created_at: datetime
    updated_at: datetime
    url: str
    head_branch: str
    head_sha: str
    run_number: int
    event: str


def format_time_ago(dt: datetime) -> str:
    """Format a datetime as a relative time (e.g., '2 hours ago')"""
    now = datetime.now(UTC)
    delta = now - dt

    if delta.days > 0:
        return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
    hours = delta.seconds // 3600
    if hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    minutes = (delta.seconds % 3600) // 60
    if minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    return "just now"


@effect.result[list[WorkflowRunSummary], str]()
def get_recent_workflow_runs(
    token: str, repo_name: str, limit: int = 10, branch: str = None, status: str = None
):
    """Get recent workflow runs for a repository"""
    try:
        g = Github(token)
        user = g.get_user()
        repo = user.get_repo(repo_name)

        # Filter parameters
        params = {}
        if branch:
            params["branch"] = branch
        if status and status != "all":
            params["status"] = status

        # Get workflow runs
        runs = list(repo.get_workflow_runs(**params))
        runs.sort(key=lambda x: x.created_at, reverse=True)

        # Limit the number of runs
        runs = runs[:limit]

        # Convert to summary objects
        summaries = [
            WorkflowRunSummary(
                id=run.id,
                name=run.name,
                status=run.status,
                conclusion=run.conclusion or "pending",
                created_at=run.created_at,
                updated_at=run.updated_at,
                url=run.html_url,
                head_branch=run.head_branch,
                head_sha=run.head_sha[:7],
                run_number=run.run_number,
                event=run.event,
            )
            for run in runs
        ]

        yield Ok(summaries)
    except Exception as e:
        yield Error(f"Failed to get workflow runs: {e!s}")


@effect.result[None, str]()
def list_workflow_runs(
    token: str,
    repo_name: str,
    limit: int = 10,
    branch: str = None,
    status: str = None,
    display_ctx: DisplayContext = None,
):
    """Lists workflow runs for a repository in a formatted table"""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())

    try:
        # Display header
        status_display = status or "all"
        branch_display = f" on branch '{branch}'" if branch else ""
        yield from display_rule(
            display_ctx, f"GitHub Actions Workflow Runs for {repo_name}{branch_display}"
        )

        # Get workflow runs
        runs_result = yield from get_recent_workflow_runs(token, repo_name, limit, branch, status)
        if runs_result.is_error():
            yield from error_message(display_ctx, "Failed to get workflow runs", runs_result.error)
            return Error(runs_result.error)

        runs = runs_result.ok

        if not runs:
            yield from warning_message(display_ctx, f"No {status_display} workflow runs found")
            return Ok(None)

        # Prepare table data
        headers = ["Run #", "Workflow", "Branch", "Status", "Started", "Trigger"]
        rows = []

        # Status emoji mapping
        status_icons = {
            "success": "✅",
            "completed": "✅",
            "failure": "❌",
            "cancelled": "⚪",
            "skipped": "⏭️",
            "in_progress": "⏳",
            "queued": "🔄",
            "pending": "⏱️",
            "waiting": "⌛",
            "requested": "🔍",
        }

        for run in runs:
            # Status with color and emoji
            status_display = run.conclusion if run.status == "completed" else run.status
            status_icon = status_icons.get(status_display.lower(), "❓")
            status_with_icon = f"{status_icon} {status_display}"

            # Time ago
            time_ago = format_time_ago(run.created_at)

            # Event trigger
            event = run.event.replace("_", " ").title()

            rows.append(
                [f"#{run.run_number}", run.name, run.head_branch, status_with_icon, time_ago, event]
            )

        # Create and display table
        table_result = yield from create_multi_column_table("Recent Workflow Runs", headers, rows)
        if table_result.is_ok():
            yield from display_table(table_result.ok)
            yield from success_message(display_ctx, f"Showing {len(rows)} recent workflow runs")
        else:
            yield from error_message(display_ctx, "Failed to create workflow runs table")

    except Exception as e:
        yield from error_message(display_ctx, "Failed to list workflow runs", details=str(e))
        return Error(str(e))

    return Ok(None)


@effect.result[dict[str, Any], str]()
def get_workflow_run_details(token: str, repo_name: str, run_id: int):
    """Get detailed information about a specific workflow run"""
    try:
        g = Github(token)
        user = g.get_user()
        repo = user.get_repo(repo_name)

        # Get workflow run
        run = repo.get_workflow_run(run_id)

        # Build workflow jobs dictionary
        jobs = []
        for job in run.jobs():
            job_dict = {
                "name": job.name,
                "id": job.id,
                "status": job.status,
                "conclusion": job.conclusion,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "url": job.html_url,
                "steps": [],
            }

            # Process steps
            if hasattr(job, "steps") and job.steps:
                for step in job.steps:
                    step_dict = {
                        "name": step.name,
                        "status": step.status,
                        "conclusion": step.conclusion,
                        "number": step.number,
                    }
                    job_dict["steps"].append(step_dict)

            jobs.append(job_dict)

        # Build workflow run dictionary
        run_dict = {
            "id": run.id,
            "name": run.name,
            "status": run.status,
            "conclusion": run.conclusion,
            "created_at": run.created_at,
            "updated_at": run.updated_at,
            "url": run.html_url,
            "head_branch": run.head_branch,
            "head_sha": run.head_sha,
            "run_number": run.run_number,
            "event": run.event,
            "jobs": jobs,
            "raw_run": run,
        }

        yield Ok(run_dict)
    except Exception as e:
        yield Error(f"Failed to get workflow run details: {e!s}")


@effect.result[None, str]()
def display_workflow_run_details(
    token: str, repo_name: str, run_id: int, display_ctx: DisplayContext = None
):
    """Display detailed information about a specific workflow run"""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())

    try:
        # Display header
        yield from display_rule(display_ctx, f"GitHub Actions Workflow Run #{run_id} Details")

        # Get workflow run details
        run_result = yield from get_workflow_run_details(token, repo_name, run_id)
        if run_result.is_error():
            yield from error_message(
                display_ctx, "Failed to get workflow run details", run_result.error
            )
            return Error(run_result.error)

        run = run_result.ok

        # Show workflow run summary
        yield from success_message(display_ctx, f"Workflow: {run['name']}")
        yield from success_message(
            display_ctx, f"Status: {run['status']} / Conclusion: {run['conclusion'] or 'pending'}"
        )
        yield from success_message(
            display_ctx, f"Branch: {run['head_branch']} ({run['head_sha'][:7]})"
        )
        yield from success_message(
            display_ctx, f"Triggered by: {run['event'].replace('_', ' ').title()}"
        )
        yield from success_message(
            display_ctx, f"Started: {run['created_at'].strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        yield from success_message(display_ctx, f"URL: {run['url']}")

        # Display jobs
        yield from display_rule(display_ctx, "Jobs")

        if not run["jobs"]:
            yield from warning_message(display_ctx, "No jobs found for this workflow run")
            return Ok(None)

        job_headers = ["Name", "Status", "Conclusion", "Started", "Duration"]
        job_rows = []

        for job in run["jobs"]:
            status = job["status"]
            conclusion = job["conclusion"] or "pending"

            # Calculate duration if possible
            duration = "N/A"
            if job["started_at"] and job["completed_at"]:
                start = job["started_at"]
                end = job["completed_at"]
                delta = end - start
                minutes = delta.seconds // 60
                seconds = delta.seconds % 60
                duration = f"{minutes}m {seconds}s"

            # Format start time
            started = "N/A"
            if job["started_at"]:
                started = job["started_at"].strftime("%H:%M:%S")

            job_rows.append([job["name"], status, conclusion, started, duration])

        # Create and display jobs table
        jobs_table_result = yield from create_multi_column_table("Jobs", job_headers, job_rows)
        if jobs_table_result.is_ok():
            yield from display_table(jobs_table_result.ok)
        else:
            yield from error_message(display_ctx, "Failed to create jobs table")

        # Show steps for each job
        for job_index, job in enumerate(run["jobs"]):
            if not job.get("steps"):
                continue

            yield from display_rule(display_ctx, f"Steps for Job: {job['name']}")

            step_headers = ["#", "Name", "Status", "Conclusion"]
            step_rows = []

            for step in job["steps"]:
                step_rows.append(
                    [
                        str(step["number"]),
                        step["name"],
                        step["status"],
                        step["conclusion"] or "pending",
                    ]
                )

            # Create and display steps table
            steps_table_result = yield from create_multi_column_table(
                f"Steps for {job['name']}", step_headers, step_rows
            )
            if steps_table_result.is_ok():
                yield from display_table(steps_table_result.ok)
            else:
                yield from error_message(
                    display_ctx, f"Failed to create steps table for job {job['name']}"
                )

    except Exception as e:
        yield from error_message(
            display_ctx, "Failed to display workflow run details", details=str(e)
        )
        return Error(str(e))

    return Ok(None)


@effect.result[str, str]()
def get_workflow_logs(token: str, repo_name: str, run_id: int):
    """Download logs for a specific workflow run"""
    try:
        g = Github(token)
        user = g.get_user()
        repo = user.get_repo(repo_name)

        # Get workflow run
        run = repo.get_workflow_run(run_id)

        # Download logs
        with Progress(
            SpinnerColumn(), TextColumn("[bold blue]Downloading workflow logs...")
        ) as progress:
            progress.add_task("download", total=None)
            log_url = run.logs_url

            # Use the PyGithub internals to download the logs
            # This might change in future PyGithub versions
            requester = g._Github__requester
            _, data = requester.requestBlobAndCheck("GET", log_url)

        yield Ok(str(data, encoding="utf-8"))
    except Exception as e:
        yield Error(f"Failed to download workflow logs: {e!s}")


def extract_failed_step_logs(logs: str) -> dict[str, str]:
    """Extract logs for failed steps from a workflow run log"""
    # This is a simplified implementation and might need adjustments
    # based on the actual log format
    failed_logs = {}

    # Split logs by job
    job_sections = re.split(r"\n##\[group\](.+?)\n", logs)

    for i in range(1, len(job_sections), 2):
        if i + 1 < len(job_sections):
            job_name = job_sections[i].strip()
            job_log = job_sections[i + 1]

            # Check if the job has failed steps
            if "##[error]" in job_log:
                # Split by steps
                step_sections = re.split(r"\n##\[group\](.+?)\n", job_log)

                for j in range(1, len(step_sections), 2):
                    if j + 1 < len(step_sections):
                        step_name = step_sections[j].strip()
                        step_log = step_sections[j + 1]

                        # Check if step has errors
                        if "##[error]" in step_log:
                            # Extract the error and context (simplified)
                            failed_logs[f"{job_name} > {step_name}"] = step_log

    return failed_logs


@effect.result[None, str]()
def display_workflow_logs(
    token: str,
    repo_name: str,
    run_id: int,
    show_failed_only: bool = True,
    display_ctx: DisplayContext = None,
):
    """Display logs for a specific workflow run, focusing on failed steps"""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())

    try:
        # Display header
        yield from display_rule(display_ctx, f"GitHub Actions Workflow Run #{run_id} Logs")

        # Get workflow logs
        logs_result = yield from get_workflow_logs(token, repo_name, run_id)
        if logs_result.is_error():
            yield from error_message(display_ctx, "Failed to get workflow logs", logs_result.error)
            return Error(logs_result.error)

        logs = logs_result.ok

        if show_failed_only:
            # Extract failed steps
            failed_logs = extract_failed_step_logs(logs)

            if not failed_logs:
                yield from warning_message(display_ctx, "No failed steps found in the logs")
                return Ok(None)

            # Display failed steps
            for step_name, step_log in failed_logs.items():
                # Create a syntax-highlighted panel
                syntax = Syntax(
                    step_log, "bash", theme="monokai", line_numbers=True, word_wrap=True
                )

                panel = Panel(
                    syntax, title=f"[bold red]Failed Step: {step_name}[/bold red]", expand=False
                )

                display_ctx.console.print(panel)
        else:
            # Display full logs
            syntax = Syntax(logs, "bash", theme="monokai", line_numbers=True, word_wrap=True)

            display_ctx.console.print(syntax)

        yield Ok(None)
    except Exception as e:
        yield from error_message(display_ctx, "Failed to display workflow logs", details=str(e))
        return Error(str(e))

    return Ok(None)


@effect.result[str, str]()
def rerun_workflow(token: str, repo_name: str, run_id: int):
    """Rerun a specific workflow run"""
    try:
        g = Github(token)
        user = g.get_user()
        repo = user.get_repo(repo_name)

        # Get workflow run
        run = repo.get_workflow_run(run_id)

        # Rerun the workflow
        run.rerun()

        yield Ok(f"Workflow run #{run_id} has been triggered to rerun")
    except Exception as e:
        yield Error(f"Failed to rerun workflow: {e!s}")


@effect.result[None, str]()
def watch_workflow_run(token: str, repo_name: str, run_id: int, display_ctx: DisplayContext = None):
    """Watch a workflow run and display real-time status updates"""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())

    try:
        g = Github(token)
        user = g.get_user()
        repo = user.get_repo(repo_name)

        # Get initial workflow run details
        run_result = yield from get_workflow_run_details(token, repo_name, run_id)
        if run_result.is_error():
            yield from error_message(
                display_ctx, "Failed to get workflow run details", run_result.error
            )
            return Error(run_result.error)

        run = run_result.ok
        initial_run = run["raw_run"]

        # Display initial information
        yield from display_rule(display_ctx, f"Watching GitHub Actions Workflow Run #{run_id}")
        yield from success_message(display_ctx, f"Workflow: {run['name']}")
        yield from success_message(
            display_ctx, f"Branch: {run['head_branch']} ({run['head_sha'][:7]})"
        )
        yield from success_message(display_ctx, f"URL: {run['url']}")

        # Watch loop
        with Progress(
            SpinnerColumn(), TextColumn("[bold blue]Watching workflow run..."), transient=True
        ) as progress:
            task = progress.add_task("watching", total=None)

            # Track job states
            job_states = {
                job["id"]: {"status": job["status"], "conclusion": job["conclusion"]}
                for job in run["jobs"]
            }

            # Continue while run is active
            active = initial_run.status in ["queued", "in_progress", "waiting"]
            start_time = time.time()
            update_interval = 5  # seconds
            max_duration = 60 * 30  # 30 minutes maximum watch time
            last_refresh = start_time

            while active and (time.time() - start_time) < max_duration:
                # Check if it's time for a refresh
                if time.time() - last_refresh >= update_interval:
                    # Refresh run information
                    run_result = yield from get_workflow_run_details(token, repo_name, run_id)
                    if run_result.is_error():
                        # Don't fail on temporary errors, just try again later
                        time.sleep(update_interval)
                        last_refresh = time.time()
                        continue

                    run = run_result.ok
                    current_run = run["raw_run"]
                    last_refresh = time.time()

                    # Check for status/conclusion changes
                    if (
                        current_run.status != initial_run.status
                        or current_run.conclusion != initial_run.conclusion
                    ):
                        display_ctx.console.print(
                            f"[yellow]Workflow status changed: {initial_run.status} → {current_run.status} / {initial_run.conclusion or 'pending'} → {current_run.conclusion or 'pending'}[/yellow]"
                        )
                        initial_run = current_run

                    # Check for job changes
                    for job in run["jobs"]:
                        job_id = job["id"]
                        if job_id in job_states:
                            old_status = job_states[job_id]["status"]
                            old_conclusion = job_states[job_id]["conclusion"]

                            if job["status"] != old_status or job["conclusion"] != old_conclusion:
                                display_ctx.console.print(
                                    f"[cyan]Job '{job['name']}' changed: {old_status} → {job['status']} / {old_conclusion or 'pending'} → {job['conclusion'] or 'pending'}[/cyan]"
                                )
                                job_states[job_id] = {
                                    "status": job["status"],
                                    "conclusion": job["conclusion"],
                                }
                        else:
                            display_ctx.console.print(
                                f"[green]New job started: '{job['name']}' - {job['status']}[/green]"
                            )
                            job_states[job_id] = {
                                "status": job["status"],
                                "conclusion": job["conclusion"],
                            }

                    # Check if we should stop watching
                    active = current_run.status in ["queued", "in_progress", "waiting"]

                    # Increase interval as time passes
                    if time.time() - start_time > 300:  # After 5 minutes
                        update_interval = 10
                    if time.time() - start_time > 600:  # After 10 minutes
                        update_interval = 20

                time.sleep(1)  # Small sleep to prevent CPU spinning

        # Final status
        yield from display_rule(display_ctx, "Final Workflow Status")

        # Get final details
        final_run_result = yield from get_workflow_run_details(token, repo_name, run_id)
        if final_run_result.is_ok():
            final_run = final_run_result.ok

            status_color = "green" if final_run["conclusion"] == "success" else "red"
            yield from success_message(
                display_ctx, f"Status: [{status_color}]{final_run['status']}[/{status_color}]"
            )
            yield from success_message(
                display_ctx,
                f"Conclusion: [{status_color}]{final_run['conclusion'] or 'pending'}[/{status_color}]",
            )

            if final_run["conclusion"] == "failure":
                yield from warning_message(
                    display_ctx, "Workflow failed! Use 'logs' command to see error details"
                )
        else:
            # Use the last known state
            status_color = "green" if initial_run.conclusion == "success" else "red"
            yield from success_message(
                display_ctx, f"Status: [{status_color}]{initial_run.status}[/{status_color}]"
            )
            yield from success_message(
                display_ctx,
                f"Conclusion: [{status_color}]{initial_run.conclusion or 'pending'}[/{status_color}]",
            )

        yield Ok(None)
    except Exception as e:
        yield from error_message(display_ctx, "Failed to watch workflow run", details=str(e))
        return Error(str(e))

    return Ok(None)
