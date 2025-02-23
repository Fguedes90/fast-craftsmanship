"""Unit tests for verify command using functional approach."""
from typing import Any
import subprocess
from unittest.mock import MagicMock, patch
from expression import Result, Ok, Error
from expression.collections import Block, Map
from hypothesis import given, strategies as st
from hypothesis.strategies import SearchStrategy

from fcship.commands.verify import (
    VerificationOutcome,
    CommandOutput,
    run_command,
    validate_check_type,
    format_verification_output,
    run_verification,
    process_verification_results,
    VERIFICATIONS,
)
from fcship.utils.ui import (
    create_table_row,
    create_summary_table,
    create_panel
)
import pytest

############################################
# Test Strategy Definitions
############################################

def verification_name_strategy() -> SearchStrategy[str]:
    """Generate valid verification names."""
    return st.text(min_size=1, max_size=50).filter(lambda x: x.isalnum())

def verification_outcome_strategy() -> SearchStrategy[VerificationOutcome]:
    """Generate valid verification outcomes."""
    return st.one_of(
        st.builds(
            VerificationOutcome.Success,
            st.text(min_size=1)
        ),
        st.builds(
            VerificationOutcome.Failure,
            st.text(min_size=1),
            st.text(min_size=1)
        ),
        st.builds(
            VerificationOutcome.ValidationError,
            st.text(min_size=1)
        ),
        st.builds(
            VerificationOutcome.ExecutionError,
            st.text(min_size=1),
            st.text(min_size=1)
        )
    )

############################################
# Test Data & Fixtures
############################################

# Test data
MOCK_COMMAND = Block.of_seq(["test", "command"])
MOCK_OUTPUT = "test output"
MOCK_ERROR = "test error"

############################################
# Pure Function Tests
############################################

def test_validate_check_type_valid() -> None:
    """Test validation of valid check type."""
    result = validate_check_type("test")
    assert result.is_ok()
    assert result.ok == "test"

def test_validate_check_type_invalid() -> None:
    """Test validation of invalid check type."""
    result = validate_check_type("invalid")
    assert result.is_error()
    assert isinstance(result.error, VerificationOutcome)
    assert result.error.tag == "validation_error"

def test_create_table_row_success() -> None:
    """Test table row creation for successful result."""
    name = "test"
    result: Result[str, VerificationOutcome] = Ok("Success")
    row = create_table_row((name, result))
    assert row == ("Test", "[green]✨ Passed[/green]")

def test_create_table_row_failure() -> None:
    """Test table row creation for failed result."""
    name = "test"
    result: Result[str, VerificationOutcome] = Error(
        VerificationOutcome.Failure(name, "Failed")
    )
    row = create_table_row((name, result))
    assert row == ("Test", "[red]❌ Failed[/red]")

def test_format_verification_output_success() -> None:
    """Test verification output formatting for success."""
    outcome = VerificationOutcome.Success("Test passed")
    panel = format_verification_output(outcome)
    assert panel.title == "[green]Success[/green]"
    assert panel.border_style == "green"
    assert "Test passed" in panel.renderable

def test_format_verification_output_failure() -> None:
    """Test verification output formatting for failure."""
    outcome = VerificationOutcome.Failure("test", "Test failed")
    panel = format_verification_output(outcome)
    assert panel.title == "[red]test Failed[/red]"
    assert panel.border_style == "red"
    assert "Test failed" in panel.renderable

def test_create_summary_table(mock_verification_results: Block[tuple[str, Result[str, VerificationOutcome]]]) -> None:
    """Test summary table creation."""
    table = create_summary_table(mock_verification_results)
    assert len(table.columns) == 2
    assert table.columns[0].style == "cyan"

############################################
# Command Tests
############################################

def test_run_command_success(mock_subprocess_run: MagicMock) -> None:
    """Test successful command execution."""
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = MOCK_OUTPUT
    mock_subprocess_run.return_value.stderr = ""

    with patch("subprocess.run", mock_subprocess_run):
        result = run_command(MOCK_COMMAND)
        assert result.is_ok()
        assert isinstance(result.ok, CommandOutput)
        assert result.ok.stdout == MOCK_OUTPUT

def test_run_command_failure(mock_subprocess_run: MagicMock) -> None:
    """Test failed command execution."""
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.stdout = ""
    mock_subprocess_run.return_value.stderr = MOCK_ERROR

    with patch("subprocess.run", mock_subprocess_run):
        result = run_command(MOCK_COMMAND)
        assert result.is_error()
        assert isinstance(result.error, VerificationOutcome)
        assert result.error.tag == "execution_error"

def test_run_verification_success(mock_subprocess_run: MagicMock) -> None:
    """Test successful verification run."""
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = MOCK_OUTPUT
    mock_subprocess_run.return_value.stderr = ""

    with patch("subprocess.run", mock_subprocess_run):
        result = run_verification("test", MOCK_COMMAND)
        assert result.is_ok()
        assert result.ok == MOCK_OUTPUT

def test_run_verification_failure(mock_subprocess_run: MagicMock) -> None:
    """Test failed verification run."""
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.stdout = ""
    mock_subprocess_run.return_value.stderr = MOCK_ERROR

    with patch("subprocess.run", mock_subprocess_run):
        result = run_verification("test", MOCK_COMMAND)
        assert result.is_error()
        assert isinstance(result.error, VerificationOutcome)
        assert result.error.tag == "failure"

def test_process_verification_results_all_success(
    mock_console: MagicMock,
    mock_verification_results: Block[tuple[str, Result[str, VerificationOutcome]]]
) -> None:
    """Test processing of all successful verification results."""
    success_results = Block.of_seq([
        ("test1", Ok("Success 1")),
        ("test2", Ok("Success 2"))
    ])

    result = process_verification_results(success_results, mock_console)
    assert result.is_ok()
    assert mock_console.print.call_count >= 1

def test_process_verification_results_with_failures(
    mock_console: MagicMock,
    mock_verification_results: Block[tuple[str, Result[str, VerificationOutcome]]]
) -> None:
    """Test processing of verification results with failures."""
    result = process_verification_results(mock_verification_results, mock_console)
    assert result.is_error()
    assert isinstance(result.error, VerificationOutcome)
    assert result.error.tag == "failure"
    assert mock_console.print.call_count >= 1

############################################
# Integration Tests
############################################

def test_verifications_configuration() -> None:
    """Test verification commands configuration."""
    assert isinstance(VERIFICATIONS, Map)
    assert "type" in VERIFICATIONS
    assert "lint" in VERIFICATIONS
    assert "test" in VERIFICATIONS
    assert "format" in VERIFICATIONS

    for cmd in VERIFICATIONS.values():
        assert isinstance(cmd, Block)
        assert len(cmd) > 0

def test_verification_workflow_integration(
    mock_subprocess_run: MagicMock,
    mock_console: MagicMock
) -> None:
    """Test complete verification workflow integration."""
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = MOCK_OUTPUT
    mock_subprocess_run.return_value.stderr = ""

    with (
        patch("subprocess.run", mock_subprocess_run),
        patch("fcship.utils.ui.console", mock_console)
    ):
        # Test full workflow with a single verification
        check_type = "test"
        result = (
            validate_check_type(check_type)
            .bind(lambda t: Ok(Block.of_seq([
                (t, run_verification(t, VERIFICATIONS[t]))
            ])))
            .bind(lambda res: process_verification_results(res, mock_console))
        )

        assert result.is_ok()
        mock_subprocess_run.assert_called()
        mock_console.print.assert_called()

############################################
# Property-Based Tests
############################################

@given(st.text())
def test_validate_check_type_properties(check_type: str) -> None:
    """Test properties of validate_check_type."""
    result = validate_check_type(check_type)
    assert isinstance(result, Result)
    if check_type in list(VERIFICATIONS.keys()) + ["all"]:
        assert result.is_ok()
        assert result.ok == check_type
    else:
        assert result.is_error()
        assert isinstance(result.error, VerificationOutcome)
        assert result.error.tag == "validation_error"

@given(verification_name_strategy())
def test_run_verification_properties(name: str) -> None:
    """Test properties of run_verification."""
    # Use a fixed safe command for testing
    cmd = Block.of_seq(["echo", "test"])
    with patch("subprocess.run", MagicMock(
        return_value=MagicMock(
            returncode=0,
            stdout="test output",
            stderr=""
        )
    )):
        result = run_verification(name, cmd)
        
        # Test that result maintains Result type invariants
        assert isinstance(result, Result)
        assert result.is_ok() or result.is_error()
        
        # Test success case properties
        if result.is_ok():
            assert isinstance(result.ok, str)
        else:
            assert isinstance(result.error, VerificationOutcome)
            assert result.error.tag in {"failure", "execution_error"}

@given(verification_outcome_strategy())
def test_format_output_properties(outcome: VerificationOutcome) -> None:
    """Test properties of format_verification_output."""
    panel = format_verification_output(outcome)
    assert panel.title.startswith("[")
    assert panel.title.endswith("]")
    assert panel.border_style in {"green", "red"}
    assert isinstance(panel.renderable, str)

@given(st.lists(
    st.tuples(
        verification_name_strategy(),
        st.one_of(
            st.builds(lambda x: Ok(x), st.text()),
            st.builds(lambda e: Error(e), verification_outcome_strategy())
        )
    ),
    min_size=0,
    max_size=20
))
def test_process_results_properties(
    results: list[tuple[str, Result[str, VerificationOutcome]]]
) -> None:
    """Test properties of process_verification_results."""
    mock_console = MagicMock()
    result = process_verification_results(Block.of_seq(results), mock_console)
    assert isinstance(result, Result)
    if any(r[1].is_error() for r in results):
        assert result.is_error()
        assert isinstance(result.error, VerificationOutcome)
        assert result.error.tag == "failure"
    else:
        assert result.is_ok()
    assert mock_console.print.call_count >= 1

############################################
# Error Handling Tests
############################################

@pytest.mark.parametrize("error_case", [
    VerificationOutcome.ValidationError("Invalid input"),
    VerificationOutcome.ExecutionError("cmd", "Process failed"),
    VerificationOutcome.Failure("tool", "Tool failed")
])
def test_error_outcomes(error_case: VerificationOutcome) -> None:
    """Test different error outcomes are handled correctly."""
    result = Error(error_case)
    assert result.is_error()
    assert result.error == error_case

def test_empty_verification_results(mock_console: MagicMock) -> None:
    """Test handling of empty verification results."""
    empty_results = Block.of_seq([])

    result = process_verification_results(empty_results, mock_console)
    assert result.is_ok()
    assert mock_console.print.call_count >= 1

def test_verification_with_empty_command() -> None:
    """Test verification with empty command."""
    empty_cmd = Block.of_seq([])
    result = run_verification("empty", empty_cmd)
    assert result.is_error()
    assert isinstance(result.error, VerificationOutcome)
    assert result.error.tag == "execution_error"

@pytest.mark.parametrize("failure_mode", [
    subprocess.CalledProcessError(1, "cmd", b"error"),
    subprocess.TimeoutExpired("cmd", 30),
    PermissionError("Permission denied"),
    FileNotFoundError("Command not found")
])
def test_command_failure_modes(
    mock_subprocess_run: MagicMock,
    failure_mode: Exception
) -> None:
    """Test various command failure modes."""
    mock_subprocess_run.side_effect = failure_mode

    with patch("subprocess.run", mock_subprocess_run):
        result = run_command(MOCK_COMMAND)
        assert result.is_error()
        assert isinstance(result.error, VerificationOutcome)
        assert result.error.tag == "execution_error"

def test_very_long_output(mock_subprocess_run: MagicMock) -> None:
    """Test handling of very long command output."""
    long_output = "x" * 10000
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = long_output
    mock_subprocess_run.return_value.stderr = ""

    with patch("subprocess.run", mock_subprocess_run):
        result = run_command(MOCK_COMMAND)
        assert result.is_ok()
        assert len(result.ok.stdout) == 10000

def test_unicode_output(mock_subprocess_run: MagicMock) -> None:
    """Test handling of unicode characters in output."""
    unicode_output = "测试输出 🚀 テスト"
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = unicode_output
    mock_subprocess_run.return_value.stderr = ""

    with patch("subprocess.run", mock_subprocess_run):
        result = run_command(MOCK_COMMAND)
        assert result.is_ok()
        assert result.ok.stdout == unicode_output

def test_concurrent_verifications(
    mock_subprocess_run: MagicMock,
    mixed_verifications: Block[tuple[str, Result[str, VerificationOutcome]]]
) -> None:
    """Test handling multiple verifications."""
    def mock_run(*args: Any, **kwargs: Any) -> Any:
        return MagicMock(
            returncode=0,
            stdout="Success",
            stderr=""
        )

    mock_subprocess_run.side_effect = mock_run

    with patch("subprocess.run", mock_subprocess_run):
        results = Block.of_seq([
            (name, run_verification(name, Block.of_seq(["test"])))
            for name, _ in mixed_verifications
        ])
        assert all(isinstance(r[1], Result) for r in results)

############################################
# Invariant Tests
############################################

def test_verification_outcome_invariants() -> None:
    """Test that VerificationOutcome maintains its invariants."""
    # Success case
    success = VerificationOutcome.Success("test")
    assert success.tag == "success"
    assert success.success == "test"

    # Failure case
    failure = VerificationOutcome.Failure("test", "error")
    assert failure.tag == "failure"
    assert isinstance(failure.failure, tuple)
    assert len(failure.failure) == 2

    # Validation error case
    validation = VerificationOutcome.ValidationError("error")
    assert validation.tag == "validation_error"
    assert isinstance(validation.validation_error, str)

    # Execution error case
    execution = VerificationOutcome.ExecutionError("cmd", "error")
    assert execution.tag == "execution_error"
    assert isinstance(execution.execution_error, tuple)
    assert len(execution.execution_error) == 2

def test_command_output_invariants() -> None:
    """Test that CommandOutput maintains its invariants."""
    output = CommandOutput(stdout="out", stderr="err")
    assert output.stdout == "out"
    assert output.stderr == "err"

    # Test immutability
    with pytest.raises(Exception):
        output.stdout = "new"  # type: ignore

"""Tests for verification commands."""
from unittest.mock import MagicMock, patch
import pytest
from hypothesis import given, strategies as st
from expression import Ok, Error, Result, pipe, Effect
from expression.collections import Block, seq

from fcship.commands.verify import (
    CommandOutput,
    VerificationOutcome,
    verify_all,
    verify_check,
    run_command,
    run_command_effect,
    run_verification,
    run_verifications,
    VerificationEffect
)

# Test strategies
def command_output_strategy() -> st.SearchStrategy[CommandOutput]:
    """Generate valid command output data."""
    return st.builds(
        CommandOutput,
        stdout=st.text(),
        stderr=st.text(),
        returncode=st.integers(min_value=-1, max_value=1)
    )

def verification_outcome_strategy() -> st.SearchStrategy[VerificationOutcome]:
    """Generate valid verification outcomes."""
    return st.builds(
        VerificationOutcome,
        name=st.text(min_size=1),
        message=st.text(min_size=1)
    )

############################################
# Command Output Tests
############################################

def test_command_output_creation() -> None:
    """Test creation of CommandOutput."""
    output = CommandOutput("stdout", "stderr", 0)
    assert output.stdout == "stdout"
    assert output.stderr == "stderr"
    assert output.returncode == 0

@given(command_output_strategy())
def test_command_output_properties(output: CommandOutput) -> None:
    """Test CommandOutput properties."""
    assert isinstance(output.stdout, str)
    assert isinstance(output.stderr, str)
    assert isinstance(output.returncode, int)

############################################
# Verification Outcome Tests
############################################

def test_verification_outcome_creation() -> None:
    """Test creation of VerificationOutcome."""
    outcome = VerificationOutcome("test", "message")
    assert outcome.name == "test"
    assert outcome.message == "message"

def test_verification_outcome_failure() -> None:
    """Test creation of failure outcome."""
    outcome = VerificationOutcome.Failure("test", "failed")
    assert outcome.name == "test"
    assert outcome.message == "failed"

def test_verification_outcome_execution_error() -> None:
    """Test creation of execution error outcome."""
    outcome = VerificationOutcome.ExecutionError("cmd", "error")
    assert "Execution Error" in outcome.name
    assert "cmd" in outcome.message
    assert "error" in outcome.message

############################################
# Command Execution Tests
############################################

def test_run_command_success(mock_subprocess_run: MagicMock) -> None:
    """Test successful command execution."""
    mock_subprocess_run.return_value.stdout = "success"
    mock_subprocess_run.return_value.stderr = ""
    mock_subprocess_run.return_value.returncode = 0
    
    result = run_command("test")
    assert result.returncode == 0
    assert result.stdout == "success"
    assert result.stderr == ""

def test_run_command_failure(mock_subprocess_run: MagicMock) -> None:
    """Test failed command execution."""
    mock_subprocess_run.return_value.stdout = ""
    mock_subprocess_run.return_value.stderr = "error"
    mock_subprocess_run.return_value.returncode = 1
    
    result = run_command("test")
    assert result.returncode == 1
    assert result.stderr == "error"

def test_run_command_error(mock_subprocess_run: MagicMock) -> None:
    """Test command execution with error."""
    mock_subprocess_run.side_effect = Exception("error")
    result = run_command("test")
    assert result.returncode == -1
    assert "error" in result.stderr

############################################
# Verification Tests
############################################

def test_verify_check_success(mock_subprocess_run: MagicMock) -> None:
    """Test successful verification check."""
    mock_subprocess_run.return_value.returncode = 0
    result = verify_check(["test"])
    assert result.is_ok()
    assert "Passed" in result.ok

def test_verify_check_failure(mock_subprocess_run: MagicMock) -> None:
    """Test failed verification check."""
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.stderr = "error"
    result = verify_check(["test"])
    assert result.is_error()
    assert isinstance(result.error, VerificationOutcome)
    assert "error" in result.error.message

def test_verify_all(mock_subprocess_run: MagicMock) -> None:
    """Test running all verifications."""
    mock_subprocess_run.return_value.returncode = 0
    result = verify_all()
    assert result.is_ok()
    assert isinstance(result.ok, list)
    assert all(isinstance(r, tuple) for r in result.ok)

############################################
# Effect Tests
############################################

def test_run_command_effect() -> None:
    """Test command execution as effect."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        effect = run_command_effect(Block.of_seq(["test"]))
        result = effect.run()
        assert result.is_ok()
        assert result.ok.returncode == 0

def test_run_verification_success() -> None:
    """Test successful verification as effect."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        effect = run_verification("test", Block.of_seq(["cmd"]))
        result = effect.run()
        assert result.is_ok()
        assert "Passed" in result.ok

def test_run_verification_failure() -> None:
    """Test failed verification as effect."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "error"
        effect = run_verification("test", Block.of_seq(["cmd"]))
        result = effect.run()
        assert result.is_error()
        assert isinstance(result.error, VerificationOutcome)
        assert "error" in result.error.message

############################################
# Property-Based Tests
############################################

@given(verification_outcome_strategy())
def test_verification_outcome_properties(outcome: VerificationOutcome) -> None:
    """Test properties of verification outcomes."""
    assert isinstance(outcome.name, str)
    assert isinstance(outcome.message, str)

@given(st.lists(st.text(min_size=1), min_size=1))
def test_verify_check_properties(commands: list[str]) -> None:
    """Test properties of verification checks."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        result = verify_check(commands)
        assert isinstance(result, Result)

############################################
# Integration Tests
############################################

def test_verification_workflow(mock_subprocess_run: MagicMock) -> None:
    """Test complete verification workflow."""
    mock_subprocess_run.return_value.returncode = 0
    
    # Run all verifications
    all_result = verify_all()
    assert all_result.is_ok()
    
    # Run individual check
    check_result = verify_check(["test"])
    assert check_result.is_ok()
    
    # Run as effect
    effect_result = run_verification("test", Block.of_seq(["cmd"])).run()
    assert effect_result.is_ok()

def test_error_handling_workflow(mock_subprocess_run: MagicMock) -> None:
    """Test error handling in verification workflow."""
    # Command failure
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.stderr = "error"
    result1 = verify_check(["test"])
    assert result1.is_error()
    assert isinstance(result1.error, VerificationOutcome)
    
    # Execution error
    mock_subprocess_run.side_effect = Exception("error")
    result2 = verify_check(["test"])
    assert result2.is_error()
    assert isinstance(result2.error, VerificationOutcome)
    assert result2.error.name == "Execution Error"