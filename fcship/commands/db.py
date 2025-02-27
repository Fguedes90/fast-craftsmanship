"""Database management commands using Railway Oriented Programming."""

import subprocess

from dataclasses import dataclass

import typer

from expression import Error, Ok, effect, tagged_union
from rich.console import Console
from rich.panel import Panel

from fcship.tui.display import DisplayContext, error_message, success_message
from fcship.utils.error_handling import handle_command_errors


@dataclass(frozen=True)
class CommandOutput:
    """Immutable command output."""

    stdout: str
    stderr: str
    returncode: int


@tagged_union
class DbError:
    """Tagged union for database operation errors."""

    tag: str
    validation_error: str | None = None
    migration_error: tuple[str, str] | None = None

    @staticmethod
    def ValidationError(message: str) -> "DbError":
        """Creates a validation error."""
        return DbError(tag="validation_error", validation_error=message)

    @staticmethod
    def MigrationError(command: str, details: str) -> "DbError":
        """Creates a migration execution error."""
        return DbError(tag="migration_error", migration_error=(command, details))


@effect.result[CommandOutput, DbError]()
def run_command(command: list[str], status_message: str, console: Console):
    """Run a shell command and return its result."""
    try:
        with console.status(status_message):
            process = subprocess.run(command, capture_output=True, text=True, check=False)

        output = CommandOutput(
            stdout=process.stdout, stderr=process.stderr, returncode=process.returncode
        )

        if process.returncode != 0:
            error_details = (
                output.stderr or output.stdout or f"Command failed with code {process.returncode}"
            )
            yield Error(DbError.MigrationError(" ".join(command), error_details))
            return

        yield Ok(output)
    except Exception as e:
        yield Error(DbError.MigrationError(" ".join(command), str(e)))


@effect.result[str, DbError]()
def create_migration(name: str, ctx: DisplayContext = None):
    """Create a new migration."""
    display_ctx = ctx or DisplayContext(console=Console())

    # Run alembic command
    result = yield from run_command(
        ["alembic", "revision", "-m", name],
        "[bold green]Creating migration...",
        display_ctx.console,
    )

    if result.is_ok():
        output = result.ok
        # Display output
        if output.stdout.strip():
            display_ctx.console.print(
                Panel(output.stdout, title="Migration Output", border_style="blue")
            )
        # Success message
        yield from success_message(display_ctx, f"Created migration: {name}")
        yield Ok(f"Migration '{name}' created successfully")

    return Error(result.error)


@effect.result[str, DbError]()
def run_migrations(ctx: DisplayContext = None):
    """Run pending migrations."""
    display_ctx = ctx or DisplayContext(console=Console())

    # Run alembic command
    result = yield from run_command(
        ["alembic", "upgrade", "head"], "[bold green]Applying migrations...", display_ctx.console
    )

    if result.is_ok():
        output = result.ok
        # Display output
        if output.stdout.strip():
            display_ctx.console.print(
                Panel(output.stdout, title="Migration Output", border_style="blue")
            )
        # Success message
        yield from success_message(display_ctx, "Migrations applied successfully")
        yield Ok("Migrations applied successfully")

    return Error(result.error)


@effect.result[str, DbError]()
def rollback_migration(ctx: DisplayContext = None):
    """Rollback last migration."""
    display_ctx = ctx or DisplayContext(console=Console())

    # Run alembic command
    result = yield from run_command(
        ["alembic", "downgrade", "-1"],
        "[bold yellow]Rolling back migration...",
        display_ctx.console,
    )

    if result.is_ok():
        output = result.ok
        # Display output
        if output.stdout.strip():
            display_ctx.console.print(
                Panel(output.stdout, title="Rollback Output", border_style="yellow")
            )
        # Success message
        yield from success_message(display_ctx, "Migration rolled back successfully")
        yield Ok("Migration rolled back successfully")

    return Error(result.error)


@effect.result[tuple[str, str | None], DbError]()
def validate_db_operation(operation: str, name: str | None = None):
    """Validate database operation."""
    valid_operations = ["migration", "migrate", "rollback"]

    if operation not in valid_operations:
        yield Error(
            DbError.ValidationError(
                f"Invalid operation '{operation}'. Must be one of: {', '.join(valid_operations)}"
            )
        )
        return

    if operation == "migration" and (name is None or not name.strip()):
        yield Error(DbError.ValidationError("Migration name is required for 'migration' operation"))
        return

    yield Ok((operation, name))


@effect.result[str, DbError]()
def handle_db_error(error: DbError, ctx: DisplayContext = None):
    """Handle database errors."""
    display_ctx = ctx or DisplayContext(console=Console())

    match error:
        case DbError(tag="validation_error") if error.validation_error is not None:
            yield from error_message(display_ctx, "Validation Error", error.validation_error)
        case DbError(tag="migration_error") if error.migration_error is not None:
            command, details = error.migration_error
            yield from error_message(display_ctx, f"Error executing '{command}'", details)
        case _:
            yield from error_message(display_ctx, "Unknown Error", "An unknown error occurred")

    yield Error(error)


@handle_command_errors
@effect.result[str, DbError]()
def db(
    operation: str = typer.Argument(..., help="Operation to perform [migration/migrate/rollback]"),
    name: str | None = typer.Argument(None, help="Name of the migration"),
    ctx: DisplayContext = None,
):
    """Manage database migrations."""
    display_ctx = ctx or DisplayContext(console=Console())

    # Validate operation
    validation = yield from validate_db_operation(operation, name)
    if validation.is_error():
        yield from handle_db_error(validation.error, display_ctx)
        return

    operation_val, name_val = validation.ok

    # Execute operation
    match operation_val:
        case "migration":
            result = yield from create_migration(name_val, display_ctx)  # type: ignore
        case "migrate":
            result = yield from run_migrations(display_ctx)
        case "rollback":
            result = yield from rollback_migration(display_ctx)
        case _:
            yield Error(DbError.ValidationError(f"Unsupported operation: {operation_val}"))
            return

    if result.is_error():
        yield from handle_db_error(result.error, display_ctx)
        return

    yield Ok(result.ok)
