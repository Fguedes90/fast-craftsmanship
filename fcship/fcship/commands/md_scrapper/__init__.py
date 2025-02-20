"""MD Scrapper module with functional approach."""
from typing import Dict, Any, List
from pathlib import Path
from expression import Result

from .orchestrator import run_scraper
from .config import create_config, ScrapeConfig
from .exceptions import ProcessingException
from .types import Url, Depth

__all__ = [
    'run_scraper',
    'create_config',
    'ScrapeConfig',
    'ProcessingException',
    'Result',
    'Url',
    'Depth'
]

# Type aliases for better type hints
ScraperResult = Result[Dict[str, Any], ProcessingException]

async def scrape(
    root_url: str,
    allowed_paths: List[str],
    output_dir: str = "./docs",
    max_concurrent: int = 5,
    max_depth: int = 3,
    content_selector: str = None,
    timeout: float = 30.0,
    log_file: Path = Path('scraper.log')
) -> ScraperResult:
    """
    Scrape documentation from a website using Railway Oriented Programming.
    
    Args:
        root_url: The root URL to start scraping from
        allowed_paths: List of URL paths that are allowed to be scraped
        output_dir: Directory to save scraped content
        max_concurrent: Maximum number of concurrent workers
        max_depth: Maximum depth to traverse from root URL
        content_selector: CSS selector for content extraction
        timeout: Timeout for page operations in seconds
        log_file: Path to log file
        
    Returns:
        Result containing either metrics dictionary or error
    """
    return await run_scraper(
        root_url=root_url,
        allowed_paths=allowed_paths,
        output_dir=output_dir,
        max_concurrent=max_concurrent,
        max_depth=max_depth,
        content_selector=content_selector,
        timeout=timeout,
        log_file=log_file
    )