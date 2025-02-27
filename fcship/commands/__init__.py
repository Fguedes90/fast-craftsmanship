"""Commands package for the fast-craftsmanship CLI tool."""
from typing import Callable, Any, Dict, Tuple

from .domain import domain
from .service import service
from .api import api
from .repo import repo
from .test import test
from .project import project
from .db import db
from .verify import verify
from .commit.commit import commit
from .github.cli import github_app

# Command function type hint
CommandFunction = Callable[..., Any]

# Command definitions with their help text
COMMANDS: Dict[str, Tuple[CommandFunction, str]] = {
    "domain": (domain, "Create and manage domain components"),
    "service": (service, "Create and manage service layer components"),
    "api": (api, "Generate API endpoints and schemas"),
    "repo": (repo, "Create and manage repository implementations"),
    "test": (test, "Create test files and run tests"),
    "project": (project, "Initialize and manage project structure"),
    "db": (db, "Manage database migrations"),
    "verify": (verify, "Run code quality checks"),
    "commit": (commit, "Tool to create commit messages")
}

__all__ = [
    "COMMANDS",
    "domain",
    "service", 
    "api",
    "repo",
    "test",
    "project",
    "db",
    "verify",
    "commit",
    "github_app"
]