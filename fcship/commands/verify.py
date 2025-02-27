"""Verification commands using functional programming principles."""

import subprocess

from typing import Literal, TypeVar

from expression import Error, Ok, Result, pipe, tagged_union
from expression.collections import Block, Map, seq
from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console

from fcship.tui import (
    DisplayContext,
    DisplayError,
    DisplayResult,
    create_summary_table,
    display_rule,
    error_message,
    handle_ui_error,
    success_message,
    with_ui_context,
)
from fcship.utils.error_handling import handle_command_errors

T = TypeVar("T")


class CommandOutput(BaseModel):
    """Represents the output of a command execution."""

    stdout: str = Field(description="Standard output")
    stderr: str = Field(description="Standard error")
    returncode: int = Field(description="Return code of the command")

    model_config = ConfigDict(frozen=True)


@tagged_union
class VerificationOutcome:
    """Represents all possible verification outcomes."""

    tag: Literal["success", "failure", "validation_error", "execution_error"]
    success: str | None = None
    failure: tuple[str, str] | None = None
    validation_error: str | None = None
    execution_error: tuple[str, str] | None = None

    @staticmethod
    def Success(message: str) -> "VerificationOutcome":
        """Creates a successful verification outcome."""
        return VerificationOutcome(tag="success", success=message)

    @staticmethod
    def Failure(tool: str, output: str) -> "VerificationOutcome":
        """Creates a failed verification outcome."""
        return VerificationOutcome(tag="failure", failure=(tool, output))

    @staticmethod
    def ValidationError(message: str) -> "VerificationOutcome":
        """Creates a validation error outcome."""
        return VerificationOutcome(tag="validation_error", validation_error=message)

    @staticmethod
    def ExecutionError(cmd: str, output: str) -> "VerificationOutcome":
        """Creates an execution error outcome."""
        return VerificationOutcome(tag="execution_error", execution_error=(cmd, output))

    def __str__(self) -> str:
        """String representation of the outcome."""
        match self:
            case VerificationOutcome(tag="success") if self.success is not None:
                return f"Success: {self.success}"
            case VerificationOutcome(tag="failure") if self.failure is not None:
                return f"Failure in {self.failure[0]}: {self.failure[1]}"
            case VerificationOutcome(tag="validation_error") if self.validation_error is not None:
                return f"Validation Error: {self.validation_error}"
            case VerificationOutcome(tag="execution_error") if self.execution_error is not None:
                return f"Execution Error in '{self.execution_error[0]}': {self.execution_error[1]}"
            case _:
                return "Unknown Error"


# Configuration
VERIFICATIONS = Map.of_seq(
    [
        ("type", Block.of_seq(["mypy", "."])),
        ("lint", Block.of_seq(["flake8"])),
        ("test", Block.of_seq(["pytest"])),
        ("format", Block.of_seq(["black", "--check", "."])),
    ]
)


def format_verification_output(outcome: VerificationOutcome, ctx: DisplayContext) -> DisplayResult:
    """Formats and displays verification outcome."""
    match outcome:
        case VerificationOutcome(tag="success"):
            return success_message(ctx, outcome.success or "")
        case VerificationOutcome(tag="failure"):
            return error_message(ctx, f"{outcome.failure[0]} Failed", outcome.failure[1])
        case VerificationOutcome(tag="validation_error"):
            return error_message(ctx, "Validation Error", outcome.validation_error or "")
        case VerificationOutcome(tag="execution_error"):
            return error_message(
                ctx,
                "Execution Error",
                f"Command: {outcome.execution_error[0]}\n\n{outcome.execution_error[1]}",
            )
        case _:
            return error_message(ctx, "Unknown Error", "An unknown error occurred")


def validate_check_type(check_type: str) -> Result[str, VerificationOutcome]:
    """Validates the check type parameter."""
    valid_types = pipe(["all"] + list(VERIFICATIONS.keys()), Block.of_seq)

    if check_type in valid_types:
        return Ok(check_type)

    return Error(
        VerificationOutcome.ValidationError(
            f"Invalid check type. Must be one of: {', '.join(valid_types)}"
        )
    )


def run_command(cmd: Block[str]) -> Result[CommandOutput, VerificationOutcome]:
    """Runs a command and returns its output."""
    if not cmd:
        return Error(VerificationOutcome.ExecutionError("", "Empty command"))

    try:
        process = subprocess.run(list(cmd), capture_output=True, text=True, check=False)
        output = CommandOutput(
            stdout=process.stdout, stderr=process.stderr, returncode=process.returncode
        )

        if process.returncode != 0:
            return Error(
                VerificationOutcome.ExecutionError(
                    " ".join(cmd),
                    output.stderr
                    or output.stdout
                    or f"Command failed with code {process.returncode}",
                )
            )

        return Ok(output)
    except Exception as e:
        return Error(VerificationOutcome.ExecutionError(" ".join(cmd), str(e)))


def run_verification(name: str, cmd: Block[str]) -> Result[str, VerificationOutcome]:
    """Runs a single verification check."""
    return (
        run_command(cmd)
        .map_error(
            lambda e: VerificationOutcome.Failure(name, e.execution_error[1])
            if e.tag == "execution_error"
            else e
        )
        .bind(
            lambda output: Ok("✓ Passed")
            if output.returncode == 0
            else Error(VerificationOutcome.Failure(name, output.stderr or output.stdout))
        )
    )


def process_verification_results(
    results: Block[tuple[str, Result[str, VerificationOutcome]]], console: Console
) -> Result[None, VerificationOutcome]:
    """Process verification results."""

    class DisplayResultsOperation:
        def setup(self) -> Result[None, DisplayError]:
            return Ok(None)

        def operation(self) -> DisplayResult:
            try:
                # Create and print summary table
                table = create_summary_table(results)
                if table.is_error():
                    return table

                return pipe(
                    display_rule("Verification Results", "cyan")
                    .bind(lambda _: Ok(console.print(table.ok)))
                    .bind(
                        lambda _: pipe(
                            results.filter(lambda r: r[1].is_error()),
                            seq.traverse(
                                lambda f: format_verification_output(
                                    f[1].error, DisplayContext(console=console)
                                )
                                if f[1].is_error()
                                else Ok(None)
                            ),
                        )
                    )
                )
            except Exception as e:
                return Error(DisplayError.Rendering("Failed to display results", e))

        def cleanup(self) -> Result[None, DisplayError]:
            return Ok(None)

    result = with_ui_context(DisplayResultsOperation())
    if result.is_error():
        return Error(VerificationOutcome.ExecutionError("Verification", str(result.error)))

    failures = results.filter(lambda r: r[1].is_error())
    if failures:
        return Error(
            VerificationOutcome.Failure("Verification", "One or more verifications failed")
        )

    return Ok(None)


@handle_command_errors
async def verify(check_type: str = "all", console: Console | None = None) -> None:
    """Run verification checks."""
    ui_console = console or Console()
    ctx = DisplayContext(console=ui_console)

    result = (
        validate_check_type(check_type)
        .bind(lambda t: Ok(VERIFICATIONS.items() if t == "all" else [(t, VERIFICATIONS[t])]))
        .map(Block.of_seq)
        .map(lambda checks: [(name, run_verification(name, cmd)) for name, cmd in checks])
        .map(Block.of_seq)
        .bind(lambda results: process_verification_results(results, ui_console))
    )

    if result.is_error():
        error_result = format_verification_output(result.error, ctx)
        if error_result.is_error():
            await handle_ui_error(error_result.error)
    else:
        success_result = success_message(ctx, "✨ All verifications passed successfully!")
        if success_result.is_error():
            await handle_ui_error(success_result.error)
