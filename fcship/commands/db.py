"""Database command implementation."""
from typing import Optional
import typer
from expression import Error, Ok, Result, effect
from fcship.tui import DisplayContext
from fcship.utils import console
from .base import Command

@effect.result[str, str]()
def validate_db_operation(operation: str):
    """Validate database operation"""
    valid_operations = ["migrate", "rollback", "reset"]
    if operation in valid_operations:
        yield Ok(operation)
    else:
        yield Error(f"Invalid operation '{operation}'. Supported operations: {', '.join(valid_operations)}")

@effect.result[str, str]()
def handle_db_operation(operation: str):
    """Handle database operations."""
    try:
        console.print(f"[blue]Executing database operation: {operation}[/]")
        # Implementation for database operations will go here
        # For now, just return a placeholder message
        yield Ok(f"Database {operation} completed successfully")
    except Exception as e:
        yield Error(f"Failed to execute database operation: {e!s}")

@effect.result[str, str]()
def db(
    operation: str = typer.Argument(..., help="Operation to perform [migrate, rollback, reset]"),
) -> Result[str, str]:
    """Manage database operations."""
    try:
        # Validate operation
        operation_result = yield from validate_db_operation(operation)
        if operation_result.is_error():
            yield Error(operation_result.error)
            return

        # Execute operation
        result = yield from handle_db_operation(operation)
        if result.is_error():
            yield Error(result.error)
            return
        
        yield Ok(result.ok)
    except Exception as e:
        yield Error(f"Unexpected error: {e!s}")

class DbCommand(Command):
    def __init__(self):
        super().__init__(
            name="db",
            help="Manage database operations.\n\nAvailable operations:\n- migrate: Run migrations\n- rollback: Rollback last migration\n- reset: Reset database\n\nExample: craftsmanship db migrate"
        )
    
    def execute(self, operation: str, ctx: Optional[DisplayContext] = None):
        """Execute the database command with the given operation."""
        if not operation:
            self.display_info()
            return
            
        result = effect.attempt(db, operation)
        if isinstance(result, Error):
            console.print(f"[red]Error: {result.error}[/red]")
            return
        return result.ok
