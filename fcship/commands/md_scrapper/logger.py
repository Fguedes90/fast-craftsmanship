"""Logger module with functional approach."""

import logging
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from expression import Ok, Result

from .exceptions import ProcessingException, capture_exception
from .types import Url


@dataclass
class LogConfig:
    """Configuration for logging."""

    log_file: Path
    log_level: int = logging.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_output: bool = True


class FunctionalLogger:
    """Logger with functional approach."""

    def __init__(self, config: LogConfig):
        self.config = config
        self._setup_logger()
        self.logger = logging.getLogger("scraper")

    def _setup_logger(self) -> None:
        """Setup logger with file and console handlers."""
        logger = logging.getLogger("scraper")
        logger.setLevel(self.config.log_level)

        # File handler
        file_handler = logging.FileHandler(self.config.log_file)
        file_handler.setFormatter(logging.Formatter(self.config.format))
        handlers = [file_handler]
        # Console handler if enabled
        if self.config.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(self.config.format))
            handlers.append(console_handler)

        # Remove existing handlers and add new ones
        logger.handlers.clear()
        for handler in handlers:
            logger.addHandler(handler)

    def info(self, message: str) -> Result[None, ProcessingException]:
        """Log info message."""
        try:
            self.logger.info(message)
            return Ok(None)
        except Exception as e:
            return capture_exception(e, ProcessingException, f"Failed to log info: {message}")

    def error(
        self, message: str, error: Exception | None = None
    ) -> Result[None, ProcessingException]:
        """Log error message."""
        try:
            if error:
                self.logger.error(f"{message}: {error!s}")
            else:
                self.logger.error(message)
            return Ok(None)
        except Exception as e:
            return capture_exception(e, ProcessingException, f"Failed to log error: {message}")

    def warning(self, message: str) -> Result[None, ProcessingException]:
        """Log warning message."""
        try:
            self.logger.warning(message)
            return Ok(None)
        except Exception as e:
            return capture_exception(e, ProcessingException, f"Failed to log warning: {message}")

    def debug(self, message: str) -> Result[None, ProcessingException]:
        """Log debug message."""
        try:
            self.logger.debug(message)
            return Ok(None)
        except Exception as e:
            return capture_exception(e, ProcessingException, f"Failed to log debug: {message}")

    async def log_url_processing(self, url: Url, depth: int) -> Result[None, ProcessingException]:
        """Log URL processing with context."""
        return self.info(f"Processing URL: {url} at depth {depth}")

    async def log_url_success(self, url: Url) -> Result[None, ProcessingException]:
        """Log successful URL processing."""
        return self.info(f"Successfully processed URL: {url}")

    async def log_url_failure(
        self, url: Url, error: Exception
    ) -> Result[None, ProcessingException]:
        """Log URL processing failure."""
        return self.error(f"Failed to process URL: {url}", error)

    async def log_metrics(self, metrics: dict[str, Any]) -> Result[None, ProcessingException]:
        """Log scraping metrics."""
        try:
            self.info("Scraping completed. Final metrics:")
            for key, value in metrics.items():
                if isinstance(value, float):
                    self.info(f"  {key}: {value:.2f}")
                else:
                    self.info(f"  {key}: {value}")
            return Ok(None)
        except Exception as e:
            return capture_exception(e, ProcessingException, "Failed to log metrics")
