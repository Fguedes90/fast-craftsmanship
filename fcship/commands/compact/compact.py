"""Entry point for the compact command."""

import sys

from collections.abc import Sequence

from .cli import main


def compact(args: Sequence[str] | None = None) -> int:
    """Execute the compact command.
    
    Args:
        args: Command line arguments (optional)
        
    Returns:
        Exit code
    """
    try:
        main()
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1 