"""Orchestrator module for scraper operations."""

from pathlib import Path
from typing import Any

from expression import Error, Ok, Result

from .browser_pool import with_browser_pool
from .config import create_config
from .context import ScraperContext
from .exceptions import ProcessingException, capture_exception
from .logger import FunctionalLogger, LogConfig
from .pipeline import create_scraping_pipeline
from .validation import validate_scraper_config


async def run_scraper(
    root_url: str,
    allowed_paths: list[str],
    output_dir: str,
    max_concurrent: int = 5,
    max_depth: int = 3,
    content_selector: str = None,
    timeout: float = 30.0,
    log_file: Path = Path("scraper.log"),
    browser_instances: int = 2,
) -> Result[dict[str, Any], ProcessingException]:
    """Run the scraper with functional composition."""
    # Initialize logger first for early error catching
    log_config = LogConfig(log_file=log_file, console_output=True)
    logger = FunctionalLogger(log_config)

    try:
        await logger.info("Starting scraper orchestration")

        # Validate configuration
        await logger.info("Validating configuration")
        config_validation = await validate_scraper_config(
            root_url, allowed_paths, max_concurrent, max_depth, timeout
        )
        if isinstance(config_validation, Error):
            await logger.error("Configuration validation failed", config_validation.error)
            return config_validation

        # Create configuration
        await logger.info("Creating scraper configuration")
        config_result = create_config(
            root_url=root_url,
            allowed_paths=allowed_paths,
            output_dir=output_dir,
            max_concurrent=max_concurrent,
            max_depth=max_depth,
            content_selector=content_selector,
            timeout=timeout,
        )
        if isinstance(config_result, Error):
            await logger.error("Configuration creation failed", config_result.error)
            return config_result

        # Initialize browser pool
        async for pool_result in with_browser_pool(browser_instances, logger):
            if isinstance(pool_result, Error):
                await logger.error("Browser pool creation failed", pool_result.error)
                return pool_result

            pool = pool_result.value
            context = pool.get_next_context()

            try:
                # Create scraper context
                await logger.info("Creating scraper context")
                context_result = await ScraperContext.create(config_result.value, context)
                if isinstance(context_result, Error):
                    await logger.error("Context creation failed", context_result.error)
                    return context_result

                # Create and run pipeline
                await logger.info("Starting scraping pipeline")
                pipeline = create_scraping_pipeline()
                result = await pipeline(context_result.value)

                if isinstance(result, Error):
                    await logger.error("Pipeline execution failed", result.error)
                    return result

                # Return metrics from monitor
                await logger.info("Scraping completed successfully")
                metrics = context_result.value.monitor.metrics.to_dict()
                await logger.log_metrics(metrics)
                return Ok(metrics)

            except Exception as e:
                error_msg = "Unexpected error during scraping"
                await logger.error(error_msg, e)
                return capture_exception(e, ProcessingException, error_msg)

    except Exception as e:
        error_msg = "Failed to run scraper orchestration"
        await logger.error(error_msg, e)
        return capture_exception(e, ProcessingException, error_msg)
