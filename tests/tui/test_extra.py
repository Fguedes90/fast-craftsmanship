import pytest
from expression import Ok, Error, Result, effect
from fcship.tui.extra import (
    UIOperation,
    UIError,
    ui_context_manager,
    handle_ui_error,
    with_fallback,
    with_ui_context,
)
from fcship.tui.errors import DisplayError

def test_ui_error_creation():
    """Test creation of different UI error types"""
    # Test validation error
    error = UIError.Validation("Invalid input")
    assert error.tag == "validation"
    assert error.validation == "Invalid input"

    # Test rendering error
    exc = Exception("Test exception")
    error = UIError.Rendering("Render failed", exc)
    assert error.tag == "rendering"
    assert error.rendering == ("Render failed", exc)

    # Test operation error
    error = UIError.Operation("Operation failed", exc)
    assert error.tag == "operation"
    assert error.operation == ("Operation failed", exc)

def test_ui_operation_creation():
    """Test creation of UI operations"""
    def operation():
        return Ok("success")

    def setup():
        return Ok(None)

    def cleanup():
        return Ok(None)

    # Test with all components
    ui_op = UIOperation(
        operation=operation,
        setup=setup,
        cleanup=cleanup
    )
    assert ui_op.operation is operation
    assert ui_op.setup is setup
    assert ui_op.cleanup is cleanup

    # Test with only operation
    ui_op = UIOperation(operation=operation)
    assert ui_op.operation is operation
    assert ui_op.setup is None
    assert ui_op.cleanup is None

def test_ui_context_manager():
    """Test UI context manager"""
    with ui_context_manager():
        # Context should be established
        pass
    # Context should be cleaned up

def test_handle_ui_error():
    """Test handling UI errors"""
    result = handle_ui_error(ValueError("Test error"))
    assert result.is_error()
    assert result.error.tag == "validation"
    assert "Test error" == result.error.validation

def test_with_fallback():
    """Test fallback mechanism"""
    # Test successful operation
    def success_op():
        return Ok("success")
    
    result = with_fallback(success_op, "fallback")
    assert result == "success"

    # Test failed operation
    def failed_op():
        return Error(DisplayError.Validation("Failed"))
    
    result = with_fallback(failed_op, "fallback")
    assert result == "fallback"

    # Test with error message
    result = with_fallback(failed_op, "fallback", "Operation failed")
    assert result == "fallback"

def test_with_ui_context_success():
    """Test successful UI context execution"""
    result = with_ui_context(lambda: "success")
    assert result.is_ok()
    assert result.ok == "success"

def test_with_ui_context_setup_error():
    """Test UI context with setup error"""
    def setup_error():
        raise ValueError("Setup failed")
    result = with_ui_context(lambda: "success", setup=setup_error)
    assert result.is_error()
    assert result.error.tag == "rendering"
    assert "Setup failed" in str(result.error)

def test_with_ui_context_operation_error():
    """Test UI context with operation error"""
    def operation_error():
        raise ValueError("Operation failed")
    result = with_ui_context(operation_error)
    assert result.is_error()
    assert result.error.tag == "rendering"
    assert "Operation failed" in str(result.error)

def test_with_ui_context_cleanup_error():
    """Test UI context with cleanup error"""
    def cleanup_error():
        raise ValueError("Cleanup failed")
    result = with_ui_context(lambda: "success", cleanup=cleanup_error)
    assert result.is_error()
    assert result.error.tag == "rendering"
    assert "Cleanup failed" in str(result.error)

def test_with_ui_context_error_handling():
    """Test UI context error handling"""
    def invalid_operation():
        raise ValueError("Invalid value")
    result = with_ui_context(invalid_operation)
    assert result.is_error()
    assert result.error.tag == "rendering"
    assert "Invalid value" in str(result.error) 