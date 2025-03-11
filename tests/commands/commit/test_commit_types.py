"""Tests for commit_types module."""

import pytest
from fcship.commands.commit.commit_types import COMMIT_TYPES, CommitType


def test_commit_types_structure():
    """Test that COMMIT_TYPES has the expected structure."""
    # Verify all expected commit types are present
    expected_types = [
        "feat", "fix", "docs", "style", "refactor", "perf", 
        "test", "build", "ci", "chore", "i18n", "move", 
        "add", "remove", "update"
    ]
    
    assert set(COMMIT_TYPES.keys()) == set(expected_types), "Missing or unexpected commit types"
    
    # Verify each CommitType has the correct structure
    for commit_type, commit_info in COMMIT_TYPES.items():
        assert isinstance(commit_info, CommitType), f"{commit_type} is not a CommitType"
        assert isinstance(commit_info.emoji, str), f"{commit_type} emoji is not a string"
        assert isinstance(commit_info.description, str), f"{commit_type} description is not a string"
        assert isinstance(commit_info.example_scopes, list), f"{commit_type} example_scopes is not a list"
        assert all(isinstance(scope, str) for scope in commit_info.example_scopes), f"{commit_type} has non-string scopes"
        
        # Verify required attributes are not empty
        assert commit_info.emoji, f"{commit_type} has empty emoji"
        assert commit_info.description, f"{commit_type} has empty description"


def test_specific_commit_types():
    """Test specific commit types for expected values."""
    # Test a few specific entries
    assert COMMIT_TYPES["feat"].emoji == "✨"
    assert COMMIT_TYPES["feat"].description == "New feature"
    assert "user" in COMMIT_TYPES["feat"].example_scopes
    
    assert COMMIT_TYPES["fix"].emoji == "🐛"
    assert COMMIT_TYPES["fix"].description == "Bug fix"
    assert "auth" in COMMIT_TYPES["fix"].example_scopes
    
    assert COMMIT_TYPES["docs"].emoji == "📝"
    assert COMMIT_TYPES["docs"].description == "Documentation"
    assert "README" in COMMIT_TYPES["docs"].example_scopes