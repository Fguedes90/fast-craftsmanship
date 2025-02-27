"""Configuration module with functional approach."""

import os

from dataclasses import dataclass

from expression import Error, Ok, Result


@dataclass
class ScrapeConfig:
    root_url: str
    allowed_paths: list[str]
    max_concurrent: int
    output_dir: str
    max_depth: int = 3
    content_selector: str | None = None
    timeout: float = 30.0
    max_retries: int = 3
    browser_instances: int = 3


def validate_config(config: ScrapeConfig) -> Result[ScrapeConfig, Exception]:
    """Validate scraper configuration using ROP."""
    try:
        if not config.root_url:
            return Error(ValueError("root_url cannot be empty"))

        if not config.allowed_paths:
            return Error(ValueError("allowed_paths cannot be empty"))

        if config.max_concurrent < 1:
            return Error(ValueError("max_concurrent must be at least 1"))

        if config.max_depth < 1:
            return Error(ValueError("max_depth must be at least 1"))

        if config.timeout <= 0:
            return Error(ValueError("timeout must be positive"))

        if config.max_retries < 0:
            return Error(ValueError("max_retries cannot be negative"))

        if config.browser_instances < 1:
            return Error(ValueError("browser_instances must be at least 1"))

        return Ok(config)
    except Exception as e:
        return Error(e)


def ensure_output_directory(config: ScrapeConfig) -> Result[ScrapeConfig, Exception]:
    """Ensure output directory exists using ROP."""
    try:
        os.makedirs(config.output_dir, exist_ok=True)
        return Ok(config)
    except Exception as e:
        return Error(e)


def create_config(
    root_url: str,
    allowed_paths: list[str],
    output_dir: str,
    max_concurrent: int = 5,
    max_depth: int = 3,
    content_selector: str | None = None,
    timeout: float = 30.0,
    max_retries: int = 3,
    browser_instances: int = 1,
) -> Result[ScrapeConfig, Exception]:
    """Create and validate scraper configuration using ROP."""
    try:
        config = ScrapeConfig(
            root_url=root_url,
            allowed_paths=allowed_paths,
            output_dir=output_dir,
            max_concurrent=max_concurrent,
            max_depth=max_depth,
            content_selector=content_selector,
            timeout=timeout,
            max_retries=max_retries,
            browser_instances=browser_instances,
        )

        return validate_config(config).bind(ensure_output_directory)
    except Exception as e:
        return Error(e)
