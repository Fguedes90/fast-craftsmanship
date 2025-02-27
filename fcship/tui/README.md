# Fast-Craftsmanship Terminal UI

This module provides an interactive terminal user interface for the Fast-Craftsmanship CLI tool, making it easier to discover, navigate and use the various commands available in the tool.

## Features

- Category-based command navigation
- Interactive menu system with rich formatting
- Command help and execution options
- Responsive and user-friendly interface
- Keyboard shortcuts for quick navigation
- Error handling for command execution

## Usage

The TUI can be launched in two ways:

1. Using the dedicated menu command:
   ```
   python -m fcship.cli menu
   ```

2. From the Makefile:
   ```
   make tui
   ```

## Navigation

The TUI provides a three-level navigation structure:

1. **Category Selection**: Choose from available command categories (scaffold, vcs, quality, db)
2. **Command Selection**: Select a specific command within the chosen category
3. **Command Options**: Run the command or view its help information

### Keyboard Navigation

- `1-N`: Select a numbered option
- `b`: Go back to the previous menu
- `q`: Quit the TUI
- `Enter`: Confirm selection

## Implementation

The TUI is implemented using the Rich library for Python, which provides:
- Formatted text output with colors and styles
- Tables and panels for organized display
- Interactive prompts for user input
- Command execution with subprocess

## Core Components

- `display_categories()`: Shows available command categories with descriptions
- `display_commands(category_id)`: Shows commands available in the selected category
- `display_command_options(category_id, command_name)`: Shows options for a specific command
- `run_command(command_name, show_help)`: Executes the selected command
- `run_tui()`: Main entry point for the TUI

## Command Execution

Commands are executed using Python's subprocess module to maintain interactive capabilities:

```python
def run_command(command_name: str, show_help: bool = False):
    """Run a command or show its help."""
    if show_help:
        cmd = ["python", "-m", "fcship.cli", command_name, "--help"]
    else:
        cmd = ["python", "-m", "fcship.cli", command_name]
    
    # Use subprocess.Popen to maintain interactive capabilities
    process = subprocess.Popen(cmd)
    process.wait()
```

## File Structure

- `__init__.py` - Package initialization
- `menu.py` - Main TUI implementation with menu hierarchy and navigation
- `display.py` - Display utilities for consistent UI rendering
- `errors.py` - Error types and handling for UI operations
- `README.md` - This documentation file

## Future Improvements

1. **Parameter Input**: Add interactive parameter input for commands
2. **Command History**: Implement command history tracking
3. **Theming Support**: Allow users to customize the TUI appearance
4. **Auto-complete**: Add tab completion for command names and parameters
5. **Filter Options**: Allow filtering command lists by keyword

## Requirements

- Rich library (included in project dependencies)
- Python 3.10+