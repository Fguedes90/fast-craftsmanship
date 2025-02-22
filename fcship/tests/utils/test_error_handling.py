"""Tests for error handling utilities."""
import pytest
from typer import BadParameter, Exit
from fcship.utils import error_handling


def test_validate_operation_valid():
    """Test validate_operation with valid input."""
    valid_ops = ["create", "update", "delete"]
    result = error_handling.validate_operation("create", valid_ops)
    assert result == "create"


def test_validate_operation_invalid():
    """Test validate_operation with invalid operation."""
    valid_ops = ["create", "update", "delete"]
    with pytest.raises(BadParameter) as exc_info:
        error_handling.validate_operation("invalid", valid_ops)
    assert "Invalid operation" in str(exc_info.value)


def test_validate_operation_missing_required_name():
    """Test validate_operation when name is required but not provided."""
    valid_ops = ["create", "update"]
    requires_name = ["create"]
    with pytest.raises(BadParameter) as exc_info:
        error_handling.validate_operation("create", valid_ops, name=None, requires_name=requires_name)
    assert "requires a name parameter" in str(exc_info.value)


def test_handle_command_errors_sync_success():
    """Test handle_command_errors with successful sync function."""
    @error_handling.handle_command_errors
    def successful_function():
        return "success"

    result = successful_function()
    assert result == "success"


def test_handle_command_errors_sync_failure():
    """Test handle_command_errors with failing sync function."""
    @error_handling.handle_command_errors
    def failing_function():
        raise ValueError("test error")

    with pytest.raises(Exit):
        failing_function()


@pytest.mark.asyncio
async def test_handle_command_errors_async_success():
    """Test handle_command_errors with successful async function."""
    @error_handling.handle_command_errors
    async def successful_async_function():
        return "async success"

    result = await successful_async_function()
    assert result == "async success"


@pytest.mark.asyncio
async def test_handle_command_errors_async_failure():
    """Test handle_command_errors with failing async function."""
    @error_handling.handle_command_errors
    async def failing_async_function():
        raise ValueError("async test error")

    with pytest.raises(Exit):
        await failing_async_function()



