import os
import importlib
import inspect
from pathlib import Path
from .commands.base import Command

def load_commands() -> dict[str, Command]:
    commands = {}
    commands_dir = Path(__file__).parent / "commands"
    
    for file in os.listdir(commands_dir):
        if file.endswith('.py') and not file.startswith('__'):
            module_name = file[:-3]
            module = importlib.import_module(f'ai_dev_toolkit.commands.{module_name}')
            
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) 
                    and issubclass(obj, Command) 
                    and obj != Command):
                    command = obj()
                    commands[command.name] = command
    
    return commands

COMMANDS = load_commands()