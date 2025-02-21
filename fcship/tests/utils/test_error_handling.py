"""Test cases for error handling utilities."""
import pytest
import asyncio
import typer
from fcship.utils.error_handling import handle_command_errors

def test_handle_command_errors_sync_success():
    """Test handle_command_errors with successful sync function."""
    @handle_command_errors
    def success_fn():
        return "success"
    
    result = success_fn()
    assert result == "success"

def test_handle_command_errors_sync_failure():
    """Test handle_command_errors with failing sync function."""
    @handle_command_errors
    def failing_fn():
        raise ValueError("test error")
    
    with pytest.raises(typer.Exit):
        failing_fn()

@pytest.mark.asyncio
async def test_handle_command_errors_async_success():
    """Test handle_command_errors with successful async function."""
    @handle_command_errors
    async def success_fn():
        return "success"
    
    result = await success_fn()
    assert result == "success"

@pytest.mark.asyncio
async def test_handle_command_errors_async_failure():
    """Test handle_command_errors with failing async function."""
    @handle_command_errors
    async def failing_fn():
        raise ValueError("test error")
    
    with pytest.raises(typer.Exit):
        await failing_fn()

def test_handle_command_errors_preserves_typer_exit():
    """Test handle_command_errors preserves typer.Exit exceptions."""
    @handle_command_errors
    def exit_fn():
        raise typer.Exit(1)
    
    with pytest.raises(typer.Exit):
        exit_fn()

@pytest.mark.asyncio
async def test_handle_command_errors_async_preserves_typer_exit():
    """Test handle_command_errors preserves typer.Exit in async functions."""
    @handle_command_errors
    async def exit_fn():
        raise typer.Exit(1)
    
    with pytest.raises(typer.Exit):
        await exit_fn()