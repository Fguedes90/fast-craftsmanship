"""Interactive Terminal UI menu for fast-craftsmanship CLI."""

import os
import subprocess

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from ..commands import COMMAND_CATEGORIES, COMMANDS_BY_CATEGORY

console = Console()

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_title():
    """Display the application title."""
    title = Panel.fit(
        "[bold cyan]Fast-Craftsmanship CLI[/bold cyan]",
        border_style="green",
        padding=(1, 2)
    )
    console.print(title)
    console.print()

def display_categories():
    """Display the available command categories."""
    clear_screen()
    display_title()
    
    console.print("[bold]Available Command Categories:[/bold]")
    console.print()
    
    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Category", style="green")
    table.add_column("Description", style="yellow")
    table.add_column("Commands", style="blue")
    
    # Store category IDs in order for reference
    valid_categories = []
    
    index = 1
    for category_id, description in COMMAND_CATEGORIES.items():
        commands = ", ".join(COMMANDS_BY_CATEGORY.get(category_id, {}).keys())
        if commands:
            table.add_row(str(index), category_id, description, commands)
            valid_categories.append(category_id)
            index += 1
    
    console.print(table)
    console.print()
    console.print("[bold]Select a category (or 'q' to quit):[/bold]")
    
    return valid_categories

def display_commands(category_id: str):
    """Display the commands for a specific category."""
    clear_screen()
    display_title()
    
    category_name = COMMAND_CATEGORIES.get(category_id, "Unknown Category")
    console.print(f"[bold]Commands in {category_name}:[/bold]")
    console.print()
    
    commands = COMMANDS_BY_CATEGORY.get(category_id, {})
    if not commands:
        console.print("[italic]No commands available in this category.[/italic]")
        return None
    
    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Command", style="green")
    table.add_column("Description", style="yellow")
    
    for i, (cmd_name, (_, help_text)) in enumerate(commands.items(), 1):
        table.add_row(str(i), cmd_name, help_text)
    
    console.print(table)
    console.print()
    console.print("[bold]Select a command (or 'b' to go back, 'q' to quit):[/bold]")
    
    return commands

def display_command_options(category_id: str, command_name: str):
    """Display options for a specific command."""
    clear_screen()
    display_title()
    
    commands = COMMANDS_BY_CATEGORY.get(category_id, {})
    _, help_text = commands.get(command_name, (None, "No help available"))
    
    panel = Panel(
        f"[bold]{command_name}[/bold]: {help_text}",
        border_style="green",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()
    
    options_table = Table(box=None)
    options_table.add_column("Option", style="cyan", justify="right")
    options_table.add_column("Action", style="green")
    
    # Opções especiais para comandos com subcomandos
    if command_name == "github":
        options_table.add_row("1", "Show GitHub commands")
        options_table.add_row("2", "Use interactive GitHub menu")
    elif command_name == "docs":
        options_table.add_row("1", "Show docs commands")
        options_table.add_row("2", "Use interactive docs menu")
    else:
        options_table.add_row("1", f"Run '{command_name}' command")
        options_table.add_row("2", f"Show '{command_name}' help")
    
    options_table.add_row("b", "Go back to commands list")
    options_table.add_row("q", "Quit")
    
    console.print(options_table)
    console.print()
    console.print("[bold]Select an option:[/bold]")

def run_command(command_name: str, show_help: bool = False):
    """Run a command or show its help."""
    clear_screen()
    
    # Tratamento especial para o comando github, que é um sub-aplicativo Typer
    if command_name == "github":
        if show_help:
            cmd = ["python", "-m", "fcship.cli", "github", "--help"]
        else:
            # Para o comando github sem argumentos, mostrar a ajuda é o comportamento padrão
            cmd = ["python", "-m", "fcship.cli", "github"]
    elif command_name == "docs":
        if show_help:
            cmd = ["python", "-m", "fcship.cli", "docs", "--help"]
        else:
            cmd = ["python", "-m", "fcship.cli", "docs"]
    else:
        if show_help:
            cmd = ["python", "-m", "fcship.cli", command_name, "--help"]
        else:
            cmd = ["python", "-m", "fcship.cli", command_name]
    
    console.print(f"[bold]Running: [green]{' '.join(cmd)}[/green][/bold]")
    console.print()
    
    try:
        # Use subprocess.Popen to maintain interactive capabilities
        process = subprocess.Popen(cmd)
        process.wait()
        
        if process.returncode == 0:
            console.print()
            console.print("[bold green]Command completed successfully.[/bold green]")
        else:
            console.print()
            console.print(f"[bold red]Command failed with exit code {process.returncode}[/bold red]")
    except Exception as e:
        console.print()
        console.print(f"[bold red]Error: {e}[/bold red]")
    
    console.print()
    input("Press Enter to continue...")

def display_github_menu():
    """Display the GitHub submenu."""
    clear_screen()
    display_title()
    
    console.print("[bold]GitHub Commands:[/bold]")
    console.print()
    
    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Command", style="green")
    table.add_column("Description", style="yellow")
    
    commands = [
        ("repos", "List all your GitHub repositories"),
        ("branches", "List branches in a GitHub repository"),
        ("issues", "List open issues in a GitHub repository"),
        ("prs", "List pull requests for a repository"),
        ("actions", "GitHub Actions related commands"),
        ("setup", "GitHub repository setup commands"),
    ]
    
    for i, (cmd_name, help_text) in enumerate(commands, 1):
        table.add_row(str(i), cmd_name, help_text)
    
    console.print(table)
    console.print()
    console.print("[bold]Select a GitHub command (or 'b' to go back, 'q' to quit):[/bold]")
    
    return commands

def run_github_command(subcmd: str):
    """Run a GitHub subcommand."""
    clear_screen()
    cmd = ["python", "-m", "fcship.cli", "github", subcmd]
    
    console.print(f"[bold]Running: [green]{' '.join(cmd)}[/green][/bold]")
    console.print()
    
    try:
        process = subprocess.Popen(cmd)
        process.wait()
        
        if process.returncode == 0:
            console.print()
            console.print("[bold green]Command completed successfully.[/bold green]")
        else:
            console.print()
            console.print(f"[bold red]Command failed with exit code {process.returncode}[/bold red]")
    except Exception as e:
        console.print()
        console.print(f"[bold red]Error: {e}[/bold red]")
    
    console.print()
    input("Press Enter to continue...")

def display_docs_options(command_name: str):
    """Display options for docs command."""
    clear_screen()
    display_title()
    
    commands = {
        "setup": "Configurar MkDocs interativamente",
        "serve": "Iniciar servidor de desenvolvimento do MkDocs",
        "build": "Construir documentação para produção",
    }
    
    help_text = commands.get(command_name, "Documentation command")
    
    panel = Panel(
        f"[bold]docs {command_name}[/bold]: {help_text}",
        border_style="green",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()
    
    options_table = Table(box=None)
    options_table.add_column("Option", style="cyan", justify="right")
    options_table.add_column("Action", style="green")
    options_table.add_row("1", f"Run 'docs {command_name}' command")
    options_table.add_row("2", f"Show 'docs {command_name}' help")
    options_table.add_row("b", "Go back to docs commands")
    options_table.add_row("q", "Quit")
    
    console.print(options_table)
    console.print()
    console.print("[bold]Select an option:[/bold]")

def run_docs_command(subcmd: str, show_help: bool = False):
    """Run a docs subcommand."""
    clear_screen()
    if show_help:
        cmd = ["python", "-m", "fcship.cli", "docs", subcmd, "--help"]
    else:
        cmd = ["python", "-m", "fcship.cli", "docs", subcmd]
    
    console.print(f"[bold]Running: [green]{' '.join(cmd)}[/green][/bold]")
    console.print()
    
    try:
        process = subprocess.Popen(cmd)
        process.wait()
        
        if process.returncode == 0:
            console.print()
            console.print("[bold green]Command completed successfully.[/bold green]")
        else:
            console.print()
            console.print(f"[bold red]Command failed with exit code {process.returncode}[/bold red]")
    except Exception as e:
        console.print()
        console.print(f"[bold red]Error: {e}[/bold red]")
    
    console.print()
    input("Press Enter to continue...")

def display_docs_menu():
    """Display the docs submenu."""
    clear_screen()
    display_title()
    
    console.print("[bold]Documentation Commands:[/bold]")
    console.print()
    
    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Command", style="green")
    table.add_column("Description", style="yellow")
    
    commands = [
        ("setup", "Configurar MkDocs interativamente"),
        ("serve", "Iniciar servidor de desenvolvimento do MkDocs"),
        ("build", "Construir documentação para produção"),
    ]
    
    for i, (cmd_name, help_text) in enumerate(commands, 1):
        table.add_row(str(i), cmd_name, help_text)
    
    console.print(table)
    console.print()
    console.print("[bold]Select a documentation command (or 'b' to go back, 'q' to quit):[/bold]")
    
    return commands

def run_tui() -> None:
    """Run the Terminal UI application."""
    try:
        while True:
            # Display categories and get valid category IDs
            valid_categories = display_categories()
            
            # Get category selection
            choice = Prompt.ask("> ", choices=["q"] + [str(i) for i in range(1, len(valid_categories) + 1)])
            
            if choice.lower() == 'q':
                break
            
            # Convert choice to category ID
            category_index = int(choice) - 1
            if category_index < 0 or category_index >= len(valid_categories):
                console.print("[bold red]Invalid selection.[/bold red]")
                continue
            
            category_id = valid_categories[category_index]
            
            while True:
                # Display commands for selected category
                commands = display_commands(category_id)
                if not commands:
                    input("Press Enter to continue...")
                    break
                
                # Get command selection
                cmd_choices = ["b", "q"] + [str(i) for i in range(1, len(commands) + 1)]
                cmd_choice = Prompt.ask("> ", choices=cmd_choices)
                
                if cmd_choice.lower() == 'b':
                    break
                if cmd_choice.lower() == 'q':
                    return
                
                # Convert choice to command name
                cmd_index = int(cmd_choice) - 1
                cmd_names = list(commands.keys())
                if cmd_index < 0 or cmd_index >= len(cmd_names):
                    console.print("[bold red]Invalid selection.[/bold red]")
                    continue
                
                cmd_name = cmd_names[cmd_index]
                
                # GitHub menu requires special handling
                if cmd_name == "github" and category_id == "github":
                    while True:
                        display_command_options(category_id, cmd_name)
                        option = Prompt.ask("> ", choices=["1", "2", "b", "q"])
                        
                        if option == "1":
                            run_command(cmd_name, show_help=True)
                            break
                        if option == "2":
                            # GitHub interactive submenu
                            while True:
                                github_commands = display_github_menu()
                                gh_choice = Prompt.ask("> ", choices=["b", "q"] + [str(i) for i in range(1, len(github_commands) + 1)])
                                
                                if gh_choice.lower() == 'b':
                                    break
                                if gh_choice.lower() == 'q':
                                    return
                                
                                gh_index = int(gh_choice) - 1
                                if gh_index < 0 or gh_index >= len(github_commands):
                                    console.print("[bold red]Invalid selection.[/bold red]")
                                    continue
                                
                                gh_subcmd = github_commands[gh_index][0]
                                run_github_command(gh_subcmd)
                            break
                        if option.lower() == 'b':
                            break
                        if option.lower() == 'q':
                            return
                elif cmd_name == "docs" and category_id == "docs":
                    while True:
                        display_command_options(category_id, cmd_name)
                        option = Prompt.ask("> ", choices=["1", "2", "b", "q"])
                        
                        if option == "1":
                            run_command(cmd_name, show_help=True)
                            break
                        if option == "2":
                            # Docs interactive submenu
                            while True:
                                docs_commands = display_docs_menu()
                                docs_choice = Prompt.ask("> ", choices=["b", "q"] + [str(i) for i in range(1, len(docs_commands) + 1)])
                                
                                if docs_choice.lower() == 'b':
                                    break
                                if docs_choice.lower() == 'q':
                                    return
                                
                                docs_index = int(docs_choice) - 1
                                if docs_index < 0 or docs_index >= len(docs_commands):
                                    console.print("[bold red]Invalid selection.[/bold red]")
                                    continue
                                
                                docs_subcmd = docs_commands[docs_index][0]
                                run_docs_command(docs_subcmd)
                            break
                        if option.lower() == 'b':
                            break
                        if option.lower() == 'q':
                            return
                else:
                    while True:
                        # Display command options
                        display_command_options(category_id, cmd_name)
                        
                        # Get option selection
                        option = Prompt.ask("> ", choices=["1", "2", "b", "q"])
                        
                        if option == "1":
                            run_command(cmd_name, show_help=False)
                            break
                        if option == "2":
                            run_command(cmd_name, show_help=True)
                            break
                        if option.lower() == 'b':
                            break
                        if option.lower() == 'q':
                            return
    
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Menu interrupted. Exiting...[/bold yellow]")
    finally:
        clear_screen()
        console.print("[bold green]Thanks for using Fast-Craftsmanship CLI![/bold green]")


if __name__ == "__main__":
    run_tui()