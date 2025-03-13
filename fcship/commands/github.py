"""GitHub command implementation."""
from typing import Optional
import typer
from expression import Error, Ok, Result, effect
from fcship.tui import DisplayContext
from fcship.utils import console
from .base import Command

@effect.result[str, str]()
def validate_github_operation(operation: str):
    """Validate GitHub operation"""
    valid_operations = ["setup", "actions"]
    if operation in valid_operations:
        yield Ok(operation)
    else:
        yield Error(f"Invalid operation '{operation}'. Supported operations: {', '.join(valid_operations)}")

@effect.result[str, str]()
def handle_github_operation(operation: str):
    """Handle GitHub operations."""
    try:
        console.print(f"[blue]Executing GitHub operation: {operation}[/]")
        # Implementation for GitHub operations will go here
        # For now, just return a placeholder message
        yield Ok(f"GitHub {operation} completed successfully")
    except Exception as e:
        yield Error(f"Failed to execute GitHub operation: {e!s}")

@effect.result[str, str]()
def github(
    operation: str = typer.Argument(..., help="Operation to perform [setup, actions]"),
) -> Result[str, str]:
    """Manage GitHub operations."""
    try:
        # Validate operation
        operation_result = yield from validate_github_operation(operation)
        if operation_result.is_error():
            yield Error(operation_result.error)
            return

        # Execute operation
        result = yield from handle_github_operation(operation)
        if result.is_error():
            yield Error(result.error)
            return
        
        yield Ok(result.ok)
    except Exception as e:
        yield Error(f"Unexpected error: {e!s}")

class GitHubCommand(Command):
    def __init__(self):
        super().__init__(
            name="github",
            help="Manage GitHub operations.\n\nAvailable operations:\n- setup: Setup GitHub repository\n- actions: Configure GitHub Actions\n\nExample: craftsmanship github setup"
        )
    
    def execute(self, operation: str, ctx: Optional[DisplayContext] = None):
        """Execute the GitHub command with the given operation."""
        if not operation:
            self.display_info()
            return
            
        result = effect.attempt(github, operation)
        if isinstance(result, Error):
            console.print(f"[red]Error: {result.error}[/red]")
            return
        return result.ok