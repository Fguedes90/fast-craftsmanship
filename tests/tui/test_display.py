from unittest.mock import patch

import pytest

from expression import Error, Ok, effect
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from rich.console import Console

from fcship.tui.display import (
    BatchMessages,
    DisplayContext,
    DisplayError,
    DisplayMessage,
    DisplayStyle,
    batch_display_messages,
    display_indented_text,
    display_rule,
    error_message,
    handle_display,
    print_rule,
    print_styled,
    process_messages,
    success_message,
    validate_batch_messages,
    validate_message,
    validate_message_pair,
    warning_message,
)

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
def display_ctx(mock_console):
    return DisplayContext(console=mock_console)


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
    indent_level=st.integers(min_value=0, max_value=10),
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
            st.sampled_from([style.value for style in DisplayStyle]),
        ),
        min_size=1,
        max_size=10,
    )
)
@settings(suppress_health_check=[])
def test_batch_messages_properties(messages):
    """Test that valid BatchMessages combinations work correctly."""
    batch = BatchMessages(messages=messages)

    @effect.result[None, DisplayError]()
    def run_test():
        result = yield from validate_batch_messages(batch)
        assert result.is_ok()
        assert isinstance(result.ok, BatchMessages)
        assert result.ok.messages == messages

    # Execute the effect computation
    run_test()


@given(
    content=st.text(min_size=1).filter(lambda x: bool(x.strip())),
    level=st.integers(min_value=0, max_value=10),
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_indented_text_properties(content, level, display_ctx):
    """Test that indentation works correctly for various content and levels."""
    with patch("fcship.tui.display.display_message", return_value=Ok(None)) as mock_display:
        result = display_indented_text(display_ctx, content, level)
        assert result.is_ok()
        mock_display.assert_called_once()
        args = mock_display.call_args[0][1]  # Second arg is the message
        assert args.indent_level == level
        assert args.content == content


# Test print functions
def test_print_styled_with_valid_message(display_ctx, valid_display_message):
    result = print_styled(display_ctx, valid_display_message)
    assert result.is_ok()
    display_ctx.console.print.assert_called_once()


def test_print_styled_with_exception(display_ctx, valid_display_message):
    display_ctx.console.print.side_effect = Exception("Test error")
    result = print_styled(display_ctx, valid_display_message)
    assert result.is_error()
    assert "Test error" in str(result.error.rendering[1])


def test_print_rule_with_valid_message(display_ctx):
    result = print_rule(display_ctx, VALID_MESSAGE)
    assert result.is_ok()
    display_ctx.console.print.assert_called_once()


def test_print_rule_with_exception(display_ctx):
    display_ctx.console.print.side_effect = Exception("Test error")
    result = print_rule(display_ctx, VALID_MESSAGE)
    assert result.is_error()
    assert "Test error" in str(result.error.rendering[1])


def test_print_styled_without_style(display_ctx):
    """Test print_styled when message has no style."""
    message = DisplayMessage(content=VALID_MESSAGE)
    result = print_styled(display_ctx, message)
    assert result.is_ok()
    display_ctx.console.print.assert_called_once_with(VALID_MESSAGE)


def test_display_rule_with_error(mocker, display_ctx):
    """Test display_rule when print_rule fails."""
    mock_print_rule = mocker.patch(
        "fcship.tui.display.print_rule",
        return_value=Error(DisplayError.Rendering("Rule error", Exception("Test"))),
    )
    result = display_rule(display_ctx, VALID_MESSAGE)
    assert result.is_error()
    assert "Rule error" in str(result.error.rendering[0])


# Test message display functions
def test_success_message(mocker, display_ctx):
    mock_display = mocker.patch("fcship.tui.display.display_message", return_value=Ok(None))
    result = success_message(display_ctx, VALID_MESSAGE)
    assert result.is_ok()
    mock_display.assert_called_once()


def test_error_message_with_details(mocker, display_ctx):
    mock_display = mocker.patch("fcship.tui.display.display_message", return_value=Ok(None))
    result = error_message(display_ctx, VALID_MESSAGE, details="Error details")
    assert result.is_ok()
    assert mock_display.call_count == 2  # Called for both message and details


def test_warning_message(mocker, display_ctx):
    mock_display = mocker.patch("fcship.tui.display.display_message", return_value=Ok(None))
    result = warning_message(display_ctx, VALID_MESSAGE)
    assert result.is_ok()
    mock_display.assert_called_once()


# Test batch processing
def test_process_messages_with_valid_batch(valid_batch_messages, mocker, display_ctx):
    mock_display = mocker.patch("fcship.tui.display.display_message", return_value=Ok(None))
    result = process_messages(display_ctx, valid_batch_messages)
    assert result.is_ok()
    assert mock_display.call_count == len(valid_batch_messages.messages)


def test_process_messages_with_display_error(valid_batch_messages, mocker, display_ctx):
    mock_display = mocker.patch(
        "fcship.tui.display.display_message",
        return_value=Error(DisplayError.Rendering("Display error", Exception("Test"))),
    )
    result = process_messages(display_ctx, valid_batch_messages)
    assert result.is_error()
    assert "Display error" in str(result.error.rendering[0])


def test_batch_display_messages_with_invalid_batch(display_ctx):
    invalid_batch = BatchMessages(messages=[])
    result = batch_display_messages(display_ctx, invalid_batch)
    assert result.ok.is_error()  # The result is Ok(Error(...))
    assert "empty" in result.ok.error.validation.lower()


def test_error_message_with_details_display_error(mocker, display_ctx):
    """Test error_message when details display fails."""
    mock_display = mocker.patch(
        "fcship.tui.display.display_message",
        side_effect=[Ok(None), Error(DisplayError.Rendering("Details error", Exception("Test")))],
    )
    result = error_message(display_ctx, VALID_MESSAGE, details="Some details")
    assert result.is_error()
    assert "Details error" in str(result.error.rendering[0])


def test_validate_message_pair_empty_message():
    """Test validate_message_pair with empty message."""
    result = validate_message_pair(("", "style"))
    assert result.is_error()
    assert "empty" in result.error.validation.lower()


def test_validate_message_pair_empty_style():
    """Test validate_message_pair with empty style."""
    result = validate_message_pair(("message", ""))
    assert result.is_error()
    assert "empty" in result.error.validation.lower()


def test_print_styled_without_style_direct(display_ctx):
    """Test print_styled directly without style."""
    message = DisplayMessage(content="test", style=None)
    result = print_styled(display_ctx, message)
    assert result.is_ok()
    display_ctx.console.print.assert_called_once_with("test")


def test_handle_display_print_error(display_ctx):
    """Test handle_display when print_styled fails."""
    with patch(
        "fcship.tui.display.print_styled",
        return_value=Error(DisplayError.Rendering("Print error", Exception("Test"))),
    ):
        result = handle_display(display_ctx, DisplayMessage(content="test"))
        assert result.ok.is_error()  # The result is Ok(Error(...))
        assert "Print error" in str(result.ok.error.rendering[0])


def test_process_messages_with_validation_error(display_ctx):
    """Test process_messages with a validation error by supplying an invalid batch."""
    # Create a BatchMessages with an empty message to trigger a validation error
    invalid_batch = BatchMessages(messages=[("", "green")])
    result = process_messages(display_ctx, invalid_batch)
    assert result.is_error()
    # Since validate_message_pair returns Error(DisplayError.Validation("Message and style cannot be empty"))
    # we check that the error message contains 'empty'
    assert "empty" in result.error.validation.lower()


def test_error_message_with_details_display(mocker, display_ctx):
    """Test error_message with details display."""
    with patch("fcship.tui.display.display_message") as mock_display:
        mock_display.side_effect = [
            Ok(None),
            Ok(None),
        ]  # First for main message, second for details
        result = error_message(display_ctx, "Error", details="Details")
        assert result.is_ok()
        assert mock_display.call_count == 2
        # Verify details message was created correctly
        details_call = mock_display.call_args_list[1]
        details_msg = details_call[0][1]  # Second arg is the message
        assert details_msg.content == "Details: Details"
        assert details_msg.style == DisplayStyle.ERROR_DETAIL.value
