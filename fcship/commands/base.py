from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

class Command:
    def __init__(self, name: str, help: str):
        self.name = name
        self.help = help
        
    def execute(self, *args, **kwargs):
        raise NotImplementedError("Command must implement execute method")
    
    def display_info(self):
        console.print(Panel(f"[bold green]{self.name}[/]\n{self.help}")) 