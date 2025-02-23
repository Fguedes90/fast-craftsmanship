"""Unit tests for file_utils.py module."""
from pathlib import Path
import sys
import pytest
from expression import Ok, Error, Some
from expression.collections import Map, Block
import typer
from fcship.utils.file_utils import (
    FileError,
    FileOperation,
    ensure_directory,
    write_file,
    create_single_file,
    create_files,
    validate_operation
)

def test_file_error_model():
    """Test FileError model creation and immutability."""
    error = FileError(message="test error", path="/test/path")
    assert error.message == "test error"
    assert error.path == "/test/path"

def test_file_creation_tracker():
    """Test FileCreationTracker functionality."""
    # Test initialization
    result = init_file_creation_tracker()
    assert result.is_ok()
    tracker = result.ok
    assert isinstance(tracker.files, Map)
    assert len(tracker.files) == 0
    
    # Test adding files
    result = tracker.add_file("/test/file.txt")
    assert result.is_ok()
    updated = result.ok
    assert len(updated.files) == 1
    assert updated.files["/test/file.txt"] == "Created"
    
    # Test immutability
    assert len(tracker.files) == 0
    
    # Test custom status
    result = updated.add_file("/test/file2.txt", "Pending")
    assert result.is_ok()
    assert result.ok.files["/test/file2.txt"] == "Pending"

def test_ensure_directory(tmp_path):
    """Test directory creation functionality."""
    test_dir = tmp_path / "test_dir"
    
    # Test successful creation
    result = ensure_directory(test_dir / "test.txt")
    assert result.is_ok()
    assert test_dir.exists()
    
    # Test with existing directory
    result = ensure_directory(test_dir / "test.txt")
    assert result.is_ok()

def test_write_file(tmp_path):
    """Test file writing functionality."""
    test_file = tmp_path / "test.txt"
    content = "test content"
    
    # Test successful write
    result = write_file(test_file, content)
    assert result.is_ok()
    assert test_file.read_text() == content
    
    # Test write to readonly directory
    if not sys.platform.startswith('win'):  # Skip on Windows
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir(mode=0o444)
        result = write_file(readonly_dir / "test.txt", content)
        assert result.is_error()
        assert isinstance(result.error, FileError)

def test_create_single_file(tmp_path):
    """Test single file creation."""
    test_file = tmp_path / "test.txt"
    content = "test content"
    
    result = create_single_file(tmp_path, ("test.txt", content))
    assert result.is_ok()
    op = result.ok
    assert op.path == test_file
    assert op.content == content
    assert test_file.read_text() == content

def test_create_files(tmp_path):
    """Test multiple file creation."""
    files = Map.of_seq([
        ("file1.txt", "content1"),
        ("nested/file2.txt", "content2")
    ])
    
    # Test successful creation
    result = create_files(files, str(tmp_path))
    assert result.is_ok()
    assert len(result.ok.files) == 2
    
    # Verify files were created
    assert (tmp_path / "file1.txt").read_text() == "content1"
    assert (tmp_path / "nested/file2.txt").read_text() == "content2"

def test_validate_operation():
    """Test operation validation."""
    valid_ops = Block.of("create", "update", "delete")
    requires_name = Block.of("update", "delete")
    
    # Test valid operation without name requirement
    result = validate_operation(valid_ops, requires_name, "create", None)
    assert result.is_ok()
    
    # Test valid operation with required name
    result = validate_operation(valid_ops, requires_name, "update", None)
    assert result.is_error()
    assert isinstance(result.error, typer.BadParameter)
    
    # Test invalid operation
    result = validate_operation(valid_ops, requires_name, "invalid", None)
    assert result.is_error()
    assert isinstance(result.error, typer.BadParameter)
    assert "Invalid operation" in str(result.error)

def test_create_files_error_handling(tmp_path):
    """Test error handling in create_files."""
    # Test with invalid directory permissions
    if not sys.platform.startswith('win'):
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir(mode=0o444)
        files = Map.of_seq([("test.txt", "content")])
        
        result = create_files(files, str(readonly_dir))
        assert result.is_error()
        assert isinstance(result.error, FileError)

def test_create_files_empty():
    """Test create_files with empty input."""
    result = create_files(Map.empty())
    assert result.is_ok()
    assert len(result.ok.files) == 0

def test_file_creation_tracker_multiple_files():
    """Test FileCreationTracker with multiple files."""
    init_result = init_file_creation_tracker()
    assert init_result.is_ok()
    tracker = init_result.ok
    
    # Add multiple files
    result1 = tracker.add_file("/test/file1.txt")
    assert result1.is_ok()
    result2 = result1.ok.add_file("/test/file2.txt", "Pending")
    assert result2.is_ok()
    result3 = result2.ok.add_file("/test/file3.txt", "Skipped")
    assert result3.is_ok()
    
    final_tracker = result3.ok
    assert len(final_tracker.files) == 3
    assert final_tracker.files["/test/file1.txt"] == "Created"
    assert final_tracker.files["/test/file2.txt"] == "Pending"
    assert final_tracker.files["/test/file3.txt"] == "Skipped"

@pytest.mark.parametrize("operation,name,expected_ok,error_message", [
    ("create", None, True, None),
    ("update", "test", True, None),
    ("delete", "test", True, None),
    ("update", None, False, "Operation 'update' requires name"),
    ("invalid", None, False, "Invalid operation: invalid"),
    ("delete", None, False, "Operation 'delete' requires name"),
])
def test_validate_operation_with_messages(operation, name, expected_ok, error_message):
    """Parametrized tests for operation validation with error messages."""
    valid_ops = Block.of("create", "update", "delete")
    requires_name = Block.of("update", "delete")
    
    result = validate_operation(valid_ops, requires_name, operation, name)
    assert result.is_ok() == expected_ok
    if error_message:
        assert error_message in str(result.error)
