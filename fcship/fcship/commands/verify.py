"""Verification commands using functional programming principles.

This module provides functionality to run and verify different types of checks
(typing, linting, testing, formatting) in a purely functional way using the Expression library.
Using Railway-Oriented Programming for error handling and effect composition.
"""

import subprocess
import typer
from dataclasses import dataclass
from typing import Literal, TypeAlias, TypeVar, Generic, Any, Protocol
from collections.abc import Callable
# Rich UI components
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Expression library imports
from expression import (
    Result, 
    Ok, 
    Error, 
    pipe,
    tagged_union, 
    case, 
    tag,
    
)
from expression.collections import seq, Map, Seq, Block

# Pydantic models
from pydantic import BaseModel, Field, ConfigDict
from typing_extensions import Annotated

# Local imports
from ..utils import handle_command_errors

# Generic type variables
T = TypeVar('T')
E = TypeVar('E')
TResult = TypeVar('TResult')
TError = TypeVar('TError')

#region Domain Models

@tagged_union
class VerificationOutcome:
    """Represents all possible outcomes of a verification check."""
    tag: Literal["success", "failure", "validation_error", "execution_error"] = tag()
    
    success: str = case()  # Success message
    failure: tuple[str, str] = case()  # (tool_name, error_output)
    validation_error: str = case()  # Validation error message
    execution_error: tuple[str, str] = case()  # (command, error_output)

    @staticmethod
    def Success(message: str) -> "VerificationOutcome":
        """Creates a successful verification outcome."""
        return VerificationOutcome(success=message)
    
    @staticmethod
    def Failure(tool: str, output: str) -> "VerificationOutcome":
        """Creates a failed verification outcome."""
        return VerificationOutcome(failure=(tool, output))
    
    @staticmethod
    def ValidationError(message: str) -> "VerificationOutcome":
        """Creates a validation error outcome."""
        return VerificationOutcome(validation_error=message)
    
    @staticmethod
    def ExecutionError(cmd: str, output: str) -> "VerificationOutcome":
        """Creates an execution error outcome."""
        return VerificationOutcome(execution_error=(cmd, output))

# Now we can define our type aliases
VerificationResult: TypeAlias = Result[str, VerificationOutcome]
VerificationName: TypeAlias = str
VerificationCommand: TypeAlias = Block[str]
VerificationPair: TypeAlias = tuple[VerificationName, VerificationCommand]
VerificationResults: TypeAlias = Block[tuple[VerificationName, VerificationResult]]
ConsoleOutput: TypeAlias = str | Table | Panel
EffectResult: TypeAlias = Result[None, VerificationOutcome]

class CommandOutput(BaseModel):
    """Represents the output of a command execution."""
    stdout: Annotated[str, Field(description="Standard output from command")] 
    stderr: Annotated[str, Field(description="Standard error from command")]

    model_config = ConfigDict(frozen=True)

#endregion

#region Protocols and Type Definitions

class Effectful(Protocol[TResult, TError]):
    """Protocol for effectful computations that can fail."""
    
    def execute(self) -> Result[TResult, TError]: ...

class ConsoleEffect(Protocol):
    """Protocol for console output effects."""
    
    def print(self, msg: ConsoleOutput) -> None: ...
    def status(self, msg: str) -> Any: ...

#endregion

#region Functional Utilities

class Pure(Generic[T]):
    """Represents a pure computation that can be applied lazily."""
    
    def __init__(self, computation: Callable[[], T]) -> None:
        self._computation = computation
        
    def map[U](self, f: Callable[[T], U]) -> "Pure[U]":
        """Maps the computation through a function."""
        return Pure(lambda: f(self._computation()))
    
    def bind[U](self, f: Callable[[T], "Pure[U]"]) -> "Pure[U]":
        """Chains computations together."""
        return Pure(lambda: f(self._computation()).apply())
    
    def apply(self) -> T:
        """Applies the computation to get the result."""
        return self._computation()

class Effect(Generic[T, E]):
    """Represents an effectful computation that can fail."""
    
    def __init__(self, computation: Callable[[], Result[T, E]]) -> None:
        self._computation = computation
    
    def map[U](self, f: Callable[[T], U]) -> "Effect[U, E]":
        """Maps the successful result through a function."""
        return Effect(lambda: self._computation().map(f))
    
    def bind[U](self, f: Callable[[T], "Effect[U, E]"]) -> "Effect[U, E]":
        """Chains effectful computations together."""
        return Effect(lambda: self._computation().bind(
            lambda x: f(x).execute()
        ))
    
    def execute(self) -> Result[T, E]:
        """Executes the effectful computation."""
        return self._computation()

def compose[T, U, V](f: Callable[[T], U], g: Callable[[U], V]) -> Callable[[T], V]:
    """Composes two functions."""
    return lambda x: g(f(x))

def tap[T](f: Callable[[T], Any]) -> Callable[[T], T]:
    """Creates a function that runs an effect and returns the original value."""
    def tap_effect(x: T) -> T:
        f(x)
        return x
    return tap_effect

def lift[T, E](f: Callable[..., T]) -> Callable[..., Result[T, E]]:
    """Lifts a function into the Result context."""
    def lifted(*args: Any, **kwargs: Any) -> Result[T, E]:
        try:
            return Ok(f(*args, **kwargs))
        except Exception as e:
            return Error(e)
    return lifted

def effect_of[T, E](value: T) -> Effect[T, E]:
    """Creates a successful effect."""
    return Effect(lambda: Ok(value))

def effect_error[T, E](error: E) -> Effect[T, E]:
    """Creates a failed effect."""
    return Effect(lambda: Error(error))

#endregion

# Initialize rich console for output
console = Console()

#region Configuration

VERIFICATIONS = Map.of_seq([
    ("type", Block.of_seq(["mypy", "."])),
    ("lint", Block.of_seq(["flake8"])),
    ("test", Block.of_seq(["pytest"])),
    ("format", Block.of_seq(["black", "--check", "."])),
])

#endregion

#region Effects

class ConsoleIO:
    """Pure console IO operations."""
    
    def __init__(self, console: Console) -> None:
        self._console = console
    
    def print(self, msg: ConsoleOutput) -> Result[None, VerificationOutcome]:
        """Prints message to console."""
        return Effect(lambda: 
            Ok(self._console.print(msg))
        )
    
    def status(self, msg: str) -> Result[None, VerificationOutcome]:
        """Shows status message."""
        return Effect(lambda:
            Ok(self._console.status(msg))
        )

# Initialize console effects
console_io = ConsoleIO(Console())

def run_command(cmd: VerificationCommand) -> Result[CommandOutput, VerificationOutcome]:
    """Runs a command in a pure way."""
    return Effect(lambda: 
        lift(subprocess.run)(
            cmd.to_list(), 
            capture_output=True, 
            text=True
        ).map(lambda result: 
            CommandOutput(stdout=result.stdout, stderr=result.stderr)
        ).map_error(lambda err: 
            VerificationOutcome.ExecutionError(
                format_command(cmd), 
                str(err)
            )
        )
    )

#endregion

#region Pure Functions

def format_command(cmd: VerificationCommand) -> str:
    """Formats a command Block into a string."""
    return " ".join(cmd)

def create_table_row(name_result: tuple[str, VerificationResult]) -> tuple[str, str]:
    """Creates a single table row from a verification result."""
    name, result = name_result
    status = "[green]✨ Passed[/green]" if result.is_ok() else "[red]❌ Failed[/red]"
    return (name.title(), status)

def add_row_to_table(table: Table, row: tuple[str, str]) -> Table:
    """Adds a row to the table in a functional way."""
    table.add_row(*row)
    return table

def create_panel(title: str, content: str, style: str) -> Pure[Panel]:
    """Creates a panel in a pure way."""
    return Pure(lambda: Panel(content, title=title, border_style=style))

def format_verification_output(outcome: VerificationOutcome) -> Pure[Panel]:
    """Formats verification outcome as a rich panel."""
    match outcome:
        case VerificationOutcome(tag="success", success=msg):
            return create_panel("[green]Success[/green]", msg, "green")
        case VerificationOutcome(tag="failure", failure=(tool, output)):
            return create_panel(f"[red]{tool} Failed[/red]", output, "red")
        case VerificationOutcome(tag="validation_error", validation_error=msg):
            return create_panel("[red]Validation Error[/red]", msg, "red")
        case VerificationOutcome(tag="execution_error", execution_error=(cmd, output)):
            return create_panel(
                "[red]Execution Error[/red]",
                f"Command: {cmd}\n\n{output}",
                "red"
            )

def create_summary_table(results: VerificationResults) -> Pure[Table]:
    """Creates a summary table of verification results."""
    def init_table() -> Table:
        table = Table(title="Verification Results")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="bold")
        return table
    
    return Pure(lambda: pipe(
        results,
        seq.map(create_table_row),
        Block.of_seq,
        lambda rows: seq.fold(add_row_to_table, init_table(), rows)
    ))

def validate_check_type(check_type: str) -> Result[str, VerificationOutcome]:
    """Validates the check type parameter."""
    valid_types = Block.of_seq(VERIFICATIONS.keys()).append("all")
    return (
        Ok(check_type)
        if check_type in valid_types
        else Error(VerificationOutcome.ValidationError(
            f"Invalid check type. Must be one of: {', '.join(valid_types)}"
        ))
    )

#endregion

#region Verification Logic

def run_verification(name: str, cmd: Block[str]) -> Effect[str, VerificationOutcome]:
    """Runs a single verification check."""
    return (
        run_command(cmd)
        .map(lambda out: out.stdout)
        .map_error(lambda err: 
            err if isinstance(err, VerificationOutcome)
            else VerificationOutcome.ExecutionError(name, str(err))
        )
    )

def process_verification_results(
    results: VerificationResults
) -> Effect[None, VerificationOutcome]:
    """Processes verification results."""
    def show_result(result: VerificationResult) -> Effect[None, VerificationOutcome]:
        panel = format_verification_output(result.error).apply()
        return console_io.print(panel)
    
    table = create_summary_table(results).apply()
    failures = pipe(
        results,
        seq.filter(lambda x: x[1].is_error()),
        Block.of_seq
    )
    
    return (
        console_io.print(table)
        .bind(lambda _: 
            pipe(
                failures,
                seq.iter(lambda f: show_result(f[1])),
                lambda _: (
                    effect_of(None)
                    if failures.is_empty
                    else effect_error(
                        VerificationOutcome
                        .Failure("verification", "Some checks failed")
                    )
                )
            )
        )
    )

#endregion

#region Main Command

@handle_command_errors
def verify(check_type: str = "all") -> None:
    """Runs verification checks using functional programming principles."""
    with console_io._console.status("[bold green]Running verifications..."):
        def run_checks(validated_type: str) -> VerificationResults:
            """Runs the specified verification checks."""
            checks = (VERIFICATIONS if validated_type == "all" 
                     else Map.of_seq([(validated_type, VERIFICATIONS[validated_type])]))
            return pipe(
                checks.items(),
                Block.of_seq,
                seq.map(lambda item: 
                    (item[0], run_verification(*item).execute())
                )
            )
        
        result = (
            validate_check_type(check_type)
            .map(run_checks)
            .bind(lambda results: 
                process_verification_results(results).execute()
            )
        )
        
        match result:
            case Error(outcome):
                panel = format_verification_output(outcome).apply()
                console_io._console.print(panel)
                raise typer.Exit(1)
            case Ok(_):
                console_io._console.print(
                    "\n[bold green]✨ All verifications passed successfully![/bold green]"
                )

#endregion
