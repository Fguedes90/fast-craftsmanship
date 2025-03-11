"""Entry point for the compact command."""

import sys
from typing import Optional, List, Literal
from pathlib import Path
from expression import Result, Ok, Error

from .cli import parse_arguments
from .generator import generate_compact_code_with_config
from .token_counter import analyze_file, print_token_analysis
from .config import (
    COMPACT_NOTATION_FILE,
    DEFAULT_OUTPUT_FILE,
    IGNORE_DIRS,
    IGNORE_FILES,
)

def compact(
    output_file: Optional[str] = None,
    project_root: str = ".",
    notation_file: Optional[str] = None,
    ignore_dirs: Optional[List[str]] = None,
    ignore_files: Optional[List[str]] = None,
    target: Optional[str] = None, 
    stdout: bool = False,
    verbose: bool = False,
    count_tokens: bool = False,
    token_model: Literal["gpt-4o", "gpt-3.5-turbo", "claude-3-opus"] = "gpt-4o",
) -> Result[str, str]:
    """Generate compact code representation of Python files.
    
    Args:
        output_file: Path to output file (default: compact_code.md)
        project_root: Project root directory (default: current directory)
        notation_file: Path to compact notation guide file
        ignore_dirs: List of directory patterns to ignore
        ignore_files: List of file patterns to ignore
        target: Target file or directory to process
        stdout: Print output to stdout instead of file
        verbose: Enable verbose output
        count_tokens: Count tokens in the output file
        token_model: Model to use for token counting
        
    Returns:
        Result containing path to the output file or error message
    """
    try:
        # Use provided values or defaults from config
        final_output_file = output_file or DEFAULT_OUTPUT_FILE
        final_notation_file = notation_file or COMPACT_NOTATION_FILE
        
        # Process ignore patterns
        final_ignore_dirs = IGNORE_DIRS.copy()
        final_ignore_files = IGNORE_FILES.copy()
        
        if ignore_dirs:
            final_ignore_dirs.extend(ignore_dirs)
        if ignore_files:
            final_ignore_files.extend(ignore_files)
            
        # Generate compact code
        result_file = generate_compact_code_with_config(
            output_file=final_output_file,
            project_root=project_root,
            notation_file=final_notation_file,
            ignore_dirs=final_ignore_dirs,
            ignore_files=final_ignore_files,
            target=target,
            stdout=stdout,
            verbose=verbose
        )
        
        # Count tokens if requested and output file was generated
        if count_tokens and result_file and not stdout:
            stats = analyze_file(result_file, token_model)
            print_token_analysis(stats)
            
        if stdout:
            return Ok("Compact code generated and printed to stdout")
        else:
            return Ok(f"Compact code generated at {result_file}")
            
    except Exception as e:
        return Error(f"Error generating compact code: {e}")

def compact_command() -> Result[str, str]:
    """Command-line entry point for the compact command.
    
    Returns:
        Result containing the output message or error
    """
    try:
        args = parse_arguments()
        
        # Process ignore patterns
        ignore_dirs = IGNORE_DIRS.copy()
        ignore_files = IGNORE_FILES.copy()
        
        if args.ignore_dirs:
            ignore_dirs.extend(args.ignore_dirs.split(","))
        if args.ignore_files:
            ignore_files.extend(args.ignore_files.split(","))
        
        return compact(
            output_file=args.output,
            project_root=args.directory,
            notation_file=args.guide,
            ignore_dirs=ignore_dirs,
            ignore_files=ignore_files,
            target=args.target,
            stdout=args.stdout,
            verbose=args.verbose,
            count_tokens=args.count_tokens,
            token_model=args.token_model
        )
            
    except Exception as e:
        return Error(f"Error in compact command: {e}") 