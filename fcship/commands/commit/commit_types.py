"""Types and emojis for conventional commits."""

from typing import NamedTuple


class CommitType(NamedTuple):
    """Commit type with emoji and description."""

    emoji: str
    description: str
    example_scopes: list[str]


COMMIT_TYPES: dict[str, CommitType] = {
    "feat": CommitType("✨", "New feature", ["user", "payment"]),
    "fix": CommitType("🐛", "Bug fix", ["auth", "data"]),
    "docs": CommitType("📝", "Documentation", ["README", "API"]),
    "style": CommitType("💄", "Code style", ["formatting"]),
    "refactor": CommitType("♻️", "Code refactoring", ["utils", "helpers"]),
    "perf": CommitType("⚡️", "Performance", ["query", "cache"]),
    "test": CommitType("✅", "Testing", ["unit", "e2e"]),
    "build": CommitType("📦", "Build system", ["webpack", "npm"]),
    "ci": CommitType("👷", "CI config", ["Travis", "Jenkins"]),
    "chore": CommitType("🔧", "Other changes", ["scripts", "config"]),
    "i18n": CommitType("🌐", "Internationalization", ["locale", "translation"]),
    "move": CommitType("🚚", "Move/rename", ["files", "folders"]),
    "add": CommitType("➕", "Add files", ["assets", "config"]),
    "remove": CommitType("🗑️", "Remove files", ["deprecated", "unused"]),
    "update": CommitType("✨", "Update content", ["content", "data"]),
}
