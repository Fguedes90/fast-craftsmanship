"""Entry point for the compact command."""

import sys
import os
from typing import Literal, Optional, List, Any

from expression import Error, Ok, Result, pipe

from .config import (
    COMPACT_NOTATION_FILE,
    DEFAULT_OUTPUT_FILE,
    IGNORE_DIRS,
    IGNORE_FILES,
)
from .generator import generate_compact_code_with_config
from .token_counter import analyze_file, print_token_analysis


def compact_command(*args, **kwargs) -> Result[str, str]:
    """Generate compact code representation of Python files.
    
    This command creates a compact representation of Python code in markdown format,
    which is useful for providing a high-level overview of a codebase or preparing
    it for analysis by LLMs.
    
    Command-line options:
        --output, -o: Path to output file (default: compact_code.md)
        --directory, -d: Project root directory (default: current directory)
        --guide, -g: Path to compact notation guide file
        --ignore-dirs: Comma-separated list of directories to ignore
        --ignore-files: Comma-separated list of file patterns to ignore
        --target, -t: Target file or directory to process
        --stdout: Print output to stdout instead of file
        --verbose, -v: Enable verbose output
        --count-tokens: Count tokens in the output file
        --token-model: Model to use for token counting
    
    Returns:
        Result containing the output message or error
    """
    # Safeguard for direct CLI invocation through the Typer wrapper
    if len(sys.argv) > 2 and sys.argv[1] == "compact":
        # When called from the command line with arguments
        from .cli import main as compact_main
        
        # Save current argv and replace with our CLI arguments
        original_argv = sys.argv.copy()
        
        try:
            # Reformat the sys.argv to match what argparse expects
            # Remove "fcship compact" and keep the rest
            sys.argv = [sys.argv[0]] + sys.argv[2:]  
            
            # Run the command's main function which will use argparse
            compact_main()
            return Ok("Compact code generation completed")
        except Exception as e:
            return Error(f"Error in compact command: {e}")
        finally:
            # Restore original sys.argv
            sys.argv = original_argv
    
    # For programmatic use when arguments are passed directly
    elif args and args[0]:
        try:
            # Handle arguments passed to this function directly
            from .cli import main as compact_main
            
            # Save current argv and replace with our arguments
            original_argv = sys.argv.copy()
            
            try:
                # Set sys.argv for argparse to process
                sys.argv = [sys.argv[0]] + (list(args[0]) if isinstance(args[0], (list, tuple)) else [str(args[0])])
                
                # Execute the compact command
                compact_main()
                return Ok("Compact code generation completed")
            finally:
                # Restore original sys.argv
                sys.argv = original_argv
        except Exception as e:
            return Error(f"Error in compact command: {e}")
    
    # Default case with no arguments, just run with defaults
    else:
        try:
            from .cli import main as compact_main
            compact_main()
            return Ok("Compact code generation completed")
        except Exception as e:
            return Error(f"Error in compact command: {e}") 