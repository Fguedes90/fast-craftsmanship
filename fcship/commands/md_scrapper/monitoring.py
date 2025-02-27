"""Monitoring and logging module with functional approach."""

import logging

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from expression import Ok, Result

from .exceptions import ProcessingException, capture_exception
from .types import Url


@dataclass
class ScraperMetrics:
    """Metrics for scraper operations."""

    start_time: datetime
    end_time: datetime | None = None
    total_pages: int = 0
    successful_pages: int = 0
    failed_pages: int = 0
    total_links: int = 0
    network_errors: int = 0
    processing_errors: int = 0
    validation_errors: int = 0

    @property
    def duration(self) -> float | None:
        """Get operation duration in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "duration_seconds": self.duration,
            "total_pages": self.total_pages,
            "successful_pages": self.successful_pages,
            "failed_pages": self.failed_pages,
            "total_links": self.total_links,
            "network_errors": self.network_errors,
            "processing_errors": self.processing_errors,
            "validation_errors": self.validation_errors,
            "success_rate": (self.successful_pages / self.total_pages * 100)
            if self.total_pages > 0
            else 0,
        }


class ScraperMonitor:
    """Monitor for scraper operations."""

    def __init__(self):
        self.metrics = ScraperMetrics(start_time=datetime.now())
        self._configure_logging()

    def _configure_logging(self) -> None:
        """Configure logging with proper format."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
        )

    def record_success(self, url: Url) -> Result[None, ProcessingException]:
        """Record successful page processing."""
        try:
            self.metrics.successful_pages += 1
            self.metrics.total_pages += 1
            logging.info(f"Successfully processed {url}")
            return Ok(None)
        except Exception as e:
            return capture_exception(e, ProcessingException, f"Failed to record success for {url}")

    def record_failure(self, url: Url, error: Exception) -> Result[None, ProcessingException]:
        """Record page processing failure."""
        try:
            self.metrics.failed_pages += 1
            self.metrics.total_pages += 1

            if isinstance(error, ProcessingException):
                self.metrics.processing_errors += 1
            elif "network" in str(error).lower():
                self.metrics.network_errors += 1
            else:
                self.metrics.validation_errors += 1

            logging.error(f"Failed to process {url}: {error!s}")
            return Ok(None)
        except Exception as e:
            return capture_exception(e, ProcessingException, f"Failed to record failure for {url}")

    def record_link(self, url: Url) -> Result[None, ProcessingException]:
        """Record discovered link."""
        try:
            self.metrics.total_links += 1
            logging.debug(f"Discovered link: {url}")
            return Ok(None)
        except Exception as e:
            return capture_exception(e, ProcessingException, f"Failed to record link {url}")

    def finish(self) -> Result[dict[str, Any], ProcessingException]:
        """Finish monitoring and return metrics."""
        try:
            self.metrics.end_time = datetime.now()
            metrics_dict = self.metrics.to_dict()

            logging.info("Scraping completed. Final metrics:")
            for key, value in metrics_dict.items():
                logging.info(f"{key}: {value}")

            return Ok(metrics_dict)
        except Exception as e:
            return capture_exception(e, ProcessingException, "Failed to finish monitoring")
