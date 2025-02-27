"""GitHub commands module."""

from typing import Any, Literal

from fcship.commands.github.cli import github_app
from fcship.commands.github.main import (
    Release,
    WorkflowRunSummary,
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
from fcship.commands.github.setup import app as setup_app

__all__ = [
    "Release",
    "WorkflowRunSummary",
    "create_issue",
    "create_pull_request",
    "create_release",
    "delete_repository",
    "display_workflow_logs",
    "display_workflow_run_details",
    "download_issue_body",
    "github_app",
    "setup_app",
    "list_branches",
    "list_issues",
    "list_pull_requests",
    "list_repositories",
    "list_workflow_runs",
    "rerun_workflow",
    "watch_workflow_run",
]
