"""Commit command implementation with LLM assistance for conventional commits."""

import typer

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from ...utils import error_message, handle_command_errors, success_message
from .generate_commit_message import combine_commit_messages, generate_commit_message
from .utils import GitCommands, GitStatus

console = Console()


def display_status(status: GitStatus) -> bool:
    """Display the current status of files with color coding. Returns True if there are changes."""
    if not status.has_changes():
        console.print(
            Panel("[yellow]No changes detected to commit.[/yellow]", border_style="yellow")
        )
        return False

    console.print("\n[bold]Changes detected:[/bold]")

    if status.renamed:
        console.print("\n[cyan]Renamed files:[/cyan]")
        for file in status.renamed:
            console.print(f"  {file.display_path}")

    if status.added:
        console.print("\n[green]New files:[/green]")
        for file in status.added:
            console.print(f"  {file.path}")

    if status.modified:
        console.print("\n[yellow]Modified files:[/yellow]")
        for file in status.modified:
            console.print(f"  {file.path}")

    if status.deleted:
        console.print("\n[red]Deleted files:[/red]")
        for file in status.deleted:
            console.print(f"  {file.path}")

    if status.untracked:
        console.print("\n[dim]Untracked files:[/dim]")
        for file in status.untracked:
            console.print(f"  {file.path}")

    return True


def generate_commit_messages_for_status(status: GitStatus) -> list[str]:
    """Generate commit messages for each file change."""
    messages = []

    # First handle renamed files
    for file in status.renamed:
        if file.original_path:
            messages.append(f"🚚 move: {file.original_path} -> {file.path}")
            # Check for additional modifications in renamed file
            diff = GitCommands.get_file_diff(file.path)
            if diff and len(diff.strip()) > 0:
                mod_message = generate_commit_message(diff)
                if mod_message and not mod_message.startswith("🚚"):
                    messages.append(f"✨ update: {file.path} - Modified after move")

    # Handle other changes
    for file in status.added:
        messages.append(f"➕ add: {file.path}")

    for file in status.deleted:
        messages.append(f"🗑️ remove: {file.path}")

    for file in status.modified:
        diff = GitCommands.get_file_diff(file.path)
        if diff:
            msg = generate_commit_message(diff)
            if msg:
                messages.append(f"✨ update: {file.path} - {msg}")

    for file in status.untracked:
        messages.append(f"➕ add: {file.path}")

    return messages


@handle_command_errors
def commit_interactive() -> None:
    """Interactive commit command with LLM-assisted conventional commit generation."""
    # Ensure we're in a git repository
    git_root = GitCommands.get_git_root()
    if not git_root:
        error_message("Not a git repository")
        raise typer.Exit(1)

    # Get and display status of files
    status = GitCommands.get_status()
    if not display_status(status):
        raise typer.Exit()

    # Ask user what to do with the changes
    console.print("\nOptions: [A] Commit all, [R] Remove all, [M] Selection manually")
    option = Prompt.ask("Select an option", choices=["A", "R", "M"], default="A")

    if option.upper() == "R":
        # Remove all files from staging area
        for file_path in status.all_files():
            GitCommands.unstage_file(file_path)
        console.print(
            Panel(
                "[yellow]All files have been deselected. Commit aborted.[/yellow]",
                border_style="yellow",
            )
        )
        raise typer.Exit()

    selected_files: GitStatus = GitStatus()
    if option.upper() == "M":
        # Handle each file type separately
        for status_type in ["renamed", "added", "modified", "deleted", "untracked"]:
            files = getattr(status, status_type)
            if not files:
                continue

            console.print(f"\n[bold]{status_type.title()} files:[/bold]")
            for file in files:
                answer = Prompt.ask(
                    f"Include '{file.display_path}'?", choices=["y", "n"], default="y"
                )
                if answer.lower() == "y":
                    getattr(selected_files, status_type).append(file)
    else:
        # Use all files
        selected_files = status

    # Stage all selected changes
    GitCommands.stage_changes(selected_files)

    # Generate commit messages for each change
    commit_messages = generate_commit_messages_for_status(selected_files)

    if not commit_messages:
        console.print(Panel("[yellow]No changes to commit.[/yellow]", border_style="yellow"))
        raise typer.Exit()

    # Display and confirm commit messages
    console.print("\n[bold]Generated Commit Messages:[/bold]")
    for msg in commit_messages:
        console.print(f"  {msg}")

    # Combine messages
    final_message = combine_commit_messages(commit_messages)

    # Confirm and commit
    confirm = Prompt.ask(
        "\nDo you want to use these commit messages?", choices=["y", "n"], default="y"
    )
    if confirm.lower() != "y":
        console.print(Panel("[red]Commit aborted by user.[/red]", border_style="red"))
        raise typer.Exit()

    GitCommands.make_commit(final_message)
    success_message("Commit successful.")


def commit(operation: str = typer.Argument(..., help="Must be 'auto'")) -> None:
    """Run interactive commit with LLM-assisted conventional commit message generation."""
    if operation != "auto":
        error_message("Invalid operation. Only 'auto' is supported for this command.")
        raise typer.Exit(1)
    commit_interactive()
