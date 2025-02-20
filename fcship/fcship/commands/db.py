"""Database management commands."""
from typing import Optional
import typer
import subprocess
from rich.panel import Panel
from ..utils import (
    handle_command_errors, 
    validate_operation, 
    success_message, 
    error_message,
    console
)

@handle_command_errors
def create_migration(name: str) -> None:
    """Create a new migration."""
    try:
        with console.status("[bold green]Creating migration..."):
            result = subprocess.run(
                ["alembic", "revision", "-m", name],
                check=True,
                capture_output=True,
                text=True
            )
            console.print(Panel(result.stdout, title="Migration Output", border_style="blue"))
        success_message(f"Created migration: {name}")
    except subprocess.CalledProcessError as e:
        error_message("Failed to create migration", e.stderr)
        raise typer.Exit(1)

@handle_command_errors
def run_migrations() -> None:
    """Run pending migrations."""
    try:
        with console.status("[bold green]Applying migrations..."):
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                check=True,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                console.print(Panel(result.stdout, title="Migration Output", border_style="blue"))
        success_message("Successfully applied migrations")
    except subprocess.CalledProcessError as e:
        error_message("Failed to apply migrations", e.stderr)
        raise typer.Exit(1)

@handle_command_errors
def rollback_migration() -> None:
    """Rollback last migration."""
    try:
        with console.status("[bold yellow]Rolling back migration..."):
            result = subprocess.run(
                ["alembic", "downgrade", "-1"],
                check=True,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                console.print(Panel(result.stdout, title="Rollback Output", border_style="yellow"))
        success_message("Successfully rolled back migration")
    except subprocess.CalledProcessError as e:
        error_message("Failed to rollback migration", e.stderr)
        raise typer.Exit(1)

def db(
    operation: str = typer.Argument(..., help="Operation to perform [migration/migrate/rollback]"),
    name: Optional[str] = typer.Argument(None, help="Name of the migration")
) -> None:
    """Manage database migrations."""
    valid_operations = ["migration", "migrate", "rollback"]
    validate_operation(operation, valid_operations, name, requires_name=["migration"])
    
    if operation == "migration":
        create_migration(name)  # type: ignore (we know name is not None due to validation)
    elif operation == "migrate":
        run_migrations()
    else:  # rollback
        rollback_migration()