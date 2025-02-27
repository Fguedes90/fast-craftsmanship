"""Generate commit messages based on file changes."""

from .commit_types import COMMIT_TYPES


def analyze_diff(diff_text: str) -> tuple[list[str], list[str], bool]:
    """Analyze diff content and return additions, deletions, and rename status."""
    if not diff_text:
        return [], [], False

    lines = diff_text.splitlines()
    additions = [line[1:] for line in lines if line.startswith("+") and not line.startswith("+++")]
    deletions = [line[1:] for line in lines if line.startswith("-") and not line.startswith("---")]
    is_rename = any(line.startswith("rename from") for line in lines)

    return additions, deletions, is_rename


def get_move_details(diff_text: str) -> tuple[str | None, str | None]:
    """Extract old and new names from rename operation in diff."""
    lines = diff_text.splitlines()
    old_name = next(
        (line.replace("rename from ", "") for line in lines if line.startswith("rename from")), None
    )
    new_name = next(
        (line.replace("rename to ", "") for line in lines if line.startswith("rename to")), None
    )
    return old_name, new_name


def generate_commit_message(diff_text: str) -> str:
    """Generate a conventional commit message based on the diff content."""
    if not diff_text:
        return ""

    additions, deletions, is_rename = analyze_diff(diff_text)

    # Handle renamed files
    if is_rename:
        old_name, new_name = get_move_details(diff_text)
        if old_name and new_name:
            commit_type = COMMIT_TYPES["move"]
            return f"{commit_type.emoji} move: {old_name} -> {new_name}"

    # Handle content changes
    if additions and deletions:
        commit_type = COMMIT_TYPES["update"]
        return f"{commit_type.emoji} update: content modified"
    if additions:
        commit_type = COMMIT_TYPES["add"]
        return f"{commit_type.emoji} add: new content added"
    if deletions:
        commit_type = COMMIT_TYPES["remove"]
        return f"{commit_type.emoji} remove: content removed"

    commit_type = COMMIT_TYPES["chore"]
    return f"{commit_type.emoji} chore: other changes"


def combine_commit_messages(messages: list[str]) -> str:
    """Combine multiple commit messages into a single message."""
    if not messages:
        return ""

    # Group similar messages to avoid repetition
    grouped_messages = {}
    for msg in messages:
        if ":" not in msg:
            continue
        prefix, content = msg.split(": ", 1)
        if prefix not in grouped_messages:
            grouped_messages[prefix] = []
        grouped_messages[prefix].append(content)

    # Combine messages by type
    combined = []
    for prefix, contents in grouped_messages.items():
        if len(contents) == 1:
            combined.append(f"{prefix}: {contents[0]}")
        else:
            combined_content = "\n  - " + "\n  - ".join(contents)
            combined.append(f"{prefix}:{combined_content}")

    return "\n".join(combined)
