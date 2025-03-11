"""CLI interface for the compact code command."""

import argparse

from fcship.commands.compact.config import (
    COMPACT_NOTATION_FILE,
    DEFAULT_OUTPUT_FILE,
    IGNORE_DIRS,
    IGNORE_FILES,
)
from fcship.commands.compact.generator import generate_compact_code_with_config
from fcship.commands.compact.token_counter import analyze_file, print_token_analysis


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Generate compact code representation of Python files"
    )
    
    parser.add_argument(
        "-o", "--output",
        default=DEFAULT_OUTPUT_FILE,
        help="Output file path (default: %(default)s)"
    )
    
    parser.add_argument(
        "-d", "--directory",
        default=".",
        help="Project root directory (default: current directory)"
    )
    
    parser.add_argument(
        "-g", "--guide",
        default=COMPACT_NOTATION_FILE,
        help="Path to compact notation guide file (default: %(default)s)"
    )
    
    parser.add_argument(
        "-t", "--target",
        help="Target file or directory to process (default: entire project)"
    )
    
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print output to stdout instead of file"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--ignore-dirs",
        help="Comma-separated list of directories to ignore"
    )
    
    parser.add_argument(
        "--ignore-files",
        help="Comma-separated list of file patterns to ignore"
    )
    
    parser.add_argument(
        "--count-tokens",
        action="store_true",
        help="Count tokens in the output file"
    )
    
    parser.add_argument(
        "--token-model",
        default="gpt-4o",
        choices=["gpt-4o", "gpt-3.5-turbo", "claude-3-opus"],
        help="Model to use for token counting (default: %(default)s)"
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point for the compact code command."""
    args = parse_arguments()
    
    # Process ignore patterns
    ignore_dirs = IGNORE_DIRS.copy()
    ignore_files = IGNORE_FILES.copy()
    
    if args.ignore_dirs:
        ignore_dirs.extend(args.ignore_dirs.split(","))
    if args.ignore_files:
        ignore_files.extend(args.ignore_files.split(","))
    
    # Generate compact code
    output_file = generate_compact_code_with_config(
        output_file=args.output,
        project_root=args.directory,
        notation_file=args.guide,
        ignore_dirs=ignore_dirs,
        ignore_files=ignore_files,
        target=args.target,
        stdout=args.stdout,
        verbose=args.verbose
    )
    
    # Count tokens if requested and output file was generated
    if args.count_tokens and output_file and not args.stdout:
        stats = analyze_file(output_file, args.token_model)
        print_token_analysis(stats)


if __name__ == "__main__":
    main() 