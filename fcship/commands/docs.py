"""Command for running MD scraper with functional approach."""

import asyncio

import typer

from expression import Error, Ok
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from fcship.commands.docs_downloader.exceptions import ProcessingException
from fcship.commands.docs_downloader.orchestrator import run_scraper
from fcship.utils import error_message, handle_command_errors

console = Console()


@handle_command_errors
async def scrape_docs(
    root_url: str,
    allowed_paths: list[str],
    output_dir: str,
    max_concurrent: int | None = 5,
    max_depth: int | None = 3,
    content_selector: str | None = None,
    timeout: float | None = 30.0,
) -> None:
    """Run the scraper with provided configuration."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Running documentation scraper...", total=None)

        result = await run_scraper(
            root_url=root_url,
            allowed_paths=allowed_paths,
            output_dir=output_dir,
            max_concurrent=max_concurrent,
            max_depth=max_depth,
            content_selector=content_selector,
            timeout=timeout,
        )

        progress.update(task, completed=True)

        match result:
            case Ok(metrics):
                console.print("\n[green]Documentation scraping completed successfully[/green]")
                console.print("\n[bold]Scraping Metrics:[/bold]")
                for key, value in metrics.items():
                    if isinstance(value, float):
                        console.print(f"  {key}: {value:.2f}")
                    else:
                        console.print(f"  {key}: {value}")
                console.print(f"\nDocumentation scraped to: [blue]{output_dir}[/blue]")
            case Error(e):
                if isinstance(e, ProcessingException):
                    error_message(
                        "Failed to scrape documentation",
                        str(e),
                        e.original_error if hasattr(e, "original_error") else None,
                    )
                else:
                    error_message("Failed to scrape documentation", str(e))
                raise typer.Exit(1)


def docs(
    operation: str = typer.Argument(..., help="Operation to perform [scrape]"),
    root_url: str = typer.Option(..., "--url", "-u", help="Root URL to start scraping from"),
    allowed_paths: list[str] = typer.Option(
        ..., "--paths", "-p", help="List of allowed paths to scrape"
    ),
    output_dir: str = typer.Option(
        "./docs", "--output", "-o", help="Output directory for scraped docs"
    ),
    max_concurrent: int | None = typer.Option(
        5, "--concurrent", "-c", help="Maximum concurrent workers"
    ),
    max_depth: int | None = typer.Option(3, "--depth", "-d", help="Maximum depth to scrape"),
    content_selector: str | None = typer.Option(
        None, "--selector", "-s", help="CSS selector for content extraction"
    ),
    timeout: float | None = typer.Option(
        30.0, "--timeout", "-t", help="Timeout for page operations in seconds"
    ),
) -> None:
    """Scrape documentation from websites using Railway Oriented Programming."""
    if operation != "scrape":
        error_message(f"Unknown operation: {operation}", "Available operations: scrape")
        raise typer.Exit(1)

    try:
        asyncio.run(
            scrape_docs(
                root_url=root_url,
                allowed_paths=allowed_paths,
                output_dir=output_dir,
                max_concurrent=max_concurrent,
                max_depth=max_depth,
                content_selector=content_selector,
                timeout=timeout,
            )
        )
    except Exception as e:
        error_message("Failed to run scraper", str(e))
        raise typer.Exit(1)
