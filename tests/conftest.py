"""Common test configurations and fixtures."""

from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from expression import Error, Ok, Result
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from fcship.tui import DisplayError


@pytest.fixture
def mock_console(monkeypatch) -> Generator[MagicMock, None, None]:
    """Mock for rich console."""
    console_mock = MagicMock(spec=Console)
    with patch("fcship.tui.display.console", console_mock):
        yield console_mock


@pytest.fixture
def mock_table() -> Table:
    """Create a fresh table for testing."""
    table = Table()
    table.add_column("Test")
    table.add_column("Status")
    return table


def verify_table_structure(table: Table, expected_columns: list[tuple[str, str | None]]) -> None:
    """Verify table column structure."""
    assert len(table.columns) == len(expected_columns)
    for col, (name, style) in zip(table.columns, expected_columns, strict=False):
        assert col.header == name
        if style:
            assert col.style == style


def verify_panel_structure(panel: Panel, expected_title: str, expected_style: str) -> None:
    """Verify panel structure."""
    assert isinstance(panel, Panel)
    assert panel.title == expected_title
    assert panel.border_style == expected_style


@pytest.fixture
def mock_user_input(monkeypatch) -> Callable[..., None]:
    """Mock user input for testing."""
    inputs = []

    def mock_input(prompt: str = "") -> str:
        if not inputs:
            raise ValueError("No more inputs provided")
        return inputs.pop(0)

    monkeypatch.setattr("builtins.input", mock_input)

    def provide_inputs(*values: str) -> None:
        inputs.extend(values)

    return provide_inputs


@pytest.fixture
def mock_ui_operation() -> Generator[Any, None, None]:
    """Create a mock UI operation for testing error handling."""

    class MockUIOperation:
        def __init__(self) -> None:
            self.call_count = 0
            self.should_succeed_after = 1

        def __call__(self) -> Result[str, DisplayError]:
            self.call_count += 1
            if self.call_count >= self.should_succeed_after:
                return Ok("success")
            return Error(DisplayError.Validation("Operation failed"))

        def set_success_after(self, attempts: int) -> None:
            self.should_succeed_after = attempts

    yield MockUIOperation()
