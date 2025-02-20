"""Verification commands."""
import typer
import subprocess
from typing import Tuple, List, Callable
from rich.table import Table
from rich.panel import Panel
from ..utils import (
    handle_command_errors,
    validate_operation,
    success_message,
    error_message,
    console
)

class VerificationError(Exception):
    """Custom error for verification failures."""
    def __init__(self, tool: str, output: str):
        self.tool = tool
        self.output = output
        super().__init__(f"{tool} check failed")

def run_command(cmd: List[str], tool: str) -> Tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except FileNotFoundError:
        return False, f"{tool} is not installed. Run: pip install {tool}"

@handle_command_errors
def run_type_checking() -> None:
    """Run mypy type checking."""
    with console.status("[bold blue]Running type checking..."):
        success, output = run_command(["mypy", "."], "mypy")
        if not success:
            raise VerificationError("Type checking", output)
    success_message("Type checking passed")

@handle_command_errors
def run_linting() -> None:
    """Run flake8 linting."""
    with console.status("[bold blue]Running linting..."):
        success, output = run_command(["flake8"], "flake8")
        if not success:
            raise VerificationError("Linting", output)
    success_message("Linting passed")

@handle_command_errors
def run_tests() -> None:
    """Run pytest tests."""
    with console.status("[bold blue]Running tests..."):
        success, output = run_command(["pytest"], "pytest")
        if not success:
            raise VerificationError("Tests", output)
    success_message("Tests passed")

@handle_command_errors
def run_format_check() -> None:
    """Run black format checking."""
    with console.status("[bold blue]Checking code format..."):
        success, output = run_command(["black", "--check", "."], "black")
        if not success:
            raise VerificationError("Format checking", output)
    success_message("Format checking passed")

VERIFICATION_TYPES = {
    "type": (run_type_checking, "Run type checking only"),
    "lint": (run_linting, "Run linting only"),
    "test": (run_tests, "Run tests only"),
    "format": (run_format_check, "Run format checking only"),
    "all": (None, "Run all verifications")
}

def show_verification_summary(failed_checks: List[Tuple[str, str]]) -> None:
    """Display a summary table of verification results."""
    table = Table(title="Verification Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="bold")
    
    all_checks = ["Type checking", "Linting", "Tests", "Format checking"]
    failed_check_names = [name for name, _ in failed_checks]
    
    for check in all_checks:
        status = ("❌ Failed", "red") if check in failed_check_names else ("✨ Passed", "green")
        table.add_row(check, f"[{status[1]}]{status[0]}[/{status[1]}]")
    
    console.print(table)
    
    if failed_checks:
        for name, error in failed_checks:
            console.print(Panel(
                error,
                title=f"[red]{name} Output[/red]",
                border_style="red"
            ))

def verify(
    check_type: str = typer.Argument(
        "all",
        help="Type of check to run [all/type/lint/test/format]"
    )
) -> None:
    """Run verification checks.
    
    Args:
        check_type: Type of check to run. Use 'all' to run all checks.
    """
    validate_operation(check_type, list(VERIFICATION_TYPES.keys()))
    
    if check_type == "all":
        checks: List[Tuple[str, Callable[[], None]]] = [
            ("Type checking", run_type_checking),
            ("Linting", run_linting),
            ("Tests", run_tests),
            ("Format checking", run_format_check)
        ]
        
        failed_checks: List[Tuple[str, str]] = []
        
        with console.status("[bold green]Running verifications...") as status:
            for name, check_fn in checks:
                status.update(f"[bold green]Running {name.lower()}...")
                try:
                    check_fn()
                except VerificationError as e:
                    failed_checks.append((name, e.output))
                except Exception as e:
                    failed_checks.append((name, str(e)))
        
        show_verification_summary(failed_checks)
        
        if failed_checks:
            raise typer.Exit(1)
        else:
            console.print("\n[bold green]✨ All verifications passed successfully![/bold green]")
    else:
        # Run single check
        check_fn, _ = VERIFICATION_TYPES[check_type]
        if check_fn:
            check_fn()