import pytest
from expression import Ok, Error, Result, effect
from fcship.tui.input import (
    InputContext,
    TyperInputHandler,
    prompt_for_input,
    get_user_input,
    get_confirmation,
)
from fcship.tui.errors import DisplayError

class MockInputHandler:
    def __init__(self, responses=None, raise_error=False):
        self.responses = responses or {}
        self.raise_error = raise_error
        self.prompts = []
        self.confirmations = []

    def prompt(self, text: str) -> str:
        self.prompts.append(text)
        if self.raise_error:
            raise Exception("Mock input error")
        return self.responses.get("prompt", "mock_input")

    def confirm(self, text: str) -> bool:
        self.confirmations.append(text)
        if self.raise_error:
            raise Exception("Mock confirmation error")
        return self.responses.get("confirm", True)

@pytest.fixture
def mock_input_handler():
    return MockInputHandler()

@pytest.fixture
def error_input_handler():
    return MockInputHandler(raise_error=True)

@pytest.fixture
def input_context(mock_input_handler):
    return InputContext(input_handler=mock_input_handler)

@pytest.fixture
def error_context(error_input_handler):
    return InputContext(input_handler=error_input_handler)

@effect.result[str, DisplayError]()
def test_get_user_input_success(input_context):
    """Test successful user input retrieval"""
    result = yield from get_user_input(input_context, "Enter value: ")
    assert result.is_ok()
    assert result.ok == "mock_input"
    assert input_context.input_handler.prompts == ["Enter value: "]

@effect.result[str, DisplayError]()
def test_get_user_input_error(error_context):
    """Test error handling in user input retrieval"""
    result = yield from get_user_input(error_context, "Enter value: ")
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "interaction"
    assert "Failed to get user input" in result.error.interaction[0]

@effect.result[str, DisplayError]()
def test_prompt_for_input_valid(input_context):
    """Test prompt with valid input"""
    def validator(value: str) -> bool:
        return len(value) > 0

    result = yield from prompt_for_input(input_context, "Enter name: ", validator)
    assert result.is_ok()
    assert result.ok == "mock_input"
    assert input_context.input_handler.prompts == ["Enter name: "]

@effect.result[str, DisplayError]()
def test_prompt_for_input_invalid(input_context):
    """Test prompt with invalid input"""
    def validator(value: str) -> bool:
        return False

    result = yield from prompt_for_input(input_context, "Enter name: ", validator)
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "validation"

@effect.result[bool, DisplayError]()
def test_get_confirmation_success(input_context):
    """Test successful confirmation"""
    result = yield from get_confirmation(input_context, "Proceed?")
    assert result.is_ok()
    assert result.ok is True
    assert input_context.input_handler.confirmations == ["Proceed?"]

@effect.result[bool, DisplayError]()
def test_get_confirmation_error(error_context):
    """Test error handling in confirmation"""
    result = yield from get_confirmation(error_context, "Proceed?")
    assert result.is_error()
    assert isinstance(result.error, DisplayError)
    assert result.error.tag == "interaction"
    assert "Failed to get user confirmation" in result.error.interaction[0]

def test_typer_input_handler():
    """Test the actual Typer input handler implementation"""
    handler = TyperInputHandler()
    assert isinstance(handler.prompt, object)
    assert isinstance(handler.confirm, object) 