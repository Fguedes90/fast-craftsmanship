"""Tests for commit module utils."""

import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from fcship.commands.commit.utils import (
    GitCommands,
    GitFileStatus,
    GitStatus,
)


class TestGitFileStatus:
    """Tests for GitFileStatus class."""

    def test_init(self):
        """Test initialization of GitFileStatus."""
        # Test with minimal parameters
        file_status = GitFileStatus(path="test.py")
        assert file_status.path == "test.py"
        assert file_status.original_path is None
        assert file_status.staged is False

        # Test with all parameters
        file_status = GitFileStatus(
            path="new_file.py", 
            original_path="old_file.py", 
            staged=True
        )
        assert file_status.path == "new_file.py"
        assert file_status.original_path == "old_file.py"
        assert file_status.staged is True

    def test_display_path(self):
        """Test display_path property."""
        # Regular file
        file_status = GitFileStatus(path="test.py")
        assert file_status.display_path == "test.py"

        # Renamed file
        file_status = GitFileStatus(
            path="new_file.py", 
            original_path="old_file.py"
        )
        assert file_status.display_path == "old_file.py -> new_file.py"


class TestGitStatus:
    """Tests for GitStatus class."""

    def test_init(self):
        """Test initialization of GitStatus."""
        # Default initialization
        status = GitStatus()
        assert status.added == []
        assert status.modified == []
        assert status.deleted == []
        assert status.renamed == []
        assert status.untracked == []

        # Initialization with values
        file1 = GitFileStatus(path="file1.py")
        file2 = GitFileStatus(path="file2.py")
        status = GitStatus(added=[file1], modified=[file2])
        assert status.added == [file1]
        assert status.modified == [file2]
        assert status.deleted == []
        assert status.renamed == []
        assert status.untracked == []

    def test_has_changes_without_changes(self):
        """Test has_changes method with no changes."""
        status = GitStatus()
        assert status.has_changes() is False

    def test_has_changes_with_changes(self):
        """Test has_changes method with changes."""
        file = GitFileStatus(path="file.py")
        
        # Test with added file
        status = GitStatus(added=[file])
        assert status.has_changes() is True
        
        # Test with modified file
        status = GitStatus(modified=[file])
        assert status.has_changes() is True
        
        # Test with deleted file
        status = GitStatus(deleted=[file])
        assert status.has_changes() is True
        
        # Test with renamed file
        status = GitStatus(renamed=[file])
        assert status.has_changes() is True
        
        # Test with untracked file
        status = GitStatus(untracked=[file])
        assert status.has_changes() is True

    def test_all_files(self):
        """Test all_files method."""
        # Empty status
        status = GitStatus()
        assert status.all_files() == set()
        
        # Status with files
        file1 = GitFileStatus(path="file1.py")
        file2 = GitFileStatus(path="file2.py")
        file3 = GitFileStatus(path="file3.py")
        file4 = GitFileStatus(path="file4.py")
        file5 = GitFileStatus(path="file5.py")
        
        status = GitStatus(
            added=[file1],
            modified=[file2],
            deleted=[file3],
            renamed=[file4],
            untracked=[file5]
        )
        
        expected_files = {"file1.py", "file2.py", "file3.py", "file4.py", "file5.py"}
        assert status.all_files() == expected_files


class TestGitCommands:
    """Tests for GitCommands class."""
    
    @patch("subprocess.run")
    def test_get_git_root_success(self, mock_run):
        """Test get_git_root with successful git command."""
        mock_result = MagicMock()
        mock_result.stdout = "/path/to/repo\n"
        mock_run.return_value = mock_result
        
        result = GitCommands.get_git_root()
        
        assert result == "/path/to/repo"
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--show-toplevel"], 
            capture_output=True, 
            text=True, 
            check=True
        )
    
    @patch("subprocess.run")
    @patch("os.getcwd")
    def test_get_git_root_failure(self, mock_getcwd, mock_run):
        """Test get_git_root with failed git command."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        mock_getcwd.return_value = "/current/dir"
        
        result = GitCommands.get_git_root()
        
        assert result == "/current/dir"
    
    @patch("fcship.commands.commit.utils.GitCommands.get_git_root")
    def test_get_relative_path(self, mock_get_git_root):
        """Test get_relative_path method."""
        mock_get_git_root.return_value = "/path/to/repo"
        
        with patch("os.path.relpath") as mock_relpath:
            mock_relpath.return_value = "relative/path"
            result = GitCommands.get_relative_path("/path/to/repo/relative/path")
            assert result == "relative/path"
    
    @patch("fcship.commands.commit.utils.GitCommands.get_git_root")
    def test_get_relative_path_error(self, mock_get_git_root):
        """Test get_relative_path with ValueError."""
        mock_get_git_root.return_value = "/path/to/repo"
        
        with patch("os.path.relpath") as mock_relpath:
            mock_relpath.side_effect = ValueError("Path error")
            result = GitCommands.get_relative_path("/some/unrelated/path")
            assert result == "/some/unrelated/path"
    
    @patch("fcship.commands.commit.utils.GitCommands.get_git_root")
    @patch("subprocess.run")
    @patch("os.chdir")
    def test_run_git_command(self, mock_chdir, mock_run, mock_get_git_root):
        """Test run_git_command method."""
        mock_get_git_root.return_value = "/path/to/repo"
        mock_result = MagicMock()
        mock_result.stdout = "command output"
        mock_result.stderr = "error output"
        mock_run.return_value = mock_result
        
        with patch("os.getcwd") as mock_getcwd:
            mock_getcwd.return_value = "/current/dir"
            
            stdout, stderr = GitCommands.run_git_command(["git", "status"])
            
            assert stdout == "command output"
            assert stderr == "error output"
            mock_chdir.assert_any_call("/path/to/repo")
            mock_chdir.assert_any_call("/current/dir")
            mock_run.assert_called_once_with(
                ["git", "status"], 
                capture_output=True, 
                text=True, 
                check=True
            )

    @patch("fcship.commands.commit.utils.GitCommands.run_git_command")
    def test_get_status_empty(self, mock_run_git_command):
        """Test get_status with empty git status."""
        # Mock detect_renames_with_similarity
        with patch("fcship.commands.commit.utils.GitCommands.detect_renames_with_similarity") as mock_detect:
            mock_detect.return_value = {}
            
            # Mock run_git_command for git status
            mock_run_git_command.return_value = ("", "")
            
            status = GitCommands.get_status()
            
            assert isinstance(status, GitStatus)
            assert status.added == []
            assert status.modified == []
            assert status.deleted == []
            assert status.renamed == []
            assert status.untracked == []
            assert not status.has_changes()

    @patch("fcship.commands.commit.utils.GitCommands.run_git_command")
    def test_get_status_with_changes(self, mock_run_git_command):
        """Test get_status with various file statuses."""
        # Mock detect_renames_with_similarity
        with patch("fcship.commands.commit.utils.GitCommands.detect_renames_with_similarity") as mock_detect:
            mock_detect.return_value = {"new_file.py": "old_file.py"}
            
            # Create git status output
            status_output = "\n".join([
                "A  added.py",       # Staged new file
                "M  modified.py",    # Staged modified file
                " M unstaged.py",    # Unstaged modified file
                "D  deleted.py",     # Staged deleted file
                "?? untracked.py",   # Untracked file
            ])
            
            # Mock run_git_command for git status
            mock_run_git_command.return_value = (status_output, "")
            
            # Mock get_file_diff to check for modifications after rename
            with patch("fcship.commands.commit.utils.GitCommands.get_file_diff") as mock_diff:
                mock_diff.return_value = "diff content"
                
                status = GitCommands.get_status()
                
                assert isinstance(status, GitStatus)
                assert len(status.added) == 1
                assert status.added[0].path == "added.py"
                assert status.added[0].staged is True
                
                assert len(status.modified) == 3  # Including renamed with modifications
                assert any(f.path == "modified.py" for f in status.modified)
                assert any(f.path == "unstaged.py" for f in status.modified)
                assert any(f.path == "new_file.py" for f in status.modified)
                
                assert len(status.deleted) == 1
                assert status.deleted[0].path == "deleted.py"
                
                assert len(status.renamed) == 1
                assert status.renamed[0].path == "new_file.py"
                assert status.renamed[0].original_path == "old_file.py"
                
                assert len(status.untracked) == 1
                assert status.untracked[0].path == "untracked.py"
                
                assert status.has_changes()

    @patch("fcship.commands.commit.utils.GitCommands.run_git_command")
    def test_stage_file(self, mock_run_git_command):
        """Test stage_file method."""
        with patch("fcship.commands.commit.utils.GitCommands.get_relative_path") as mock_get_rel:
            mock_get_rel.return_value = "relative/path.py"
            
            GitCommands.stage_file("/absolute/path.py")
            
            mock_get_rel.assert_called_once_with("/absolute/path.py")
            mock_run_git_command.assert_called_once_with(
                ["git", "add", "--", "relative/path.py"], 
                check=False
            )

    @patch("fcship.commands.commit.utils.GitCommands.run_git_command")
    def test_unstage_file(self, mock_run_git_command):
        """Test unstage_file method."""
        with patch("fcship.commands.commit.utils.GitCommands.get_relative_path") as mock_get_rel:
            mock_get_rel.return_value = "relative/path.py"
            
            GitCommands.unstage_file("/absolute/path.py")
            
            mock_get_rel.assert_called_once_with("/absolute/path.py")
            mock_run_git_command.assert_called_once_with(
                ["git", "reset", "--", "relative/path.py"], 
                check=False
            )

    @patch("fcship.commands.commit.utils.GitCommands.run_git_command")
    def test_make_commit(self, mock_run_git_command):
        """Test make_commit method."""
        GitCommands.make_commit("Test commit message")
        
        mock_run_git_command.assert_called_once_with(
            ["git", "commit", "-m", "Test commit message"]
        )

    @patch("fcship.commands.commit.utils.GitCommands.run_git_command")
    def test_stage_changes(self, mock_run_git_command):
        """Test stage_changes method."""
        # Create a GitStatus with different types of changes
        rename_file = GitFileStatus(path="new.py", original_path="old.py")
        added_file = GitFileStatus(path="added.py")
        modified_file = GitFileStatus(path="modified.py")
        deleted_file = GitFileStatus(path="deleted.py")
        untracked_file = GitFileStatus(path="untracked.py")
        
        status = GitStatus(
            added=[added_file],
            modified=[modified_file],
            deleted=[deleted_file],
            renamed=[rename_file],
            untracked=[untracked_file]
        )
        
        # Mock stage_rename
        with patch("fcship.commands.commit.utils.GitCommands.stage_rename") as mock_stage_rename:
            # Mock stage_file
            with patch("fcship.commands.commit.utils.GitCommands.stage_file") as mock_stage_file:
                GitCommands.stage_changes(status)
                
                # Check stage_rename was called for renamed files
                mock_stage_rename.assert_called_once_with("old.py", "new.py")
                
                # Check stage_file was called for added, modified, and untracked files
                assert mock_stage_file.call_count == 3
                mock_stage_file.assert_any_call("added.py")
                mock_stage_file.assert_any_call("modified.py")
                mock_stage_file.assert_any_call("untracked.py")
                
                # Check git rm was called for deleted files
                mock_run_git_command.assert_called_once_with(
                    ["git", "rm", "--cached", "deleted.py"], 
                    check=False
                )