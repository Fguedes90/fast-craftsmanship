"""Commands package for the fast-craftsmanship CLI tool."""

from collections.abc import Callable
from typing import Any

from .api import api
from .commit.commit import commit
from .compact.compact import compact_command
from .db import db
from .docs import setup_command, serve_docs, build_docs
from .domain import domain
from .github.cli import github_app
from .project import project
from .repo import repo
from .service import service
from .test import test
from .verify import verify

# Command function type hint
CommandFunction = Callable[..., Any]

# Command categories with their help text
COMMAND_CATEGORIES: dict[str, str] = {
    "scaffold": "Project Scaffolding & Structure",
    "vcs": "Version Control & Collaboration",
    "github": "GitHub Integration",
    "quality": "Quality Assurance & Testing",
    "db": "Database Management", 
    "docs": "Documentation Management",
    "scraper": "Web Scraping",
    "utils": "Utility Commands"
}

# Command definitions organized by category
COMMANDS_BY_CATEGORY: dict[str, dict[str, tuple[CommandFunction, str]]] = {
    "scaffold": {
        "project": (project, "Initialize and manage project structure"),
        "domain": (domain, "Create and manage domain components"),
        "service": (service, "Create and manage service layer components"),
        "api": (api, "Generate API endpoints and schemas"),
        "repo": (repo, "Create and manage repository implementations"),
    },
    "vcs": {
        "commit": (commit, "Tool to create commit messages"),
    },
    "github": {
        "github": (lambda *args, **kwargs: None, "GitHub repository and workflow management"),
    },
    "quality": {
        "test": (test, "Create test files and run tests"),
        "verify": (verify, "Run code quality checks"),
    },
    "db": {
        "db": (db, "Manage database migrations"),
    },
    "utils": {
        "compact": (compact_command, "Generate compact code representation"),
    },
    "docs": {
        "setup": (setup_command, "Configurar MkDocs interativamente"),
        "serve": (serve_docs, "Iniciar servidor de desenvolvimento do MkDocs"),
        "build": (build_docs, "Construir documentação para produção"),
    },
    "scraper": {
        "scraper": (lambda *args, **kwargs: None, "Web scraping tools and utilities"),
    },
}

# Flat command structure for backward compatibility
COMMANDS: dict[str, tuple[CommandFunction, str]] = {}
for category_commands in COMMANDS_BY_CATEGORY.values():
    COMMANDS.update(category_commands)

__all__ = [
    "COMMANDS",
    "COMMANDS_BY_CATEGORY",
    "COMMAND_CATEGORIES",
    "api",
    "commit",
    "compact_command",
    "db",
    "domain",
    "github_app",
    "project",
    "repo",
    "service",
    "test",
    "verify",
    "setup_command",
    "serve_docs",
    "build_docs",
]
