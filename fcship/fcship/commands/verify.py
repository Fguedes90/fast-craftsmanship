"""Verification commands using functional programming principles."""
import subprocess
import typer
from typing import Literal, TypeVar
from collections.abc import Generator
from rich.console import Console
from rich.panel import Panel
from expression import Result, Ok, Error, pipe, effect, tagged_union
from expression.collections import seq, Map, Block
from pydantic import BaseModel, Field, ConfigDict

from ..utils import handle_command_errors
from ..utils.ui import (
    create_panel, 
    create_summary_table,
    create_table_row,
    add_row_to_table
)

T = TypeVar('T')

class CommandOutput(BaseModel):
    """Represents the output of a command execution."""
    stdout: str = Field(description="Standard output")
    stderr: str = Field(description="Standard error")

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
VERIFICATIONS = Map.of_seq([
    ("type", Block.of_seq(["mypy", "."])),
    ("lint", Block.of_seq(["flake8"])),
    ("test", Block.of_seq(["pytest"])),
    ("format", Block.of_seq(["black", "--check", "."]))
])

def format_command(cmd: Block[str]) -> str:
    """Formats a command Block into a string."""
    return " ".join(cmd)

def format_verification_output(outcome: VerificationOutcome) -> Panel:
    """Formats verification outcome as a rich panel."""
    match outcome:
        case VerificationOutcome(tag="success"):
            return create_panel("[green]Success[/green]", outcome.success or "", "green")
        case VerificationOutcome(tag="failure"):
            return create_panel(f"[red]{outcome.failure[0]} Failed[/red]", outcome.failure[1], "red")
        case VerificationOutcome(tag="validation_error"):
            return create_panel("[red]Validation Error[/red]", outcome.validation_error or "", "red")
        case VerificationOutcome(tag="execution_error"):
            return create_panel(
                "[red]Execution Error[/red]",
                f"Command: {outcome.execution_error[0]}\n\n{outcome.execution_error[1]}",
                "red"
            )
        case _:
            return create_panel("[red]Unknown Error[/red]", "An unknown error occurred", "red")

def validate_check_type(check_type: str) -> Result[str, VerificationOutcome]:
    """Validates the check type parameter."""
    valid_types = pipe(
        ["all"] + list(VERIFICATIONS.keys()),
        Block.of_seq
    )
    
    if check_type in valid_types:
        return Ok(check_type)
        
    return Error(VerificationOutcome.ValidationError(
        f"Invalid check type. Must be one of: {', '.join(valid_types)}"
    ))

def run_command(cmd: Block[str]) -> Result[CommandOutput, VerificationOutcome]:
    """Runs a command and returns its output."""
    if not cmd:
        return Error(VerificationOutcome.ExecutionError("", "Empty command"))
        
    try:
        process = subprocess.run(
            list(cmd), 
            capture_output=True,
            text=True
        )
        output = CommandOutput(stdout=process.stdout, stderr=process.stderr)
        
        if process.returncode != 0:
            return Error(VerificationOutcome.ExecutionError(
                " ".join(cmd),
                output.stderr or output.stdout or f"Command failed with code {process.returncode}"
            ))
            
        return Ok(output)
    except Exception as e:
        return Error(VerificationOutcome.ExecutionError(
            " ".join(cmd),
            str(e)
        ))

def run_verification(name: str, cmd: Block[str]) -> Result[str, VerificationOutcome]:
    """Runs a single verification check."""
    if not cmd:
        return Error(VerificationOutcome.ExecutionError(name, "Empty command"))
        
    try:
        process = subprocess.run(
            list(cmd), 
            capture_output=True,
            text=True
        )
        
        if process.returncode != 0:
            return Error(VerificationOutcome.Failure(
                name,
                process.stderr or process.stdout or f"Command failed with code {process.returncode}"
            ))
            
        return Ok(process.stdout)
    except Exception as e:
        return Error(VerificationOutcome.ExecutionError(
            name,
            str(e)
        ))

def process_verification_results(
    results: Block[tuple[str, Result[str, VerificationOutcome]]],
    console: Console
) -> Result[None, VerificationOutcome]:
    """Process verification results."""
    try:
        # Create and print summary table
        table = create_summary_table(results)
        console.print("\nVerification Results")
        console.print(table)
        
        # Get failures
        failures = results.filter(lambda r: r[1].is_error())
        if not failures:
            return Ok(None)
            
        # Show all failure details
        for name, result in failures:
            if result.is_error():
                console.print(format_verification_output(result.error))
                
        return Error(VerificationOutcome.Failure(
            "Verification",
            "One or more verifications failed"
        ))
    except Exception as e:
        return Error(VerificationOutcome.ExecutionError(
            "Verification",
            str(e)
        ))

@handle_command_errors
def verify(check_type: str = "all", console: Console | None = None) -> None:
    """Run verification checks."""
    ui_console = console or Console()
    
    result = (
        validate_check_type(check_type)
        .bind(lambda t: Ok(
            VERIFICATIONS.items() if t == "all"
            else [(t, VERIFICATIONS[t])]
        ))
        .map(Block.of_seq)
        .map(lambda checks: [
            (name, run_verification(name, cmd))
            for name, cmd in checks
        ])
        .map(Block.of_seq)
        .bind(lambda results: process_verification_results(results, ui_console))
    )
    
    if result.is_error():
        ui_console.print(format_verification_output(result.error))
    else:
        ui_console.print("\n[bold green]✨ All verifications passed successfully![/bold green]")
"""Verification commands for the CLI."""
import subprocess
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable
from expression import Ok, Error, Result, pipe, effect, Effect
from expression.collections import Block, seq

from fcship.utils.file_utils import format_command

# Define generic type parameter
T = TypeVar('T')

@dataclass(frozen=True)
class CommandOutput:
    """Output from a command execution."""
    stdout: str
    stderr: str
    returncode: int

@dataclass(frozen=True)
class VerificationOutcome:
    """Represents the outcome of a verification check."""
    name: str
    message: str

    @classmethod
    def Failure(cls, name: str, message: str) -> "VerificationOutcome":
        """Create a failure outcome."""
        return cls(name=name, message=message)

    @classmethod
    def ExecutionError(cls, command: str, error: str) -> "VerificationOutcome":
        """Create an execution error outcome."""
        return cls(
            name="Execution Error", 
            message=f"Failed to execute '{command}': {error}"
        )

# Registry of verification checks
VERIFICATIONS: dict[str, list[str]] = {
    "Style": ["black --check .", "flake8 ."],
    "Types": ["mypy ."],
    "Tests": ["pytest"]
}

def validate_check_type(check_type: str) -> Result[str, VerificationOutcome]:
    """Validates the check type parameter."""
    valid_types = pipe(
        VERIFICATIONS.keys(),
        Block.of_seq,
        lambda b: b.append(Block.of_seq(["all"]))
    )
    
    return (
        Ok(check_type)
        if check_type in valid_types
        else Error(VerificationOutcome.ValidationError(
            f"Invalid check type. Must be one of: {', '.join(valid_types)}"
        ))
    )

def run_command_effect(cmd: Block[str]) -> Effect[CommandOutput, VerificationOutcome]:
    """Run command as an effect."""
    def execute() -> Result[CommandOutput, VerificationOutcome]:
        try:
            return Ok(run_command(cmd[0]))
        except Exception as e:
            return Error(VerificationOutcome.ExecutionError(cmd[0], str(e)))
            
    return Effect(execute)

def run_verification(name: str, cmd: Block[str]) -> Effect[str, VerificationOutcome]:
    """Run a single verification as an effect."""
    return Effect(lambda: run_command_effect(cmd)
                 .map(lambda output: 
                      Ok("✓ Passed") if output.returncode == 0
                      else Error(VerificationOutcome.Failure(name, output.stderr))))

def verify_all() -> Result[list[tuple[str, Result[str, VerificationOutcome]]], str]:
    """Run all verifications."""
    return (pipe(
        VERIFICATIONS,
        Block.of_seq,
        seq.map(lambda v: (v[0], verify_check(v[1]))),
        Block.of_seq,
        Ok
    ))

def verify_check(commands: list[str]) -> Result[str, VerificationOutcome]:
    """Verify a single check."""
    try:
        for cmd in commands:
            result = run_command(cmd)
            if result.returncode != 0:  # Simplified logical expression
                return Error(VerificationOutcome.Failure(
                    format_command(cmd),
                    result.stderr or result.stdout
                ))
        return Ok("✓ Passed")
    except Exception as e:
        return Error(VerificationOutcome.ExecutionError(
            format_command(commands[0]),
            str(e)
        ))

def run_command(command: str) -> CommandOutput:
    """Run a shell command and return its output."""
    try:
        proc = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=False
        )
        return CommandOutput(
            stdout=proc.stdout,
            stderr=proc.stderr,
            returncode=proc.returncode
        )
    except subprocess.SubprocessError as e:
        return CommandOutput("", str(e), -1)

@effect.result[list[tuple[str, Effect[Result[str, VerificationOutcome]]]]]()
def run_verifications() -> Result[list[tuple[str, Effect[Result[str, VerificationOutcome]]]], str]:
    """Run all verifications with effects."""
    return verify_all()

@dataclass(frozen=True)
class VerificationEffect(Generic[T]):
    """Effect for verification operations."""
    inner: Block[tuple[str, Effect[Result[str, VerificationOutcome]]]]

    @staticmethod
    def create(effects: Block[tuple[str, Effect[Result[str, VerificationOutcome]]]]) -> "VerificationEffect[T]":
        """Create a new verification effect."""
        return VerificationEffect(effects)