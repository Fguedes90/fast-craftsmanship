"""Tests for verification commands."""
from unittest.mock import MagicMock, patch
import pytest
from hypothesis import given, strategies as st
from expression import Ok, Error, Result, pipe, effect
from expression.collections import Block, seq

from fcship.commands.verify import (
    CommandOutput,
    VerificationOutcome,
    run_command,
    run_verification,
    process_verification_results,
    verify,
    validate_check_type,
    format_verification_output
)

@pytest.fixture
def mock_subprocess_run(monkeypatch) -> MagicMock:
    """Mock subprocess.run for testing."""
    mock = MagicMock()
    monkeypatch.setattr("subprocess.run", mock)
    return mock

# Test strategies
def verification_name_strategy() -> st.SearchStrategy[str]:
    """Generate valid verification names."""
    return st.text(min_size=1, max_size=50)

def verification_outcome_strategy() -> st.SearchStrategy[VerificationOutcome]:
    """Generate verification outcomes."""
    return st.one_of(
        st.builds(lambda x: VerificationOutcome.Success(x), st.text()),
        st.builds(lambda t, o: VerificationOutcome.Failure(t, o), st.text(), st.text()),
        st.builds(lambda x: VerificationOutcome.ValidationError(x), st.text()),
        st.builds(lambda c, o: VerificationOutcome.ExecutionError(c, o), st.text(), st.text())
    )

@pytest.mark.asyncio
async def test_verify_success(mock_subprocess_run: MagicMock) -> None:
    """Test successful verification."""
    mock_subprocess_run.return_value.returncode = 0
    await verify("test")
    mock_subprocess_run.assert_called()

@pytest.mark.asyncio
async def test_verify_failure(mock_subprocess_run: MagicMock) -> None:
    """Test failed verification."""
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.stderr = "error"
    await verify("test")
    mock_subprocess_run.assert_called()

def test_run_command_success(mock_subprocess_run: MagicMock) -> None:
    """Test successful command execution."""
    mock_subprocess_run.return_value.returncode = 0
    result = run_command(Block.of_seq(["test"]))
    assert result.is_ok()
    assert isinstance(result.ok, CommandOutput)
    assert result.ok.returncode == 0

def test_run_command_failure(mock_subprocess_run: MagicMock) -> None:
    """Test failed command execution."""
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.stderr = "error"
    result = run_command(Block.of_seq(["test"]))
    assert result.is_error()
    assert isinstance(result.error, VerificationOutcome)

def test_run_verification_success(mock_subprocess_run: MagicMock) -> None:
    """Test successful verification."""
    mock_subprocess_run.return_value.returncode = 0
    result = run_verification("test", Block.of_seq(["cmd"]))
    assert result.is_ok()
    assert "Passed" in result.ok

def test_run_verification_failure(mock_subprocess_run: MagicMock) -> None:
    """Test failed verification."""
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.stderr = "error"
    result = run_verification("test", Block.of_seq(["cmd"]))
    assert result.is_error()
    assert isinstance(result.error, VerificationOutcome)

@given(verification_outcome_strategy())
def test_verification_outcome_properties(outcome: VerificationOutcome) -> None:
    """Test verification outcome properties."""
    assert str(outcome)  # Should not raise
    match outcome:
        case VerificationOutcome(tag="success"):
            assert outcome.success is not None
        case VerificationOutcome(tag="failure"):
            assert outcome.failure is not None
        case VerificationOutcome(tag="validation_error"):
            assert outcome.validation_error is not None
        case VerificationOutcome(tag="execution_error"):
            assert outcome.execution_error is not None

@given(st.text())
def test_validate_check_type_properties(check_type: str) -> None:
    """Test check type validation properties."""
    result = validate_check_type(check_type)
    if check_type.strip():
        assert result.is_ok()
    else:
        assert result.is_error()
        assert isinstance(result.error, VerificationOutcome)