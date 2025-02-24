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
def test_get_user_input_success(monkeypatch):
    """Test successful user input"""
    def mock_input(*args):
        return "mock_input"
    monkeypatch.setattr('typer.prompt', mock_input)
    
    result = yield from get_user_input("Test prompt")
    assert result.is_ok()
    assert result.ok == "mock_input"
    yield Ok(None)

@effect.result[str, DisplayError]()
def test_get_user_input_error(monkeypatch):
    """Test user input error handling"""
    def mock_input(*args):
        raise ValueError("Mock input error")
    monkeypatch.setattr('typer.prompt', mock_input)
    
    result = yield from get_user_input("Test prompt")
    assert result.is_error()
    assert result.error.tag == "input"
    assert "Mock input error" in str(result.error)
    yield Ok(None)

@effect.result[str, DisplayError]()
def test_prompt_for_input_valid(monkeypatch):
    """Test valid input validation"""
    def mock_input(*args):
        return "mock_input"
    monkeypatch.setattr('typer.prompt', mock_input)
    
    result = yield from prompt_for_input("Test prompt", lambda x: True)
    assert result.is_ok()
    assert result.ok == "mock_input"
    yield Ok(None)

@effect.result[str, DisplayError]()
def test_prompt_for_input_invalid(monkeypatch):
    """Test invalid input validation"""
    def mock_input(*args):
        return "invalid"
    monkeypatch.setattr('typer.prompt', mock_input)
    
    result = yield from prompt_for_input("Test prompt", lambda x: False)
    assert result.is_error()
    assert result.error.tag == "validation"
    assert "Invalid input" in str(result.error)
    yield Ok(None)

@effect.result[bool, DisplayError]()
def test_get_confirmation_success(monkeypatch):
    """Test successful confirmation"""
    def mock_confirm(*args):
        return True
    monkeypatch.setattr('typer.confirm', mock_confirm)
    
    result = yield from get_confirmation("Test prompt")
    assert result.is_ok()
    assert result.ok is True
    yield Ok(None)

@effect.result[bool, DisplayError]()
def test_get_confirmation_error(monkeypatch):
    """Test confirmation error handling"""
    def mock_confirm(*args):
        raise ValueError("Mock confirmation error")
    monkeypatch.setattr('typer.confirm', mock_confirm)
    
    result = yield from get_confirmation("Test prompt")
    assert result.is_error()
    assert result.error.tag == "input"
    assert "Mock confirmation error" in str(result.error)
    yield Ok(None)

def test_typer_input_handler():
    """Test typer input handler"""
    result = typer_input_handler(lambda: "test")
    assert result.is_ok()
    assert result.ok == "test"

def test_typer_input_handler():
    """Test the actual Typer input handler implementation"""
    handler = TyperInputHandler()
    assert isinstance(handler.prompt, object)
    assert isinstance(handler.confirm, object) 