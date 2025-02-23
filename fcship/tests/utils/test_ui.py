"""Unit tests for UI utilities."""
from typing import Any
from unittest.mock import MagicMock, patch
import pytest
from hypothesis import given, strategies as st
from expression import Result, Ok, Error, pipe, Try, effect
from expression.collections import seq, Block
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from fcship.utils.ui import (
    DisplayError,
    validate_input,
    display_message,
    success_message,
    error_message,
    create_table_row,
    add_row_to_table,
    create_panel,
    create_summary_table,
    format_message,
    display_table,
    confirm_action,
    display_rule,
    warning_message,
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
    console
)

# Valid styles for Rich (copied from ui.py to use in tests)
VALID_STYLES = {"red", "green", "blue", "yellow", "cyan", "magenta", "white", "black"}

############################################
# Strategy Definitions
############################################

def display_error_strategy() -> st.SearchStrategy[DisplayError]:
    """Generate valid display errors."""
    return st.one_of(
        st.builds(lambda m: DisplayError.Validation(m), st.text(min_size=1)),
        st.builds(lambda m, e: DisplayError.Rendering(m, Exception(e)), st.text(min_size=1), st.text()),
        st.builds(lambda m, e: DisplayError.Interaction(m, Exception(e)), st.text(min_size=1), st.text())
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

############################################
# Validation Function Strategies
############################################

def valid_style_strategy() -> st.SearchStrategy[str]:
    """Generate valid style strings."""
    return st.sampled_from(["red", "green", "blue", "yellow", "cyan", "magenta", "white", "black"])

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
# Input Validation Tests
############################################

@given(st.one_of(st.none(), st.text(min_size=1)))
def test_validate_input_properties(value: str | None) -> None:
    """Test validate_input with property-based testing."""
    result = validate_input(value, "Test")
    if value:
        assert result.is_ok()
        assert result.ok == value
    else:
        assert result.is_error()
        assert result.error.tag == "validation"

############################################
# Display Error Tests
############################################

@given(display_error_strategy())
def test_display_error_properties(error: DisplayError) -> None:
    """Test DisplayError properties with different error types."""
    match error:
        case DisplayError(tag="validation", validation=msg):
            assert error.validation == msg
            assert error.rendering is None
            assert error.interaction is None
            
        case DisplayError(tag="rendering", rendering=tup):
            msg, exc = tup
            assert error.rendering == (msg, exc)
            assert error.validation is None
            assert error.interaction is None
            
        case DisplayError(tag="interaction", interaction=tup):
            msg, exc = tup
            assert error.interaction == (msg, exc)
            assert error.validation is None
            assert error.rendering is None

############################################
# Message Display Tests
############################################

def test_display_message(mock_console: MagicMock) -> None:
    """Test message display with different styles."""
    message = "Test message"
    result = display_message(message, "green")
    assert result.is_ok()
    mock_console.print.assert_called_once()

def test_display_message_empty(mock_console: MagicMock) -> None:
    """Test empty message handling."""
    result = display_message("", "green")
    assert result.is_error()
    assert isinstance(result.error, ValueError)
    mock_console.print.assert_not_called()

def test_success_message(mock_console: MagicMock) -> None:
    """Test success message display."""
    message = "Success!"
    result = success_message(message)
    assert result.is_ok()
    mock_console.print.assert_called_once()

def test_success_message_empty() -> None:
    """Test empty success message."""
    result = success_message("")
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

def test_error_message_simple(mock_console: MagicMock) -> None:
    """Test error message without details."""
    message = "Error occurred"
    result = error_message(message)
    assert result.is_ok()
    mock_console.print.assert_called_once()

def test_error_message_with_details(mock_console: MagicMock) -> None:
    """Test error message with details."""
    message = "Error occurred"
    details = "More information"
    result = error_message(message, details)
    assert result.is_ok()
    mock_console.print.assert_called_once()

def test_error_message_empty() -> None:
    """Test empty error message."""
    result = error_message("")
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

def test_warning_message(mock_console: MagicMock) -> None:
    """Test warning message display."""
    message = "Warning!"
    result = warning_message(message)
    assert result.is_ok()
    mock_console.print.assert_called_once()

############################################
# Table Creation Tests
############################################

@given(table_row_strategy())
def test_create_table_row_properties(row_data: tuple[str, Result[str, Any]]) -> None:
    """Test create_table_row with property-based testing."""
    name, result = row_data
    row_result = create_table_row((name, result))
    
    assert row_result.is_ok()
    created_row = row_result.ok
    assert created_row[0] == name.title()  # Name should be title-cased
    assert "[green]" in created_row[1] if result.is_ok() else "[red]" in created_row[1]

def test_create_table_row_empty() -> None:
    """Test table row creation with empty name."""
    result = create_table_row(("", Ok("value")))
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

def test_add_row_to_table() -> None:
    """Test adding row to table."""
    table = Table()
    table.add_column("Test")
    table.add_column("Status")
    row = ("Test", "Passed")
    result = add_row_to_table(table, row)
    assert isinstance(result, Table)

def test_add_row_invalid_table() -> None:
    """Test adding row to invalid table object."""
    result = add_row_to_table("not a table", ("col1", "col2"))
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

@given(st.lists(table_row_strategy(), min_size=0, max_size=10))
def test_create_summary_table_properties(results: list[tuple[str, Result[str, Any]]]) -> None:
    """Test create_summary_table with property-based testing."""
    block_results = Block.of_seq(results)
    table_result = create_summary_table(block_results)
    
    assert table_result.is_ok()
    table = table_result.ok
    
    # Verify table structure
    assert len(table.columns) == 2  # Should have "Check" and "Status" columns
    assert table.columns[0].style == "cyan"
    assert table.columns[1].style == "bold"

def test_create_summary_table_invalid() -> None:
    """Test summary table creation with invalid input."""
    result = create_summary_table([])  # type: ignore
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

############################################
# Panel Creation Tests
############################################

@given(
    st.text(min_size=1),
    st.text(min_size=1),
    st.text(min_size=1)
)
def test_create_panel_properties(title: str, content: str, style: str) -> None:
    """Test create_panel with property-based testing."""
    result = create_panel(title, content, style)
    
    if style in VALID_STYLES:
        assert result.is_ok()
        panel = result.ok
        assert isinstance(panel, Panel)
        assert panel.title == title
        assert panel.border_style == style
    else:
        assert result.is_error()
        assert result.error.tag == "validation"

def test_create_panel_empty_title() -> None:
    """Test panel creation with empty title."""
    result = create_panel("", "content", "style")
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

def test_create_panel_empty_content() -> None:
    """Test panel creation with empty content."""
    result = create_panel("title", "", "style")
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

############################################
# Message Formatting Tests
############################################

@given(st.lists(st.text(), min_size=0, max_size=5))
def test_format_message_properties(parts: list[str]) -> None:
    """Test format_message with property-based testing."""
    result = format_message(parts)
    
    if any(parts):  # If there are any non-empty parts
        assert result.is_ok()
        formatted = result.ok
        # Check each non-empty part is in the formatted message
        for part in filter(None, parts):
            assert part in formatted
    else:
        assert result.is_error()
        assert result.error.tag == "validation"

def test_format_message_invalid_input() -> None:
    """Test message formatting with invalid input."""
    result = format_message("not a list")  # type: ignore
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

def test_format_message_empty_parts() -> None:
    """Test message formatting with empty parts."""
    result = format_message(["", "", ""])
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

############################################
# Table Display Tests
############################################

def test_display_table(mock_console: MagicMock) -> None:
    """Test table display."""
    headers = ["Column 1", "Column 2"]
    rows = [["Value 1", "Value 2"], ["Value 3", "Value 4"]]
    result = display_table(headers, rows, "Test Table")
    assert result.is_ok()
    mock_console.print.assert_called_once()

def test_display_table_empty_headers() -> None:
    """Test table display with empty headers."""
    result = display_table([], [])
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

def test_display_table_invalid_headers() -> None:
    """Test table display with invalid headers."""
    result = display_table([1, 2], [])  # type: ignore
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

def test_display_table_mismatched_rows() -> None:
    """Test table display with mismatched row lengths."""
    result = display_table(["h1", "h2"], [["v1"]])
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "rendering"

############################################
# User Interaction Tests
############################################

def test_confirm_action() -> None:
    """Test confirmation prompt."""
    with patch("typer.confirm", return_value=True) as mock_confirm:
        result = confirm_action("Proceed?")
        assert result.is_ok()
        assert result.ok is True
        mock_confirm.assert_called_once_with("Proceed?")

def test_confirm_action_empty() -> None:
    """Test confirmation with empty prompt."""
    result = confirm_action("")
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

############################################
# Rule Display Tests
############################################

def test_display_rule(mock_console: MagicMock) -> None:
    """Test rule display."""
    message = "Section Break"
    result = display_rule(message)
    assert result.is_ok()
    mock_console.rule.assert_called_once_with(message, style="blue")

def test_display_rule_empty() -> None:
    """Test rule display with empty message."""
    result = display_rule("")
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

############################################
# Error Handling Tests
############################################

def test_display_message_error() -> None:
    """Test handling of display errors."""
    with patch("rich.console.Console.print", side_effect=Exception("Display error")):
        result = display_message("Test", "red")
        assert result.is_error()
        assert isinstance(result.error, Exception)

def test_display_table_error(mock_console: MagicMock) -> None:
    """Test handling of table display errors."""
    mock_console.print.side_effect = Exception("Table error")
    headers = ["Test"]
    rows = [["Value"]]
    result = display_table(headers, rows)
    assert result.is_error()
    assert isinstance(result.error, Exception)

############################################
# Integration Tests
############################################

def test_message_display_workflow(mock_console: MagicMock) -> None:
    """Test complete message display workflow."""
    # Success path
    success = success_message("Operation successful")
    assert success.is_ok()
    
    # Warning path
    warning = warning_message("Proceed with caution")
    assert warning.is_ok()
    
    # Error path with details
    error = error_message("Operation failed", "Invalid input")
    assert error.is_ok()
    
    assert mock_console.print.call_count == 3

def test_table_display_workflow(mock_console: MagicMock) -> None:
    """Test complete table display workflow."""
    # Create and display summary table
    results = Block.of_seq([
        ("test1", Ok("Success")),
        ("test2", Error("Failed"))
    ])
    
    table = create_summary_table(results)
    result = pipe(
        table,
        lambda t: display_table(
            ["Check", "Status"],
            [[r[0], r[1]] for r in results],
            "Test Results"
        )
    )
    
    assert result.is_ok()
    assert mock_console.print.called

def test_error_workflow(mock_console: MagicMock) -> None:
    """Test complete error handling workflow."""
    # Empty input validation
    v1 = validate_input("", "test")
    assert v1.is_error()
    assert v1.error.tag == "validation"
    
    # Display error
    mock_console.print.side_effect = Exception("Display failed")
    v2 = success_message("test")
    assert v2.is_error()
    assert v2.error.tag == "rendering"
    
    # User interaction error
    with patch("typer.confirm", side_effect=Exception("Input failed")):
        v3 = confirm_action("test")
        assert v3.is_error()
        assert v3.error.tag == "interaction"

def test_success_workflow(mock_console: MagicMock) -> None:
    """Test complete success workflow."""
    # Valid input
    v1 = validate_input("test", "field")
    assert v1.is_ok()
    
    # Success message
    v2 = success_message("Operation complete")
    assert v2.is_ok()
    
    # Table creation and display
    results = Block.of_seq([("test", Ok("success"))])
    v3 = (create_summary_table(results)
          .bind(lambda t: display_table(["Check", "Status"], [["test", "✨ Passed"]], "Results")))
    assert v3.is_ok()

############################################
# Utility Function Tests
############################################

def test_batch_display_messages(mock_console: MagicMock) -> None:
    """Test batch message display."""
    messages = [
        ("Success", "green"),
        ("Warning", "yellow"),
        ("Error", "red")
    ]
    result = batch_display_messages(messages)
    assert result.is_ok()
    assert mock_console.print.call_count == len(messages)

def test_batch_display_messages_empty() -> None:
    """Test batch display with empty message."""
    messages = [("Valid", "green"), ("", "red")]
    result = batch_display_messages(messages)
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

def test_create_multi_column_table(mock_console: MagicMock) -> None:
    """Test multi-column table creation."""
    columns = [("Name", "cyan"), ("Status", "green")]
    rows = [["Test 1", "Pass"], ["Test 2", "Fail"]]
    result = create_multi_column_table(columns, rows, "Results")
    assert result.is_ok()
    assert isinstance(result.ok, Table)
    assert len(result.ok.columns) == 2

def test_create_multi_column_table_mismatched_rows() -> None:
    """Test table creation with mismatched rows."""
    columns = [("Col1", None), ("Col2", None)]
    rows = [["Value1"]]  # Missing second column
    result = create_multi_column_table(columns, rows)
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "rendering"

def test_prompt_for_input() -> None:
    """Test input prompt with validation."""
    with patch("builtins.input", return_value="test"):
        def validator(value: str) -> Result[str, str]:
            return Ok(value) if len(value) > 0 else Error("Empty input")
            
        result = prompt_for_input("Enter value: ", validator)
        assert result.is_ok()
        assert result.ok == "test"

def test_prompt_for_input_validation_failure() -> None:
    """Test input prompt with failed validation."""
    with patch("builtins.input", return_value=""):
        def validator(value: str) -> Result[str, str]:
            return Ok(value) if len(value) > 0 else Error("Empty input")
            
        result = prompt_for_input("Enter value: ", validator)
        assert result.is_error()
        assert isinstance(result.error, DisplayError)
        assert result.error.tag == "validation"

def test_display_indented_text(mock_console: MagicMock) -> None:
    """Test indented text display."""
    text = "Line 1\nLine 2"
    result = display_indented_text(text, indent=4)
    assert result.is_ok()
    mock_console.print.assert_called_once()

def test_display_indented_text_empty() -> None:
    """Test indented text display with empty input."""
    result = display_indented_text("")
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

def test_create_nested_panel() -> None:
    """Test nested panel creation."""
    sections = [
        ("Section 1", "Content 1"),
        ("Section 2", "Content 2")
    ]
    result = create_nested_panel("Main Title", sections)
    assert result.is_ok()
    assert isinstance(result.ok, Panel)

def test_create_nested_panel_empty_section() -> None:
    """Test nested panel with empty section."""
    sections = [
        ("Section 1", ""),
        ("Section 2", "Content 2")
    ]
    result = create_nested_panel("Main Title", sections)
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

@pytest.mark.parametrize("items,expected_error", [
    ([], False),
    ([1, 2, 3], False),
    ([1, None, 3], True)
])
def test_display_progress(
    mock_console: MagicMock,
    items: list[int | None],
    expected_error: bool
) -> None:
    """Test progress display with different inputs."""
    def process_item(x: int | None) -> Result[str, str]:
        return Ok(str(x)) if x is not None else Error("Invalid item")
        
    result = display_progress(items, process_item, "Processing items")
    
    if expected_error:
        assert result.is_error()
        assert isinstance(result.error, DisplayError)
        assert result.error.tag == "validation"
    else:
        assert result.is_ok()

############################################
# Property-Based Tests for New Functions
############################################

@given(st.lists(st.tuples(st.text(min_size=1), st.text(min_size=1)), min_size=1))
def test_batch_display_messages_properties(messages: list[tuple[str, str]]) -> None:
    """Test batch_display_messages with property-based testing."""
    result = batch_display_messages(messages)
    
    if all(msg and style for msg, style in messages):
        assert result.is_ok()
    else:
        assert result.is_error()
        assert result.error.tag == "validation"

@given(
    st.lists(st.tuples(st.text(min_size=1), st.text()), min_size=1),
    st.lists(st.lists(st.text(), min_size=1), min_size=1)
)
def test_create_multi_column_table_properties(
    columns: list[tuple[str, str | None]],
    rows: list[list[str]]
) -> None:
    """Test create_multi_column_table with property-based testing."""
    result = create_multi_column_table(columns, rows)
    
    # Test for valid table creation
    if len(rows[0]) == len(columns):
        assert result.is_ok()
        table = result.ok
        assert len(table.columns) == len(columns)
        for (header, style), col in zip(columns, table.columns):
            assert col.header == header
            if style:
                assert col.style == style
    else:
        assert result.is_error()
        assert result.error.tag == "rendering"

@given(st.text(min_size=1), st.integers(min_value=0, max_value=10))
def test_display_indented_text_properties(text: str, indent: int) -> None:
    """Test display_indented_text with property-based testing."""
    result = display_indented_text(text, indent)
    
    if text:
        assert result.is_ok()
        # Each line should be properly indented
        for line in text.splitlines():
            assert " " * indent + line in str(result)

@given(
    st.text(min_size=1),
    st.lists(
        st.tuples(st.text(min_size=1), st.text(min_size=1)),
        min_size=1
    )
)
def test_create_nested_panel_properties(title: str, sections: list[tuple[str, str]]) -> None:
    """Test create_nested_panel with property-based testing."""
    result = create_nested_panel(title, sections)
    
    if all(title and content for title, content in sections):
        assert result.is_ok()
        panel = result.ok
        assert isinstance(panel, Panel)
        assert panel.title == title
        # Verify each section is included in the panel content
        for section_title, section_content in sections:
            assert section_title in str(panel)
            assert section_content in str(panel)
    else:
        assert result.is_error()
        assert result.error.tag == "validation"

############################################
# Integration Tests for New Functions
############################################

def test_complex_ui_workflow(mock_console: MagicMock) -> None:
    """Test complex UI workflow combining multiple components."""
    # Create nested panel with status table
    columns = [("Test", "cyan"), ("Status", "green")]
    rows = [["Test 1", "Pass"], ["Test 2", "Fail"]]
    
    result = (create_multi_column_table(columns, rows)
             .bind(lambda table: create_nested_panel(
                 "Test Results",
                 [("Summary", str(table))]
             ))
             .bind(lambda panel: Try.apply(lambda: console.print(panel))
                   .map_error(lambda e: DisplayError.Rendering("Failed to display results", e))))
                   
    assert result.is_ok()
    assert mock_console.print.called

def test_interactive_workflow() -> None:
    """Test interactive workflow with user input and progress."""
    with (patch("builtins.input", return_value="test"),
          patch("fcship.utils.ui.console")):
        
        # Get user input
        input_result = prompt_for_input(
            "Enter test count: ",
            lambda x: Ok(x) if x.isdigit() else Error("Must be a number")
        )
        assert input_result.is_ok()
        
        # Process items with progress
        items = range(3)
        process_result = display_progress(
            items,
            lambda x: Ok(f"Processed {x}"),
            "Processing tests"
        )
        assert process_result.is_ok()

############################################
# Error Handling Utility Tests
############################################

def test_with_fallback_success(mock_console: MagicMock) -> None:
    """Test successful operation with fallback."""
    result = with_fallback(
        lambda: Ok("success"),
        fallback="fallback"
    )
    assert result == "success"
    mock_console.print.assert_not_called()

def test_with_fallback_error(mock_console: MagicMock) -> None:
    """Test fallback on operation error."""
    result = with_fallback(
        lambda: Error(DisplayError.Validation("test error")),
        fallback="fallback",
        error_message="Operation failed"
    )
    assert result == "fallback"
    mock_console.print.assert_called_once()

def test_with_fallback_exception(mock_console: MagicMock) -> None:
    """Test fallback on operation exception."""
    result = with_fallback(
        lambda: exec('raise Exception("test")'),  # type: ignore
        fallback="fallback",
        error_message="Operation failed"
    )
    assert result == "fallback"
    mock_console.print.assert_called_once()

@pytest.mark.parametrize("attempts_until_success", [1, 2, 3])
def test_with_retry_eventual_success(
    mock_console: MagicMock,
    attempts_until_success: int
) -> None:
    """Test retry with eventual success."""
    attempt = 0
    def operation() -> Result[str, DisplayError]:
        nonlocal attempt
        attempt += 1
        if attempt >= attempts_until_success:
            return Ok("success")
        return Error(DisplayError.Validation("retry needed"))
    
    with patch("time.sleep"):
        result = with_retry(operation, max_attempts=3, delay=0)
        assert result.is_ok()
        assert result.ok == "success"
        assert attempt == attempts_until_success

def test_with_retry_max_attempts(mock_console: MagicMock) -> None:
    """Test retry exhausting max attempts."""
    attempt = 0
    def operation() -> Result[str, DisplayError]:
        nonlocal attempt
        attempt += 1
        return Error(DisplayError.Validation(f"attempt {attempt}"))
    
    with patch("time.sleep"):
        result = with_retry(operation, max_attempts=3, delay=0)
        assert result.is_error()
        assert isinstance(result.error, DisplayError)
        assert result.error.tag == "validation"
        assert attempt == 3

@pytest.mark.parametrize("error,expected_message", [
    (DisplayError.Validation("test error"), "Validation Error: test error"),
    (DisplayError.Rendering("test error", Exception("details")), "Display Error"),
    (DisplayError.Interaction("test error", Exception("details")), "Input Error"),
])
def test_handle_ui_error(
    mock_console: MagicMock,
    error: DisplayError,
    expected_message: str
) -> None:
    """Test UI error handling for different error types."""
    result = handle_ui_error(error)
    assert result.is_ok()
    mock_console.print.assert_called_once()
    assert expected_message in str(mock_console.print.call_args)

############################################
# Integration Tests with Error Handling
############################################

def test_complex_ui_workflow_with_retries(mock_console: MagicMock) -> None:
    """Test complex UI workflow with retry logic."""
    attempt = 0
    def create_table() -> Result[Table, DisplayError]:
        nonlocal attempt
        attempt += 1
        if attempt == 1:
            return Error(DisplayError.Validation("First attempt fails"))
        return Ok(Table())
    
    with patch("time.sleep"):
        result = with_retry(create_table)
        assert result.is_ok()
        assert attempt == 2

def test_fallback_chain(mock_console: MagicMock) -> None:
    """Test chaining multiple operations with fallbacks."""
    def operation1() -> Result[str, DisplayError]:
        return Error(DisplayError.Validation("op1 failed"))
        
    def operation2() -> Result[str, DisplayError]:
        return Ok("op2 success")
        
    result = with_fallback(
        operation1,
        with_fallback(operation2, "final fallback")
    )
    
    assert result == "op2 success"

@pytest.mark.parametrize("delay,max_attempts", [
    (0.1, 2),
    (0.2, 3),
    (0.3, 1)
])
def test_retry_timing(
    mock_console: MagicMock,
    delay: float,
    max_attempts: int
) -> None:
    """Test retry timing behavior."""
    with patch("time.sleep") as mock_sleep:
        result = with_retry(
            lambda: Error(DisplayError.Validation("test")),
            max_attempts=max_attempts,
            delay=delay
        )
        
        assert result.is_error()
        assert mock_sleep.call_count == max_attempts - 1
        for call in mock_sleep.call_args_list:
            assert call.args[0] == delay

############################################
# Error Recovery Tests
############################################

def test_aggregate_errors() -> None:
    """Test error aggregation."""
    errors = Block.of_seq([
        DisplayError.Validation("Input error"),
        DisplayError.Rendering("Display error", Exception("details")),
        DisplayError.Interaction("User error", Exception("details"))
    ])
    
    result = aggregate_errors(errors)
    assert isinstance(result, DisplayError)
    assert result.tag == "validation"
    assert "Input error" in result.validation
    assert "Display error" in result.validation
    assert "User error" in result.validation

def test_recover_ui_success() -> None:
    """Test successful recovery."""
    def operation() -> Result[str, DisplayError]:
        return Ok("success")
        
    strategies = {
        "validation": lambda: Ok("recovered")
    }
    
    result = recover_ui(operation, strategies)
    assert result.is_ok()
    assert result.ok == "success"

def test_recover_ui_with_recovery() -> None:
    """Test recovery after failure."""
    attempt = 0
    def operation() -> Result[str, DisplayError]:
        nonlocal attempt
        attempt += 1
        if attempt == 1:
            return Error(DisplayError.Validation("first try"))
        return Ok("success")
        
    strategies = {
        "validation": operation
    }
    
    result = recover_ui(operation, strategies)
    assert result.is_ok()
    assert result.ok == "success"
    assert attempt == 2

def test_recover_ui_exhausted() -> None:
    """Test recovery exhaustion."""
    def operation() -> Result[str, DisplayError]:
        return Error(DisplayError.Validation("error"))
        
    strategies = {
        "validation": operation
    }
    
    result = recover_ui(operation, strategies, max_attempts=2)
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

def test_safe_display_success(mock_console: MagicMock) -> None:
    """Test successful safe display."""
    def display(x: str) -> Result[None, DisplayError]:
        return Ok(None)
        
    def fallback(x: str) -> Result[None, DisplayError]:
        return Ok(None)
        
    result = safe_display("test", display, fallback)
    assert result.is_ok()

def test_safe_display_fallback(mock_console: MagicMock) -> None:
    """Test display with fallback."""
    def display(x: str) -> Result[None, DisplayError]:
        return Error(DisplayError.Rendering("display failed", Exception()))
        
    def fallback(x: str) -> Result[None, DisplayError]:
        return Ok(None)
        
    result = safe_display("test", display, fallback)
    assert result.is_ok()

def test_safe_display_both_fail(mock_console: MagicMock) -> None:
    """Test both display and fallback failing."""
    def display(x: str) -> Result[None, DisplayError]:
        return Error(DisplayError.Rendering("display failed", Exception()))
        
    def fallback(x: str) -> Result[None, DisplayError]:
        return Error(DisplayError.Validation("fallback failed"))
        
    result = safe_display("test", display, fallback)
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"
    assert "display failed" in result.error.validation
    assert "fallback failed" in result.error.validation

############################################
# Context Management Tests
############################################

def test_with_ui_context_success() -> None:
    """Test successful context operation."""
    def setup() -> Result[None, DisplayError]:
        return Ok(None)
        
    def operation() -> Result[str, DisplayError]:
        return Ok("success")
        
    def cleanup() -> Result[None, DisplayError]:
        return Ok(None)
        
    result = with_ui_context(operation, setup, cleanup)
    assert result.is_ok()
    assert result.ok == "success"

def test_with_ui_context_setup_failure() -> None:
    """Test context with setup failure."""
    def setup() -> Result[None, DisplayError]:
        return Error(DisplayError.Validation("setup failed"))
        
    def operation() -> Result[str, DisplayError]:
        return Ok("success")
        
    result = with_ui_context(operation, setup)
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"
    assert "setup failed" in result.error.validation

def test_with_ui_context_cleanup_failure() -> None:
    """Test context with cleanup failure."""
    def operation() -> Result[str, DisplayError]:
        return Ok("success")
        
    def cleanup() -> Result[None, DisplayError]:
        return Error(DisplayError.Validation("cleanup failed"))
        
    result = with_ui_context(operation, cleanup=cleanup)
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"
    assert "cleanup failed" in result.error.validation

def test_with_ui_context_operation_exception() -> None:
    """Test context with operation exception."""
    def operation() -> Result[str, DisplayError]:
        raise Exception("operation failed")
        
    def cleanup() -> Result[None, DisplayError]:
        return Ok(None)
        
    result = with_ui_context(operation, cleanup=cleanup)
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "rendering"
    assert "operation failed" in result.error.rendering[0]

############################################
# Integration Tests with Recovery
############################################

def test_ui_workflow_with_recovery(mock_console: MagicMock) -> None:
    """Test UI workflow with error recovery."""
    attempt = 0
    def display_operation() -> Result[None, DisplayError]:
        nonlocal attempt
        attempt += 1
        if attempt == 1:
            return Error(DisplayError.Validation("first try"))
        return Ok(None)
    
    strategies = {
        "validation": display_operation,
        "rendering": lambda: Ok(None)
    }
    
    def cleanup() -> Result[None, DisplayError]:
        return Ok(None)
        
    result = with_ui_context(
        lambda: recover_ui(display_operation, strategies),
        cleanup=cleanup
    )
    
    assert result.is_ok()
    assert attempt == 2