"""Commands package for the fast-craftsmanship CLI tool."""

from collections.abc import Callable
from typing import Any

from .api import api
from .commit.commit import commit
from .db import db
from .domain import domain
from .github.cli import github_app
from .project import project
from .repo import repo
from .service import service
from .test import test
from .verify import verify

# Command function type hint
CommandFunction = Callable[..., Any]

# Command definitions with their help text
COMMANDS: dict[str, tuple[CommandFunction, str]] = {
    "domain": (domain, "Create and manage domain components"),
    "service": (service, "Create and manage service layer components"),
    "api": (api, "Generate API endpoints and schemas"),
    "repo": (repo, "Create and manage repository implementations"),
    "test": (test, "Create test files and run tests"),
    "project": (project, "Initialize and manage project structure"),
    "db": (db, "Manage database migrations"),
    "verify": (verify, "Run code quality checks"),
    "commit": (commit, "Tool to create commit messages"),
}

__all__ = [
    "COMMANDS",
    "api",
    "commit",
    "db",
    "domain",
    "github_app",
    "project",
    "repo",
    "service",
    "test",
    "verify",
]
