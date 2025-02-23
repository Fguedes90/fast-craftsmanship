"""Common test configurations and fixtures."""
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch
import pytest
from rich.console import Console
from rich.table import Table
from expression import Result, Ok, Error, pipe
from expression.collections import Block, seq

from fcship.commands.verify import CommandOutput, VerificationOutcome

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