"""Tests for commit command functionality."""

import pytest
from unittest.mock import MagicMock, patch

from rich.console import Console

from fcship.commands.commit.commit import display_status, generate_commit_messages_for_status
from fcship.commands.commit.utils import GitFileStatus, GitStatus


@pytest.fixture
def mock_console():
    """Mock rich console for testing."""
    with patch("fcship.commands.commit.commit.console", new=MagicMock(spec=Console)) as mock_console:
        yield mock_console


class TestDisplayStatus:
    """Tests for the display_status function."""

    def test_display_empty_status(self, mock_console):
        """Test displaying an empty status with no changes."""
        # Create an empty status
        status = GitStatus()
        
        # Call the function
        result = display_status(status)
        
        # Verify the result is False
        assert result is False
        # Verify the appropriate message was displayed
        mock_console.print.assert_called_once()
        
    def test_display_status_with_changes(self, mock_console):
        """Test displaying a status with various types of changes."""
        # Create a status with different change types
        status = GitStatus(
            renamed=[GitFileStatus(path="new_file.py", original_path="old_file.py")],
            added=[GitFileStatus(path="added_file.py")],
            modified=[GitFileStatus(path="modified_file.py")],
            deleted=[GitFileStatus(path="deleted_file.py")],
            untracked=[GitFileStatus(path="untracked_file.py")]
        )
        
        # Call the function
        result = display_status(status)
        
        # Verify the result is True
        assert result is True
        
        # Verify all change types were displayed
        assert mock_console.print.call_count >= 6  # Header + each change type
        
        # Verify only that each type was displayed (order might vary by implementation)
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Changes detected" in call for call in calls)
        assert any("Renamed files" in call for call in calls)
        assert any("New files" in call for call in calls)
        assert any("Modified files" in call for call in calls)
        assert any("Deleted files" in call for call in calls)
        assert any("Untracked files" in call for call in calls)
        
    def test_display_partial_status(self, mock_console):
        """Test displaying a status with only some change types."""
        # Create a status with only added and modified files
        status = GitStatus(
            added=[GitFileStatus(path="added_file.py")],
            modified=[GitFileStatus(path="modified_file.py")]
        )
        
        # Call the function
        result = display_status(status)
        
        # Verify the result is True
        assert result is True
        
        # Verify only the relevant change types were displayed
        calls = [str(call) for call in mock_console.print.call_args_list]
        
        # Check that only the relevant sections were displayed
        assert any("Changes detected" in call for call in calls)
        assert any("New files" in call for call in calls)
        assert any("Modified files" in call for call in calls)
        
        # And verify the unrelevant ones weren't displayed
        assert not any("Renamed files" in call for call in calls)
        assert not any("Deleted files" in call for call in calls)
        assert not any("Untracked files" in call for call in calls)


class TestGenerateCommitMessagesForStatus:
    """Tests for the generate_commit_messages_for_status function."""
    
    @patch("fcship.commands.commit.commit.GitCommands")
    def test_empty_status(self, mock_git_commands):
        """Test generating commit messages for an empty status."""
        status = GitStatus()
        
        messages = generate_commit_messages_for_status(status)
        
        assert messages == []
        # No git commands should be called
        mock_git_commands.get_file_diff.assert_not_called()
    
    @patch("fcship.commands.commit.commit.GitCommands")
    def test_renamed_files(self, mock_git_commands):
        """Test generating commit messages for renamed files."""
        # Setup
        status = GitStatus(
            renamed=[GitFileStatus(path="new_path.py", original_path="old_path.py")]
        )
        
        # Empty diff (no content changes)
        mock_git_commands.get_file_diff.return_value = ""
        
        # Test
        messages = generate_commit_messages_for_status(status)
        
        # Verify
        assert len(messages) == 1
        assert messages[0] == "🚚 move: old_path.py -> new_path.py"
        mock_git_commands.get_file_diff.assert_called_once_with("new_path.py")
    
    @patch("fcship.commands.commit.commit.GitCommands")
    @patch("fcship.commands.commit.commit.generate_commit_message")
    def test_renamed_with_modifications(self, mock_generate_message, mock_git_commands):
        """Test generating commit messages for files renamed with modifications."""
        # Setup
        status = GitStatus(
            renamed=[GitFileStatus(path="new_path.py", original_path="old_path.py")]
        )
        
        # Return a non-empty diff to indicate content changes
        mock_git_commands.get_file_diff.return_value = "some diff content"
        # Make sure it doesn't return a move message
        mock_generate_message.return_value = "update in function"
        
        # Test
        messages = generate_commit_messages_for_status(status)
        
        # Verify
        assert len(messages) == 2
        assert messages[0] == "🚚 move: old_path.py -> new_path.py"
        assert messages[1] == "✨ update: new_path.py - Modified after move"
        mock_git_commands.get_file_diff.assert_called_once_with("new_path.py")
        mock_generate_message.assert_called_once_with("some diff content")
    
    @patch("fcship.commands.commit.commit.GitCommands")
    def test_added_files(self, mock_git_commands):
        """Test generating commit messages for added files."""
        # Setup
        status = GitStatus(
            added=[GitFileStatus(path="new_file1.py"), GitFileStatus(path="new_file2.py")]
        )
        
        # Test
        messages = generate_commit_messages_for_status(status)
        
        # Verify
        assert len(messages) == 2
        assert messages[0] == "➕ add: new_file1.py"
        assert messages[1] == "➕ add: new_file2.py"
        # No diffs are generated for added files
        mock_git_commands.get_file_diff.assert_not_called()
    
    @patch("fcship.commands.commit.commit.GitCommands")
    def test_deleted_files(self, mock_git_commands):
        """Test generating commit messages for deleted files."""
        # Setup
        status = GitStatus(
            deleted=[GitFileStatus(path="deleted_file.py")]
        )
        
        # Test
        messages = generate_commit_messages_for_status(status)
        
        # Verify
        assert len(messages) == 1
        assert messages[0] == "🗑️ remove: deleted_file.py"
        # No diffs are generated for deleted files
        mock_git_commands.get_file_diff.assert_not_called()
    
    @patch("fcship.commands.commit.commit.GitCommands")
    @patch("fcship.commands.commit.commit.generate_commit_message")
    def test_modified_files(self, mock_generate_message, mock_git_commands):
        """Test generating commit messages for modified files."""
        # Setup
        status = GitStatus(
            modified=[GitFileStatus(path="modified_file.py")]
        )
        
        # Mock the diff and generated message
        mock_git_commands.get_file_diff.return_value = "diff content"
        mock_generate_message.return_value = "updated error handling"
        
        # Test
        messages = generate_commit_messages_for_status(status)
        
        # Verify
        assert len(messages) == 1
        assert messages[0] == "✨ update: modified_file.py - updated error handling"
        mock_git_commands.get_file_diff.assert_called_once_with("modified_file.py")
        mock_generate_message.assert_called_once_with("diff content")
    
    @patch("fcship.commands.commit.commit.GitCommands")
    @patch("fcship.commands.commit.commit.generate_commit_message")
    def test_modified_files_no_diff(self, mock_generate_message, mock_git_commands):
        """Test generating commit messages for modified files with no diff."""
        # Setup
        status = GitStatus(
            modified=[GitFileStatus(path="modified_file.py")]
        )
        
        # Mock an empty diff
        mock_git_commands.get_file_diff.return_value = ""
        
        # Test
        messages = generate_commit_messages_for_status(status)
        
        # Verify
        assert len(messages) == 0
        mock_git_commands.get_file_diff.assert_called_once_with("modified_file.py")
        mock_generate_message.assert_not_called()
    
    @patch("fcship.commands.commit.commit.GitCommands")
    def test_untracked_files(self, mock_git_commands):
        """Test generating commit messages for untracked files."""
        # Setup
        status = GitStatus(
            untracked=[GitFileStatus(path="untracked_file.py")]
        )
        
        # Test
        messages = generate_commit_messages_for_status(status)
        
        # Verify
        assert len(messages) == 1
        assert messages[0] == "➕ add: untracked_file.py"
        # No diffs should be generated for untracked files
        mock_git_commands.get_file_diff.assert_not_called()
    
    @patch("fcship.commands.commit.commit.GitCommands")
    @patch("fcship.commands.commit.commit.generate_commit_message")
    def test_mixed_changes(self, mock_generate_message, mock_git_commands):
        """Test generating commit messages for a mix of file changes."""
        # Setup
        status = GitStatus(
            renamed=[GitFileStatus(path="new_name.py", original_path="old_name.py")],
            added=[GitFileStatus(path="added_file.py")],
            modified=[GitFileStatus(path="modified_file.py")],
            deleted=[GitFileStatus(path="deleted_file.py")],
            untracked=[GitFileStatus(path="untracked_file.py")]
        )
        
        # Mock responses for diffs and message generation
        def get_file_diff_side_effect(path):
            if path == "new_name.py":
                return "renamed file diff"
            elif path == "modified_file.py":
                return "modified file diff"
            return ""
            
        mock_git_commands.get_file_diff.side_effect = get_file_diff_side_effect
        
        def generate_message_side_effect(diff):
            if diff == "renamed file diff":
                return "updated class structure"
            elif diff == "modified file diff":
                return "fixed bug in calculation"
            return ""
            
        mock_generate_message.side_effect = generate_message_side_effect
        
        # Test
        messages = generate_commit_messages_for_status(status)
        
        # Verify all expected messages are present
        expected_messages = [
            "🚚 move: old_name.py -> new_name.py",
            "✨ update: new_name.py - Modified after move",
            "➕ add: added_file.py",
            "🗑️ remove: deleted_file.py",
            "✨ update: modified_file.py - fixed bug in calculation",
            "➕ add: untracked_file.py"
        ]
        
        # Check that we have the right number of messages
        assert len(messages) == len(expected_messages)
        
        # Check that all expected messages are present
        for expected in expected_messages:
            assert expected in messages
        
        # Verify correct calls to get diffs
        assert mock_git_commands.get_file_diff.call_count == 2
        mock_git_commands.get_file_diff.assert_any_call("new_name.py")
        mock_git_commands.get_file_diff.assert_any_call("modified_file.py")