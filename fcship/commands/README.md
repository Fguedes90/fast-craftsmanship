# Adding New Commands to AI Dev Toolkit

This guide explains how to create and add new commands to the AI Dev Toolkit.

## Quick Start

1. Create a new Python file in the `commands` directory
2. Create a class that inherits from `Command`
3. Your command will be automatically registered

## Example

```python
from .base import Command, console

class MyNewCommand(Command):
    def __init__(self):
        super().__init__(
            name="my-command",  # This will be the command name in CLI
            help="Description of what your command does"
        )
    
    def execute(self, *args, **kwargs):
        # Implement your command logic here
        console.print("[bold green]My command is running![/]")
```

## Command Structure

### Required Components

1. **Class Inheritance**: Your class must inherit from `Command`
2. **Constructor**: Must call `super().__init__()` with:
   - `name`: The command name used in CLI
   - `help`: A brief description of the command

3. **Execute Method**: Must implement `execute()` method that contains your command logic

### Optional Methods

- `display_info()`: Override to customize how your command info is displayed
- Add any helper methods your command needs

## Command Arguments

To add arguments to your command:

```python
class CommandWithArgs(Command):
    def __init__(self):
        super().__init__(
            name="greet",
            help="Greet someone by name"
        )
    
    def execute(self, name: str = "World"):
        console.print(f"[bold blue]Hello, {name}![/]")
```

## Best Practices

1. Keep commands focused on a single responsibility
2. Use descriptive names for your command
3. Provide clear help text
4. Handle errors gracefully
5. Use rich formatting for console output

## Automatic Registration

The command system will automatically:
- Discover your command
- Register it with the CLI
- Add it to help text
- Make it available for use

No manual registration needed!