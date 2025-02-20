"""Commit command implementation with LLM assistance for conventional commits."""

import subprocess
import typer
from rich.prompt import Prompt
from rich.console import Console
from rich.panel import Panel
from ..utils import handle_command_errors, success_message, error_message

console = Console()

def generate_commit_message(diff: str) -> str:
    """
    Generate a conventional commit message using LLM.
    This is a placeholder function.
    Replace this with actual LLM integration if available.
    For example, prompt an LLM with the diff and instruct it to output a conventional commit.
    """
    # Dummy implementation – in production, call your LLM API here.
    # Get the actual diff content from the input parameter
    print("\nAnalyzing changes in files...")
    console.print(Panel(f"[bold]Git Diff:[/bold]\n{diff}", border_style="cyan"))
    return "feat: auto-generated commit message based on changes"

def get_changed_files() -> list[str]:
    """Return a list of changed files using `git status --porcelain`."""
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
    lines = result.stdout.splitlines()
    files = []
    files.extend(line[3:].strip() for line in lines)
    return files

@handle_command_errors
def commit_interactive() -> None:
    """Interactive commit command with LLM-assisted conventional commit generation."""
    changed_files = get_changed_files()
    if not changed_files:
        console.print(Panel("[yellow]No changes detected to commit.[/yellow]", border_style="yellow"))
        raise typer.Exit()

    # Stage all files by default
    subprocess.run(["git", "add", "."], check=True)

    # Retrieve the list of staged files
    result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
    staged_files = result.stdout.splitlines()

    console.print("\n[bold]Staged files:[/bold]")
    for idx, file in enumerate(staged_files, start=1):
        console.print(f"{idx}. {file}")

    console.print("\nOptions: [A] Commit all, [R] Remove all, [M] Selection manually")
    option = Prompt.ask("Select an option", choices=["A", "R", "M"], default="A")

    if option.upper() == "R":
        # Remove all files from the staging area.
        subprocess.run(["git", "reset"], check=True)
        console.print(Panel("[yellow]All files have been deselected. Commit aborted.[/yellow]", border_style="yellow"))
        raise typer.Exit()

    elif option.upper() == "M":
        # For each staged file, ask the user if it should remain staged.
        for file in staged_files:
            answer = Prompt.ask(f"Include file '{file}' in commit?", choices=["y", "n"], default="y")
            if answer.lower() == "n":
                subprocess.run(["git", "reset", file], check=True)
        # Update the list of staged files after modifications.
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
        staged_files = result.stdout.splitlines()
        if not staged_files:
            console.print(Panel("[yellow]No files selected for commit. Aborting commit.[/yellow]", border_style="yellow"))
            raise typer.Exit()

    # Obtain the diff of staged files.
    diff_result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, check=True)
    diff_text = diff_result.stdout
    if not diff_text:
        console.print(Panel("[yellow]No differences found in staged files.[/yellow]", border_style="yellow"))
        raise typer.Exit()

    # Generate the commit message using LLM.
    commit_message = generate_commit_message(diff_text)
    console.print(Panel(f"[bold]Generated Commit Message:[/bold]\n{commit_message}", border_style="blue"))

    # Ask the user to confirm the generated commit message.
    confirm = Prompt.ask("Do you want to use this commit message? (y/n)", choices=["y", "n"], default="y")
    if confirm.lower() != "y":
        console.print(Panel("[red]Commit aborted by user.[/red]", border_style="red"))
        raise typer.Exit()

    # Make the commit.
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    success_message("Commit successful.")

def commit(
    operation: str = typer.Argument(..., help="Must be 'auto'")
) -> None:
    """Run interactive commit with LLM-assisted conventional commit message generation."""
    if operation != "auto":
        error_message("Invalid operation. Only 'auto' is supported for this command.")
        raise typer.Exit(1)
    commit_interactive()
