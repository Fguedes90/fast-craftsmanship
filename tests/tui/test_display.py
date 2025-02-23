from typing import List, Tuple
import pytest
from expression import Ok, Error, Result, effect
from rich.console import Console
from hypothesis import given, strategies as st
from fcship.tui.display import (
    DisplayMessage,
    BatchMessages,
    DisplayStyle,
    DisplayError,
    validate_message,
    validate_message_pair,
    validate_batch_messages,
    print_styled,
    print_rule,
    display_message,
    success_message,
    error_message,
    warning_message,
    display_rule,
    create_display_message,
    process_messages,
    batch_display_messages,
    display_indented_text,
    handle_display
)
from unittest.mock import patch
from unittest.mock import Mock

# Test data
VALID_MESSAGE = "Test message"
EMPTY_MESSAGE = ""
WHITESPACE_MESSAGE = "   "
VALID_STYLE = "green"
EMPTY_STYLE = ""

# Fixtures
@pytest.fixture
def mock_console(mocker):
    console = mocker.Mock(spec=Console)
    console.print = mocker.Mock(return_value=None)
    return console

@pytest.fixture
def valid_display_message():
    return DisplayMessage(content=VALID_MESSAGE, style=VALID_STYLE)

@pytest.fixture
def valid_batch_messages():
    messages = [(VALID_MESSAGE, VALID_STYLE), (VALID_MESSAGE, VALID_STYLE)]
    return BatchMessages(messages=messages)

# Property-based tests using Hypothesis
@given(st.text())
def test_validate_message_property(content):
    """Test that any non-whitespace message is valid."""
    message = DisplayMessage(content=content)
    result = validate_message(message)
    if content.strip():
        assert result.is_ok()
        assert result.ok == message
    else:
        assert result.is_error()
        assert result.error.tag == "validation"
        assert "empty" in result.error.validation.lower()

@given(
    content=st.text(min_size=1).filter(lambda x: bool(x.strip())),
    style=st.sampled_from([style.value for style in DisplayStyle]),
    indent_level=st.integers(min_value=0, max_value=10)
)
def test_display_message_properties(content, style, indent_level):
    """Test that valid DisplayMessage combinations work correctly."""
    message = DisplayMessage(content=content, style=style, indent_level=indent_level)
    result = validate_message(message)
    assert result.is_ok()
    assert result.ok == message

@given(
    messages=st.lists(
        st.tuples(
            st.text(min_size=1).filter(lambda x: bool(x.strip())),
            st.sampled_from([style.value for style in DisplayStyle])
        ),
        min_size=1,
        max_size=10
    )
)
@effect.result[None, DisplayError]()
def test_batch_messages_properties(messages):
    """Test that valid BatchMessages combinations work correctly."""
    batch = BatchMessages(messages=messages)
    result = yield from validate_batch_messages(batch)
    assert result.is_ok()
    assert isinstance(result.ok, BatchMessages)
    assert result.ok.messages == messages

@given(
    content=st.text(min_size=1).filter(lambda x: bool(x.strip())),
    level=st.integers(min_value=0, max_value=10)
)
def test_indented_text_properties(content, level):
    """Test that indentation works correctly for various content and levels."""
    with patch('fcship.tui.display.display_message', return_value=Ok(None)) as mock_display:
        result = display_indented_text(content, level)
        assert result.is_ok()
        mock_display.assert_called_once()
        args = mock_display.call_args[0][0]
        assert args.indent_level == level
        assert args.content == content

# Test print functions
def test_print_styled_with_valid_message(mock_console, valid_display_message):
    result = print_styled(mock_console, valid_display_message)
    assert result.is_ok()
    mock_console.print.assert_called_once()

def test_print_styled_with_exception(mock_console, valid_display_message):
    mock_console.print.side_effect = Exception("Test error")
    result = print_styled(mock_console, valid_display_message)
    assert result.is_error()
    assert "Test error" in result.error

def test_print_rule_with_valid_message(mock_console):
    result = print_rule(mock_console, VALID_MESSAGE)
    assert result.is_ok()
    mock_console.print.assert_called_once()

def test_print_rule_with_exception(mock_console):
    mock_console.print.side_effect = Exception("Test error")
    result = print_rule(mock_console, VALID_MESSAGE)
    assert result.is_error()
    assert "Test error" in result.error

def test_print_styled_without_style(mock_console):
    """Test print_styled when message has no style."""
    message = DisplayMessage(content=VALID_MESSAGE)
    result = print_styled(mock_console, message)
    assert result.is_ok()
    mock_console.print.assert_called_once_with(VALID_MESSAGE)

def test_display_rule_with_error(mocker):
    """Test display_rule when print_rule fails."""
    mock_print_rule = mocker.patch('fcship.tui.display.print_rule', return_value=Error("Rule error"))
    result = display_rule(VALID_MESSAGE)
    assert result.is_error()
    assert "Failed to display rule: Rule error" in result.error

# Test message display functions
def test_success_message(mocker):
    mock_display = mocker.patch('fcship.tui.display.display_message', return_value=Ok(None))
    result = success_message(VALID_MESSAGE)
    assert result.is_ok()
    mock_display.assert_called_once()

def test_error_message_with_details(mocker):
    mock_display = mocker.patch('fcship.tui.display.display_message', return_value=Ok(None))
    result = error_message(VALID_MESSAGE, details="Error details")
    assert result.is_ok()
    assert mock_display.call_count == 2  # Called for both message and details

def test_warning_message(mocker):
    mock_display = mocker.patch('fcship.tui.display.display_message', return_value=Ok(None))
    result = warning_message(VALID_MESSAGE)
    assert result.is_ok()
    mock_display.assert_called_once()

# Test batch processing
def test_process_messages_with_valid_batch(valid_batch_messages, mocker):
    mock_display = mocker.patch('fcship.tui.display.display_message', return_value=Ok(None))
    result = process_messages(Ok(valid_batch_messages))
    assert result.is_ok()
    assert mock_display.call_count == len(valid_batch_messages.messages)

def test_process_messages_with_display_error(valid_batch_messages, mocker):
    mock_display = mocker.patch('fcship.tui.display.display_message', return_value=Error("Display error"))
    result = process_messages(Ok(valid_batch_messages))
    assert result.is_error()
    assert "Display error" in result.error

def test_batch_display_messages_with_invalid_batch():
    invalid_batch = BatchMessages(messages=[])
    result = batch_display_messages(invalid_batch)
    assert result.is_error()
    assert "empty" in result.error.lower()

def test_error_message_with_details_display_error(mocker):
    """Test error_message when details display fails."""
    mock_display = mocker.patch(
        'fcship.tui.display.display_message',
        side_effect=[Ok(None), Error("Details error")]
    )
    result = error_message(VALID_MESSAGE, details="Some details")
    assert result.is_error()
    assert "Details error" in result.error

def test_validate_message_pair_empty_message():
    """Test validate_message_pair with empty message."""
    result = validate_message_pair(("", "style"))
    assert result.is_error()
    assert "empty" in result.error.lower()

def test_validate_message_pair_empty_style():
    """Test validate_message_pair with empty style."""
    result = validate_message_pair(("message", ""))
    assert result.is_error()
    assert "empty" in result.error.lower()

def test_print_styled_without_style_direct():
    """Test print_styled directly without style."""
    mock_console = Mock(spec=Console)
    message = DisplayMessage(content="test", style=None)
    result = print_styled(mock_console, message)
    assert result.is_ok()
    mock_console.print.assert_called_once_with("test")

def test_handle_display_print_error():
    """Test handle_display when print_styled fails."""
    with patch('fcship.tui.display.print_styled', return_value=Error("Print error")):
        result = handle_display(DisplayMessage(content="test"))
        assert result.is_error()
        assert "Failed to display message: Print error" in result.error

def test_process_messages_with_validation_error():
    """Test process_messages with a validation error."""
    error_result = Error("Validation error")
    result = process_messages(error_result)
    assert result.is_error()
    assert result.error == "Validation error"

def test_error_message_with_details_display():
    """Test error_message with details display."""
    with patch('fcship.tui.display.display_message') as mock_display:
        mock_display.side_effect = [Ok(None), Ok(None)]  # First for main message, second for details
        result = error_message("Error", details="Details")
        assert result.is_ok()
        assert mock_display.call_count == 2
        # Verify details message was created correctly
        details_call = mock_display.call_args_list[1]
        details_msg = details_call[0][0]
        assert details_msg.content == "Details: Details"
        assert details_msg.style == DisplayStyle.ERROR_DETAIL.value 