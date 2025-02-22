"""Test cases for error handling utilities."""
import pytest
import asyncio
import typer
from fcship.utils.error_handling import handle_command_errors

import pytest
import typer
from fcship.utils.error_handling import handle_command_errors

@pytest.mark.parametrize("exc", [ValueError("test error"), typer.Exit(1)])
def test_handle_command_errors_sync_failure(exc: Exception) -> None:
    """Testa que funções síncronas decoradas transformam quaisquer exceções em typer.Exit."""
    @handle_command_errors
    def failing_fn() -> str:
        raise exc

    with pytest.raises(typer.Exit):
        failing_fn()

def test_handle_command_errors_sync_success():
    """Test handle_command_errors with successful sync function."""
    @handle_command_errors
    def success_fn():
        return "success"

    result = success_fn()
    assert result == "success"


import pytest
import typer
import asyncio
from fcship.utils.error_handling import handle_command_errors

@pytest.mark.asyncio
@pytest.mark.parametrize("exc", [ValueError("test error"), typer.Exit(1)])
async def test_handle_command_errors_async_failure(exc: Exception) -> None:
    """Testa que funções assíncronas decoradas transformam quaisquer exceções em typer.Exit."""
    @handle_command_errors
    async def failing_fn() -> str:
        raise exc

    with pytest.raises(typer.Exit):
        await failing_fn()

@pytest.mark.asyncio
async def test_handle_command_errors_async_success():
    """Test handle_command_errors with successful async function."""
    @handle_command_errors
    async def success_fn():
        return "success"

    result = await success_fn()
    assert result == "success"



