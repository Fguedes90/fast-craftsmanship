"""Unit tests for generate_commit_message.py module."""

import pytest

from fcship.commands.commit.commit_types import COMMIT_TYPES
from fcship.commands.commit.generate_commit_message import (
    analyze_diff,
    combine_commit_messages,
    generate_commit_message,
    get_move_details,
)


def test_analyze_diff_empty():
    """Test analyzing an empty diff."""
    additions, deletions, is_rename = analyze_diff("")
    assert additions == []
    assert deletions == []
    assert is_rename is False


def test_analyze_diff_additions():
    """Test analyzing a diff with additions."""
    diff = """
diff --git a/test.py b/test.py
index 123456..789012 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,5 @@
 existing line
+new line 1
+new line 2
 another existing line
"""
    additions, deletions, is_rename = analyze_diff(diff)
    assert additions == ["new line 1", "new line 2"]
    assert deletions == []
    assert is_rename is False


def test_analyze_diff_deletions():
    """Test analyzing a diff with deletions."""
    diff = """
diff --git a/test.py b/test.py
index 123456..789012 100644
--- a/test.py
+++ b/test.py
@@ -1,5 +1,3 @@
 existing line
-deleted line 1
-deleted line 2
 another existing line
"""
    additions, deletions, is_rename = analyze_diff(diff)
    assert additions == []
    assert deletions == ["deleted line 1", "deleted line 2"]
    assert is_rename is False


def test_analyze_diff_mixed_changes():
    """Test analyzing a diff with both additions and deletions."""
    diff = """
diff --git a/test.py b/test.py
index 123456..789012 100644
--- a/test.py
+++ b/test.py
@@ -1,4 +1,4 @@
 existing line
-deleted line
+new line
 another existing line
"""
    additions, deletions, is_rename = analyze_diff(diff)
    assert additions == ["new line"]
    assert deletions == ["deleted line"]
    assert is_rename is False


def test_analyze_diff_rename():
    """Test analyzing a diff with a rename operation."""
    diff = """
diff --git a/old_name.py b/new_name.py
similarity index 100%
rename from old_name.py
rename to new_name.py
"""
    additions, deletions, is_rename = analyze_diff(diff)
    assert additions == []
    assert deletions == []
    assert is_rename is True


def test_get_move_details_empty():
    """Test extracting move details from an empty diff."""
    old_name, new_name = get_move_details("")
    assert old_name is None
    assert new_name is None


def test_get_move_details_no_rename():
    """Test extracting move details from a diff without rename."""
    diff = """
diff --git a/test.py b/test.py
index 123456..789012 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 existing line
+new line
 another existing line
"""
    old_name, new_name = get_move_details(diff)
    assert old_name is None
    assert new_name is None


def test_get_move_details_with_rename():
    """Test extracting move details from a diff with rename."""
    diff = """
diff --git a/old_name.py b/new_name.py
similarity index 100%
rename from old_name.py
rename to new_name.py
"""
    old_name, new_name = get_move_details(diff)
    assert old_name == "old_name.py"
    assert new_name == "new_name.py"


def test_generate_commit_message_empty():
    """Test generating a commit message from an empty diff."""
    message = generate_commit_message("")
    assert message == ""


def test_generate_commit_message_rename():
    """Test generating a commit message for a rename operation."""
    diff = """
diff --git a/old_name.py b/new_name.py
similarity index 100%
rename from old_name.py
rename to new_name.py
"""
    message = generate_commit_message(diff)
    expected = f"{COMMIT_TYPES['move'].emoji} move: old_name.py -> new_name.py"
    assert message == expected


def test_generate_commit_message_additions():
    """Test generating a commit message for additions."""
    diff = """
diff --git a/test.py b/test.py
index 123456..789012 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,5 @@
 existing line
+new line 1
+new line 2
 another existing line
"""
    message = generate_commit_message(diff)
    expected = f"{COMMIT_TYPES['add'].emoji} add: new content added"
    assert message == expected


def test_generate_commit_message_deletions():
    """Test generating a commit message for deletions."""
    diff = """
diff --git a/test.py b/test.py
index 123456..789012 100644
--- a/test.py
+++ b/test.py
@@ -1,5 +1,3 @@
 existing line
-deleted line 1
-deleted line 2
 another existing line
"""
    message = generate_commit_message(diff)
    expected = f"{COMMIT_TYPES['remove'].emoji} remove: content removed"
    assert message == expected


def test_generate_commit_message_updates():
    """Test generating a commit message for mixed changes."""
    diff = """
diff --git a/test.py b/test.py
index 123456..789012 100644
--- a/test.py
+++ b/test.py
@@ -1,4 +1,4 @@
 existing line
-deleted line
+new line
 another existing line
"""
    message = generate_commit_message(diff)
    expected = f"{COMMIT_TYPES['update'].emoji} update: content modified"
    assert message == expected


def test_generate_commit_message_other_changes():
    """Test generating a commit message for other changes."""
    # A diff with only mode changes, not content changes
    diff = """
diff --git a/test.py b/test.py
old mode 100644
new mode 100755
"""
    message = generate_commit_message(diff)
    expected = f"{COMMIT_TYPES['chore'].emoji} chore: other changes"
    assert message == expected


def test_combine_commit_messages_empty():
    """Test combining an empty list of commit messages."""
    combined = combine_commit_messages([])
    assert combined == ""


def test_combine_commit_messages_single():
    """Test combining a single commit message."""
    messages = ["✨ feat: add new feature"]
    combined = combine_commit_messages(messages)
    assert combined == "✨ feat: add new feature"


def test_combine_commit_messages_multiple_different_types():
    """Test combining multiple commit messages with different types."""
    messages = [
        "✨ feat: add new feature",
        "🐛 fix: fix bug in login",
    ]
    combined = combine_commit_messages(messages)
    assert combined == "✨ feat: add new feature\n🐛 fix: fix bug in login"


def test_combine_commit_messages_multiple_same_type():
    """Test combining multiple commit messages with the same type."""
    messages = [
        "✨ feat: add user profile",
        "✨ feat: add payment system",
    ]
    combined = combine_commit_messages(messages)
    assert combined == "✨ feat:\n  - add user profile\n  - add payment system"


def test_combine_commit_messages_mixed():
    """Test combining mixed commit messages with some same types."""
    messages = [
        "✨ feat: add user profile",
        "🐛 fix: fix login bug",
        "✨ feat: add payment system",
        "📝 docs: update README",
    ]
    combined = combine_commit_messages(messages)
    expected = (
        "✨ feat:\n  - add user profile\n  - add payment system\n"
        "🐛 fix: fix login bug\n"
        "📝 docs: update README"
    )
    assert combined == expected


def test_combine_commit_messages_invalid_format():
    """Test combining messages with invalid format."""
    messages = [
        "✨ feat: add user profile",
        "invalid message format",
        "🐛 fix: fix login bug",
    ]
    combined = combine_commit_messages(messages)
    assert combined == "✨ feat: add user profile\n🐛 fix: fix login bug"