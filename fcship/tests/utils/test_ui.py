"""Unit tests for UI utilities."""
from typing import Any
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from hypothesis import given, strategies as st, settings, HealthCheck
from expression import Result, Ok, Error
from expression.collections import Block
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Import test utilities from conftest
from ..conftest import (
    mock_ui_operation,
    mock_user_input
)

from fcship.utils.ui import (
    DisplayError,
    validate_input,
    display_message,
    success_message,
    error_message,
    warning_message,
    create_table_row,
    add_row_to_table,
    create_panel,
    create_summary_table,
    format_message,
    display_table,
    confirm_action,
    display_rule,
    batch_display_messages,
    create_multi_column_table,
    prompt_for_input,
    display_indented_text,
    create_nested_panel,
    display_progress,
    with_fallback,
    with_retry,
    handle_ui_error,
    aggregate_errors,
    recover_ui,
    safe_display,
    with_ui_context,
    is_valid_style,
    console,
    run_with_timeout,
    is_table_row,
    validate_table_data,
    validate_progress_inputs,
    validate_style,
    validate_panel_inputs,
    VALID_STYLES
)

############################################
# Strategy Definitions
############################################

def display_error_strategy() -> st.SearchStrategy[DisplayError]:
    """Generate valid display errors."""
    return st.one_of(
        st.builds(lambda m: DisplayError.Validation(m), st.text(min_size=1)),
        st.builds(lambda m, e: DisplayError.Rendering(m, Exception(e)), st.text(min_size=1), st.text()),
        st.builds(lambda m, e: DisplayError.Execution(m, e), st.text(min_size=1), st.text())
    )

def table_row_strategy() -> st.SearchStrategy[tuple[str, Result[str, Any]]]:
    """Generate valid table row data."""
    return st.tuples(
        st.text(min_size=1),
        st.one_of(
            st.builds(lambda x: Ok(x), st.text()),
            st.builds(lambda x: Error(x), st.text())
        )
    )

def valid_style_strategy() -> st.SearchStrategy[str]:
    """Generate valid style strings."""
    return st.sampled_from(VALID_STYLES)

def invalid_style_strategy() -> st.SearchStrategy[str]:
    """Generate invalid style strings."""
    return st.text(min_size=1).filter(lambda x: not is_valid_style(x))

def table_row_tuple_strategy() -> st.SearchStrategy[tuple[str, str]]:
    """Generate valid table row tuples."""
    return st.tuples(st.text(min_size=1), st.text(min_size=1))

def invalid_table_row_strategy() -> st.SearchStrategy[Any]:
    """Generate invalid table row data."""
    return st.one_of(
        st.text(),
        st.integers(),
        st.tuples(st.integers(), st.text()),
        st.lists(st.text(), min_size=3, max_size=3)
    )

############################################
# Helper Functions
############################################

def verify_table_structure(table: Table, expected_columns: list[tuple[str, str | None]]) -> None:
    """Verify table column structure."""
    assert len(table.columns) == len(expected_columns)
    for (col, (name, style)) in zip(table.columns, expected_columns):
        assert col.header == name
        if style:
            assert col.style == style

def verify_panel_structure(panel: Panel, expected_title: str, expected_style: str) -> None:
    """Verify panel structure."""
    assert isinstance(panel, Panel)
    assert panel.title == expected_title
    assert panel.border_style == expected_style

############################################
# Fixtures
############################################

@pytest.fixture
def mock_console(monkeypatch) -> MagicMock:
    """Mock Rich console for testing."""
    mock = MagicMock()
    monkeypatch.setattr("fcship.utils.ui.console", mock)
    return mock

@pytest.fixture
def mock_table() -> Table:
    """Create a mock table for testing."""
    table = Table()
    table.add_column("Test")
    table.add_column("Status")
    return table

############################################
# Input Validation Tests
############################################

@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.one_of(st.none(), st.text(min_size=1)))
def test_validate_input_properties(value: str | None) -> None:
    """Test validate_input with property-based testing."""
    result = validate_input(value, "Test")
    if value:
        assert result.is_ok()
        assert result.ok == value
    else:
        assert result.is_error()
        assert "Test cannot be empty" in str(result.error)

############################################
# Display Error Tests
############################################

@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(display_error_strategy())
def test_display_error_properties(error: DisplayError) -> None:
    """Test DisplayError properties with different error types."""
    match error:
        case DisplayError(tag="validation", validation=msg):
            assert error.tag == "validation"
            assert error.validation == msg
        case DisplayError(tag="rendering", rendering=(msg, _)):
            assert error.tag == "rendering"
            assert msg in str(error)
        case DisplayError(tag="execution", execution=(msg, _)):
            assert error.tag == "execution"
            assert msg in str(error)

############################################
# Message Display Tests
############################################

@pytest.mark.asyncio
async def test_display_message_empty() -> None:
    """Test display_message with empty input."""
    result = await display_message("")
    assert result.is_ok()
    assert result.ok is None

@pytest.mark.asyncio
async def test_display_message(mock_console: MagicMock) -> None:
    """Test message display with different styles."""
    message = "Test message"
    result = await display_message(message, "green")
    assert result.is_ok()
    mock_console.print.assert_called_once_with(f"[green]{message}[/green]")

@pytest.mark.asyncio
async def test_success_message(mock_console: MagicMock) -> None:
    """Test success message display."""
    message = "Success!"
    result = await success_message(message)
    assert result.is_ok()
    mock_console.print.assert_called_once_with(f"[green]{message}[/green]")

@pytest.mark.asyncio
async def test_error_message(mock_console: MagicMock) -> None:
    """Test error message display."""
    message = "Error!"
    details = "Details"
    result = await error_message(message, details)
    assert result.is_ok()
    assert mock_console.print.call_count == 2

@pytest.mark.asyncio
async def test_warning_message(mock_console: MagicMock) -> None:
    """Test warning message display."""
    message = "Warning!"
    result = await warning_message(message)
    assert result.is_ok()
    mock_console.print.assert_called_once_with(f"[yellow]{message}[/yellow]")

############################################
# Progress Display Tests
############################################

@pytest.mark.asyncio
async def test_display_progress_success(mock_console: MagicMock) -> None:
    """Test progress display with successful operations."""
    items = ["item1", "item2"]
    async def process(item: str) -> Result[str, str]:
        return Ok(f"Processed {item}")
    
    result = await display_progress(items, process, "Processing items")
    assert result.is_ok()

@pytest.mark.asyncio
async def test_display_progress_error(mock_console: MagicMock) -> None:
    """Test progress display with failing operations."""
    items = ["item1", "item2"]
    async def process(item: str) -> Result[str, str]:
        return Error(f"Failed {item}")
    
    result = await display_progress(items, process, "Processing items")
    assert result.is_error()
    assert result.error.tag == "execution"

@pytest.mark.asyncio
async def test_display_progress_exception(mock_console: MagicMock) -> None:
    """Test progress display with exception."""
    items = ["test1", "test2"]
    async def process(item: str) -> Result[str, str]:
        raise Exception("Process failed")
    
    result = await display_progress(items, process, "Processing items")
    assert result.is_error()
    assert result.error.tag == "rendering"

############################################
# Safe Display Tests
############################################

@pytest.mark.asyncio
async def test_safe_display_success() -> None:
    """Test safe display with successful operation."""
    async def success_fn() -> Result[str, DisplayError]:
        return Ok("Success")
    
    result = await safe_display(success_fn)
    assert result.is_ok()
    assert result.ok == "Success"

@pytest.mark.asyncio
async def test_safe_display_error() -> None:
    """Test safe display with failing operation."""
    async def error_fn() -> Result[str, DisplayError]:
        raise Exception("Test error")
    
    result = await safe_display(error_fn)
    assert result.is_error()
    assert result.error.tag == "rendering"

############################################
# Context Management Tests
############################################

def test_with_ui_context(mock_console: MagicMock) -> None:
    """Test UI context management."""
    with with_ui_context():
        mock_console.print("Test")
    
    assert mock_console.clear.call_count == 2

def test_with_ui_context_error(mock_console: MagicMock) -> None:
    """Test UI context management with error."""
    try:
        with with_ui_context():
            raise Exception("Test error")
    except Exception:
        pass
    
    assert mock_console.clear.call_count == 2

############################################
# Table Creation Tests
############################################

def test_create_table_row_properties() -> None:
    """Test create_table_row with property-based testing."""
    table_row = ("Test", Ok("Success"))
    result = create_table_row(table_row)
    
    assert result.is_ok()
    created_row = result.ok
    assert created_row[0] == "Test".title()
    assert "[green]" in created_row[1]

def test_add_row_to_table(mock_table: Table) -> None:
    """Test adding row to table."""
    row = ("Test", "Passed")
    result = add_row_to_table(mock_table, row)
    assert result.is_ok()
    verify_table_structure(result.ok, [("Test", None), ("Status", None)])

def test_create_summary_table_properties() -> None:
    """Test create_summary_table with property-based testing."""
    table_rows = [("Test1", Ok("Success")), ("Test2", Ok("Success")), ("Test3", Ok("Success"))]
    block_results = Block.of_seq(table_rows)
    table_result = create_summary_table(block_results)
    
    assert table_result.is_ok()
    table = table_result.ok
    assert len(table.columns) == 2
    assert table.columns[0].style == "cyan"
    assert table.columns[1].style == "bold"

############################################
# Panel Creation Tests
############################################

def test_create_panel_properties() -> None:
    """Test create_panel with property-based testing."""
    result = create_panel("Test Title", "Test Content", "blue")
    
    assert result.is_ok()
    verify_panel_structure(result.ok, "Test Title", "blue")

def test_create_panel_empty_title() -> None:
    """Test panel creation with empty title."""
    result = create_panel("", "content", "blue")
    assert result.is_error()
    assert result.error.tag == "validation"

def test_create_panel_empty_content() -> None:
    """Test panel creation with empty content."""
    result = create_panel("title", "", "blue")
    assert result.is_error()
    assert result.error.tag == "validation"

############################################
# Validation Tests
############################################

def test_validate_style() -> None:
    """Test style validation."""
    assert validate_style("red").is_ok()
    assert validate_style("invalid").is_error()

def test_validate_panel_inputs() -> None:
    """Test panel input validation."""
    result = validate_panel_inputs("Title", "Content", "red")
    assert result.is_ok()
    
    assert validate_panel_inputs("", "Content", "red").is_error()
    assert validate_panel_inputs("Title", "", "red").is_error()
    assert validate_panel_inputs("Title", "Content", "invalid").is_error()

def test_validate_progress_inputs() -> None:
    """Test progress inputs validation."""
    items = ["test1", "test2"]
    async def process(x: str) -> Result[str, str]:
        return Ok(x.upper())
    description = "Processing"
    
    result = validate_progress_inputs(items, process, description)
    assert result.is_ok()
    
    assert validate_progress_inputs([], process, description).is_error()
    assert validate_progress_inputs(items, None, description).is_error()  # type: ignore
    assert validate_progress_inputs(items, process, "").is_error()

def test_validate_table_data() -> None:
    """Test table data validation."""
    headers = ["Name", "Value"]
    valid_rows = [("test", "123"), ("foo", "bar")]
    assert validate_table_data(headers, valid_rows).is_ok()
    
    # Test invalid cases
    assert validate_table_data([], valid_rows).is_error()  # Empty headers
    assert validate_table_data(headers, []).is_error()  # Empty rows
    assert validate_table_data(headers, [("test",)]).is_error()  # Invalid row length
    assert validate_table_data(headers, [("test", "123", "extra")]).is_error()  # Invalid row length

############################################
# Error Handling Tests
############################################

def test_handle_ui_error(mock_console: MagicMock) -> None:
    """Test UI error handling."""
    validation_error = DisplayError.Validation("Invalid input")
    result = handle_ui_error(validation_error)
    assert result.is_error()
    assert result.error.tag == "validation"

    rendering_error = DisplayError.Rendering("Failed to render", Exception("Error"))
    result = handle_ui_error(rendering_error)
    assert result.is_error()
    assert result.error.tag == "rendering"

    execution_error = DisplayError.Execution("Operation failed", "Error")
    result = handle_ui_error(execution_error)
    assert result.is_error()
    assert result.error.tag == "execution"

############################################
# Integration Tests
############################################

@pytest.mark.asyncio
async def test_message_display_workflow(mock_console: MagicMock) -> None:
    """Test complete message display workflow."""
    results = [
        await success_message("Operation successful"),
        await warning_message("Proceed with caution"),
        await error_message("Operation failed", "Invalid input")
    ]
    assert all(r.is_ok() for r in results)
    assert mock_console.print.call_count == 4  # error_message with details makes two calls

@pytest.mark.asyncio
async def test_success_workflow() -> None:
    """Test success workflow with table display."""
    headers = [("Operation", None), ("Status", None)]
    rows = [["Create", "Success"], ["Update", "Success"]]
    table = create_multi_column_table(headers, rows)
    assert table.is_ok()
    
    result = await display_table(table.ok)
    assert result.is_ok()

@pytest.mark.asyncio
async def test_error_workflow() -> None:
    """Test error workflow."""
    result = await display_message(None)
    assert result.is_error()
    assert "Message cannot be None" in str(result.error)

############################################
# Property-Based Tests
############################################

@pytest.mark.asyncio
@given(st.lists(st.tuples(st.text(min_size=1), st.sampled_from(VALID_STYLES)), min_size=1))
async def test_batch_display_messages_properties(messages: list[tuple[str, str]]) -> None:
    """Test batch_display_messages with property-based testing."""
    result = batch_display_messages(messages)
    
    if all(msg[0] and msg[1] for msg in messages):
        assert result.is_ok()
    else:
        assert result.is_error()

@given(
    st.lists(st.tuples(st.text(min_size=1), st.text()),
    st.lists(st.lists(st.text(), min_size=1), min_size=1)
)
def test_create_multi_column_table_properties(
    columns: list[tuple[str, str | None]],
    rows: list[list[str]]
) -> None:
    """Test create_multi_column_table with property-based testing."""
    result = create_multi_column_table(columns, rows)
    
    if all(len(row) == len(columns) for row in rows):
        assert result.is_ok()
    else:
        assert result.is_error()

@pytest.mark.asyncio
@given(st.text(min_size=1), st.integers(min_value=0, max_value=10))
async def test_display_indented_text_properties(text: str, indent: int) -> None:
    """Test display_indented_text with property-based testing."""
    result = await display_indented_text(text, indent)
    if text:  # Non-empty text
        assert result.is_ok()
    else:
        assert result.is_error()

@given(st.text(min_size=1), st.lists(st.tuples(st.text(min_size=1), st.text(min_size=1)), min_size=1))
def test_create_nested_panel_properties(
    title: str, 
    sections: list[tuple[str, str]]
) -> None:
    """Test create_nested_panel with property-based testing."""
    result = create_nested_panel(title, sections)
    
    if all(title and content for title, content in sections):
        assert result.is_ok()
        panel = result.ok
        assert isinstance(panel, Panel)
        assert panel.title == title
        assert panel.border_style == "blue"
    else:
        assert result.is_error()
        assert result.error.tag == "validation"

############################################
# Recovery Tests
############################################

@pytest.mark.asyncio
async def test_retry_workflow() -> None:
    """Test retry workflow with mock operation."""
    def mock_operation() -> Result[str, DisplayError]:
        mock_operation.calls = getattr(mock_operation, 'calls', 0) + 1
        if mock_operation.calls >= 2:
            return Ok("success")
        return Error(DisplayError.Validation("Operation failed"))

    operations = [
        await with_retry(mock_operation, max_attempts=3),
        await with_retry(mock_operation, max_attempts=3, delay=0.1)
    ]
    
    assert all(r.is_ok() for r in operations)
    assert mock_operation.calls == 3  # First operation succeeds after 2 attempts, second after 1

def test_fallback_workflow() -> None:
    """Test fallback workflow."""
    operations = [
        with_fallback(lambda: Ok("primary"), "fallback"),
        with_fallback(lambda: Error(DisplayError.Validation("error")), "fallback")
    ]
    
    assert all(isinstance(r, str) for r in operations)
    assert operations[0] == "primary"
    assert operations[1] == "fallback"

############################################
# Timeout Tests
############################################

@pytest.mark.asyncio
async def test_effect_timeout_handling() -> None:
    """Test effect timeout handling with different timeouts."""
    async def slow_operation() -> Result[str, DisplayError]:
        await asyncio.sleep(0.2)
        return Ok("success")

    # Test timeout case
    result = await run_with_timeout(slow_operation(), timeout=0.1)
    assert result.is_error()
    assert result.error.tag == "timeout"
    assert result.error.timeout is not None
    assert "Operation timed out after 0.1 seconds" in result.error.timeout[0]

    # Test success case
    result = await run_with_timeout(slow_operation(), timeout=0.3)
    assert result.is_ok()
    assert result.ok == "success"

    # Test execution error case
    async def failing_operation() -> Result[str, DisplayError]:
        raise RuntimeError("Operation failed")

    result = await run_with_timeout(failing_operation(), timeout=0.1)
    assert result.is_error()
    assert result.error.tag == "execution"
    assert result.error.execution is not None
    assert "Operation failed" in result.error.execution[1]

############################################
# Type Guard Tests
############################################

def test_is_table_row() -> None:
    """Test table row type guard."""
    assert is_table_row(("test", "value"))
    assert not is_table_row(("test",))
    assert not is_table_row(["test", "value"])
    assert not is_table_row(("test", 123))

############################################
# Additional Display Tests
############################################

@pytest.mark.asyncio
async def test_display_rule_with_style() -> None:
    """Test rule display with style."""
    message = "Section Break"
    result = await display_rule(message, "red")
    assert result.is_ok()

@pytest.mark.asyncio
async def test_display_indented_text_error(mock_console: MagicMock) -> None:
    """Test indented text display error."""
    mock_console.print.side_effect = Exception("Display error")
    result = await display_indented_text("test")
    assert result.is_error()
    assert result.error.tag == "rendering"

############################################
# Additional Progress Tests
############################################

def test_display_progress_error() -> None:
    """Test progress display with errors."""
    items = ["test1", "test2"]
    def process_fn(x: str) -> Result[str, str]:
        if x == "test1":
            return Ok(x.upper())
        return Error("Failed")

    result = display_progress(items, process_fn)
    assert result.is_error()
    assert result.error.tag == "validation"

def test_display_progress_exception() -> None:
    """Test progress display with exception."""
    items = ["test1", "test2"]
    def process_fn(x: str) -> Result[str, str]:
        raise Exception("Process failed")

    result = display_progress(items, process_fn)
    assert result.is_error()
    assert result.error.tag == "rendering"

############################################
# Additional Safe Display Tests
############################################

def test_safe_display_with_error_aggregation() -> None:
    """Test safe display with error aggregation."""
    content = "test"
    display_fn = lambda x: Error(DisplayError.Validation("First error"))
    fallback_fn = lambda x: Error(DisplayError.Validation("Second error"))

    result = safe_display(content, display_fn, fallback_fn)
    assert result.is_error()
    assert "First error" in result.error.validation
    assert "Second error" in result.error.validation

############################################
# Additional Context Tests
############################################

def test_with_ui_context_error_handling() -> None:
    """Test UI context error handling."""
    def operation() -> Result[str, DisplayError]:
        return Ok("success")

    def failing_setup() -> Result[None, DisplayError]:
        raise IOError("Setup failed")

    def failing_cleanup() -> Result[None, DisplayError]:
        raise IOError("Cleanup failed")

    result = with_ui_context(operation, failing_setup, None)
    assert result.is_error()
    assert result.error.tag == "rendering"

    result = with_ui_context(operation, None, failing_cleanup)
    assert result.is_error()
    assert result.error.tag == "rendering"