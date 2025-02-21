"""Test cases for file utilities."""
import pytest
import os
import tempfile
from pathlib import Path
from fcship.utils.file_utils import (
    ensure_directory,
    FileCreationTracker,
    file_creation_status,
    create_files
)

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

def test_ensure_directory_creates_new(temp_dir):
    """Test ensure_directory creates a new directory."""
    new_dir = temp_dir / "test_dir"
    ensure_directory(new_dir)
    assert new_dir.exists()
    assert new_dir.is_dir()

def test_ensure_directory_existing(temp_dir):
    """Test ensure_directory with existing directory."""
    existing_dir = temp_dir / "existing"
    existing_dir.mkdir()
    ensure_directory(existing_dir)
    assert existing_dir.exists()
    assert existing_dir.is_dir()

def test_file_creation_tracker():
    """Test FileCreationTracker functionality."""
    tracker = FileCreationTracker()
    
    # Test successful file creation
    tracker.add_success("file1.py")
    assert tracker.successes == ["file1.py"]
    assert not tracker.failures
    
    # Test failed file creation
    tracker.add_failure("file2.py", "Permission denied")
    assert "file2.py" in tracker.failures
    assert "Permission denied" in tracker.failures["file2.py"]

def test_file_creation_status():
    """Test file_creation_status output formatting."""
    tracker = FileCreationTracker()
    tracker.add_success("success.py")
    tracker.add_failure("failed.py", "Error message")
    
    status = file_creation_status(tracker)
    assert isinstance(status, str)
    assert "success.py" in status
    assert "failed.py" in status
    assert "Error message" in status

def test_create_files(temp_dir):
    """Test create_files function."""
    files = {
        "test1.txt": "content1",
        "subdir/test2.txt": "content2"
    }
    
    tracker = create_files(str(temp_dir), files)
    
    # Verify files were created
    file1_path = temp_dir / "test1.txt"
    file2_path = temp_dir / "subdir/test2.txt"
    assert file1_path.exists()
    assert file2_path.exists()
    
    # Verify tracker status
    assert "test1.txt" in tracker.successes
    assert "subdir/test2.txt" in tracker.successes
    
    # Verify file contents
    assert file1_path.read_text() == "content1"
    assert file2_path.read_text() == "content2"

def test_create_files_with_failure(temp_dir):
    """Test create_files with write permission failure."""
    # Create a read-only directory
    readonly_dir = temp_dir / "readonly"
    readonly_dir.mkdir()
    os.chmod(readonly_dir, 0o444)
    
    files = {
        "readonly/test.txt": "content"
    }
    
    tracker = create_files(str(temp_dir), files)
    assert "readonly/test.txt" in tracker.failures