# Fast-Craftsmanship Terminal UI

This module provides an interactive terminal user interface for the Fast-Craftsmanship CLI tool, making it easier to discover, navigate and use the various commands available in the tool.

## Features

- Category-based command navigation
- Interactive menu system with rich formatting
- Command help and execution options
- Responsive and user-friendly interface

## Usage

The TUI can be launched in two ways:

1. Using the dedicated menu command:
   ```
   craftsmanship menu
   ```

2. Using the --tui flag with the main command:
   ```
   craftsmanship --tui
   ```

## Navigation

The TUI provides a multi-level navigation structure:

1. **Category Selection**: Choose from available command categories (Scaffolding, VCS, Quality, etc.)
2. **Command Selection**: Select a specific command within the chosen category
3. **Command Options**: Run the command or view its help information

## Implementation

The TUI is implemented using the Rich library for Python, which provides:
- Formatted text output with colors and styles
- Tables and panels for organized display
- Interactive prompts for user input

## File Structure

- `__init__.py` - Package initialization
- `menu.py` - Main TUI implementation with menu hierarchy
- `README.md` - This documentation file

## Development

To extend or modify the TUI:

1. The `display_categories()` function shows available command categories
2. The `display_commands()` function shows commands within a category
3. The `display_command_options()` function shows options for a specific command
4. The `run_command()` function executes the selected command

## Requirements

- Rich library (`pip install rich`)
- Python 3.6+