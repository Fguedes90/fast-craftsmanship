"""Common test configurations and fixtures."""
from collections.abc import Generator, Callable
from typing import Any
from unittest.mock import MagicMock, patch
import pytest
from hypothesis import strategies as st
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from expression import Result, Ok, Error, pipe, Try
from expression.collections import Block, seq

from fcship.commands.verify import CommandOutput, VerificationOutcome
from fcship.utils.ui import DisplayError, VALID_STYLES

@pytest.fixture
def mock_console() -> Generator[MagicMock, None, None]:
    """Mock for rich console."""
    console_mock = MagicMock(spec=Console)
    with patch('fcship.utils.ui.console', console_mock):
        yield console_mock

@pytest.fixture
def mock_table() -> Table:
    """Create a fresh table for testing."""
    table = Table()
    table.add_column("Test")
    table.add_column("Status")
    return table

@pytest.fixture
def success_verification() -> Result[str, VerificationOutcome]:
    """Provides a successful verification result."""
    return Ok("Success output")

@pytest.fixture
def failed_verification() -> Result[str, VerificationOutcome]:
    """Provides a failed verification result."""
    return Error(VerificationOutcome.Failure("test", "Failure output"))

@pytest.fixture
def mixed_verifications() -> Block[tuple[str, Result[str, VerificationOutcome]]]:
    """Provides a mix of successful and failed verifications."""
    return Block.of_seq([
        ("test1", Ok("Success")),
        ("test2", Error(VerificationOutcome.Failure("test2", "Failed"))),
        ("test3", Ok("Success")),
        ("test4", Error(VerificationOutcome.ExecutionError("cmd", "Error")))
    ])

@pytest.fixture
def successful_verifications() -> Block[tuple[str, Result[str, VerificationOutcome]]]:
    """Provides all successful verifications."""
    return Block.of_seq([
        ("test1", Ok("Success 1")),
        ("test2", Ok("Success 2")),
        ("test3", Ok("Success 3"))
    ])

@pytest.fixture
def failed_verifications() -> Block[tuple[str, Result[str, VerificationOutcome]]]:
    """Provides all failed verifications."""
    return Block.of_seq([
        ("test1", Error(VerificationOutcome.Failure("test1", "Failed 1"))),
        ("test2", Error(VerificationOutcome.Failure("test2", "Failed 2")))
    ])

@pytest.fixture
def mock_verification_results() -> Block[tuple[str, Result[str, VerificationOutcome]]]:
    """Fixture for verification results."""
    return Block.of_seq([
        ("test1", Ok("Success 1")),
        ("test2", Error(VerificationOutcome.Failure("test2", "Failed 2"))),
        ("test3", Ok("Success 3"))
    ])

@pytest.fixture
def mock_subprocess_run() -> Generator[MagicMock, None, None]:
    """Mock for subprocess.run."""
    with patch('subprocess.run') as mock:
        mock.return_value = MagicMock(
            stdout="",
            stderr="",
            returncode=0
        )
        yield mock

@pytest.fixture
def mock_command_output() -> CommandOutput:
    """Fixture for command output."""
    return CommandOutput(
        stdout="test output",
        stderr="",
        returncode=0
    )

@pytest.fixture
def mock_failed_command_output() -> CommandOutput:
    """Fixture for failed command output."""
    return CommandOutput(
        stdout="",
        stderr="test error",
        returncode=1
    )

############################################
# UI Testing Utilities
############################################

@pytest.fixture
def assert_display_error():
    """Helper fixture to assert display error properties."""
    def _assert(error: DisplayError, expected_tag: str, expected_message: str):
        assert error.tag == expected_tag
        match error:
            case DisplayError(tag="validation", validation=msg):
                assert msg == expected_message
            case DisplayError(tag="rendering", rendering=(msg, _)):
                assert msg == expected_message
            case DisplayError(tag="interaction", interaction=(msg, _)):
                assert msg == expected_message
    return _assert

@pytest.fixture
def ui_test_strategies():
    """Common UI test strategies."""
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

    def valid_style_strategy() -> st.SearchStrategy[str]:
        """Generate valid style strings."""
        return st.sampled_from(VALID_STYLES)

    def invalid_style_strategy() -> st.SearchStrategy[str]:
        """Generate invalid style strings."""
        return st.text(min_size=1).filter(lambda x: x not in VALID_STYLES)

    return {
        'display_error': display_error_strategy,
        'table_row': table_row_strategy,
        'valid_style': valid_style_strategy,
        'invalid_style': invalid_style_strategy
    }

@pytest.fixture
def assert_validation_error():
    """Helper fixture to assert validation error properties."""
    def _assert(result: Result[Any, DisplayError], expected_message: str):
        assert result.is_error()
        assert isinstance(result.error, DisplayError)
        assert result.error.tag == "validation"
        assert result.error.validation == expected_message
    return _assert

@pytest.fixture
def assert_rendering_error():
    """Helper fixture to assert rendering error properties."""
    def _assert(result: Result[Any, DisplayError], expected_message: str):
        assert result.is_error()
        assert isinstance(result.error, DisplayError)
        assert result.error.tag == "rendering"
        assert result.error.rendering[0] == expected_message
    return _assert

@pytest.fixture
def ui_test_helpers():
    """Common UI test helper functions."""
    def verify_table_structure(table: Table, expected_columns: list[tuple[str, str | None]]):
        """Verify table column structure."""
        assert len(table.columns) == len(expected_columns)
        for (col, (name, style)) in zip(table.columns, expected_columns):
            assert col.header == name
            if style:
                assert col.style == style

    def verify_panel_structure(panel: Panel, expected_title: str, expected_style: str):
        """Verify panel structure."""
        assert isinstance(panel, Panel)
        assert panel.title == expected_title
        assert panel.border_style == expected_style

    return {
        'verify_table_structure': verify_table_structure,
        'verify_panel_structure': verify_panel_structure
    }

@pytest.fixture
def mock_user_input(monkeypatch):
    """Mock user input for testing."""
    inputs = []
    
    def mock_input(prompt: str = ""):
        if not inputs:
            raise ValueError("No more inputs provided")
        return inputs.pop(0)
    
    monkeypatch.setattr('builtins.input', mock_input)
    
    def provide_inputs(*values):
        inputs.extend(values)
        
    return provide_inputs

@pytest.fixture
def mock_ui_operation():
    """Create a mock UI operation for testing error handling."""
    class MockUIOperation:
        def __init__(self):
            self.call_count = 0
            self.should_succeed_after = 1
            
        def __call__(self) -> Result[str, DisplayError]:
            self.call_count += 1
            if self.call_count >= self.should_succeed_after:
                return Ok("success")
            return Error(DisplayError.Validation("Operation failed"))
            
        def set_success_after(self, attempts: int):
            self.should_succeed_after = attempts
            
    return MockUIOperation()

"""Test utilities for functional testing."""


def assert_all_ok[T, E](results: Block[Result[T, E]]) -> bool:
    """Asserts that all results in a block are Ok."""
    return all(r.is_ok() for r in results)

def assert_any_error[T, E](results: Block[Result[T, E]]) -> bool:
    """Asserts that at least one result is Error."""
    return any(r.is_error() for r in results)

def collect_errors[T, E](results: Block[Result[T, E]]) -> Block[E]:
    """Collects all errors from results."""
    return pipe(
        results,
        seq.filter(lambda r: r.is_error()),
        seq.map(lambda r: r.error),
        Block.of_seq
    )

def pure_effect[T](value: T) -> Result[T, Any]:
    """Creates a pure effect that always succeeds."""
    return Ok(value)

class EffectTester[T, E]:
    """Helper class for testing effects."""
    
    def __init__(self, computation: Callable[[], Result[T, E]]) -> None:
        self.computation = computation
        
    def map[U](self, f: Callable[[T], U]) -> "EffectTester[U, E]":
        """Maps over the effect."""
        return EffectTester(lambda: self.computation().map(f))
        
    def bind[U](self, f: Callable[[T], Result[U, E]]) -> "EffectTester[U, E]":
        """Binds the effect."""
        return EffectTester(lambda: self.computation().bind(f))
        
    def assert_ok(self) -> T:
        """Asserts effect executes successfully and returns value."""
        result = self.computation()
        assert result.is_ok()
        return result.ok
        
    def assert_error(self) -> E:
        """Asserts effect executes with error and returns error."""
        result = self.computation()
        assert result.is_error()
        return result.error

def run_with_timeout[T, E](computation: Callable[[], Result[T, E]], timeout: float = 1.0) -> Result[T, E]:
    """Runs an effect with timeout."""
    import asyncio
    from concurrent.futures import TimeoutError
    
    try:
        return asyncio.run(
            asyncio.wait_for(
                asyncio.create_task(
                    asyncio.to_thread(computation)
                ),
                timeout=timeout
            )
        )
    except TimeoutError:
        return Try.create_error("Operation timed out")  # type: ignore
        
class ResultMatcher[T, E]:
    """Helper class for matching Result values."""
    
    def __init__(self, result: Result[T, E]) -> None:
        self.result = result
        
    def with_value(self, expected: T) -> bool:
        """Matches successful result with expected value."""
        return self.result.is_ok() and self.result.ok == expected
        
    def with_error(self, expected: E) -> bool:
        """Matches error result with expected error."""
        return self.result.is_error() and self.result.error == expected
        
    def satisfies(self, predicate: Callable[[Result[T, E]], bool]) -> bool:
        """Checks if result satisfies a predicate."""
        return predicate(self.result)