"""Context module for managing scraper state."""

import asyncio

from dataclasses import dataclass
from pathlib import Path

from expression import Ok, Result
from playwright.async_api import BrowserContext

from .config import ScrapeConfig
from .exceptions import ProcessingException, capture_exception
from .logger import FunctionalLogger, LogConfig
from .monitoring import ScraperMonitor
from .progress import ProgressTracker
from .url_tracker import UrlTracker


@dataclass
class ScraperContext:
    """Context for scraper operations."""

    config: ScrapeConfig
    browser_context: BrowserContext
    url_queue: asyncio.Queue
    url_tracker: UrlTracker
    progress: ProgressTracker
    monitor: ScraperMonitor
    logger: FunctionalLogger
    file_lock: asyncio.Lock

    @classmethod
    async def create(
        cls, config: ScrapeConfig, browser_context: BrowserContext
    ) -> Result["ScraperContext", ProcessingException]:
        """Create a new scraper context."""
        try:
            log_config = LogConfig(log_file=Path("scraper.log"), console_output=True)

            return Ok(
                cls(
                    config=config,
                    browser_context=browser_context,
                    url_queue=asyncio.Queue(),
                    url_tracker=UrlTracker(),
                    progress=ProgressTracker(),
                    monitor=ScraperMonitor(),
                    logger=FunctionalLogger(log_config),
                    file_lock=asyncio.Lock(),
                )
            )
        except Exception as e:
            return capture_exception(e, ProcessingException, "Failed to create scraper context")

    async def initialize(self) -> Result[None, ProcessingException]:
        """Initialize the context."""
        try:
            await self.url_queue.put((self.config.root_url, 0))
            self.progress.start()
            await self.logger.info("Scraper context initialized")
            return Ok(None)
        except Exception as e:
            return capture_exception(e, ProcessingException, "Failed to initialize scraper context")

    async def cleanup(self) -> Result[None, ProcessingException]:
        """Clean up the context."""
        try:
            self.progress.close()
            metrics_result = await self.monitor.finish()
            if metrics_result.is_ok():
                await self.logger.log_metrics(metrics_result.value)
            return metrics_result
        except Exception as e:
            return capture_exception(e, ProcessingException, "Failed to clean up scraper context")
