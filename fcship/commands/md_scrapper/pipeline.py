"""Pipeline module for composing scraper operations."""

import asyncio

from collections.abc import Awaitable, Callable
from typing import TypeVar

from expression import Error, Ok, Result

from .context import ScraperContext
from .exceptions import ProcessingException, capture_exception
from .result_utils import catch_errors_async
from .worker import worker

T = TypeVar("T")
Pipeline = Callable[[ScraperContext], Awaitable[Result[T, ProcessingException]]]


async def compose_pipeline(*operations: Pipeline) -> Pipeline:
    """Compose multiple pipeline operations."""

    async def composed(context: ScraperContext) -> Result[None, ProcessingException]:
        for operation in operations:
            result = await operation(context)
            if isinstance(result, Error):
                await context.logger.error(f"Pipeline operation failed: {result.error}")
                return result
            await context.logger.debug("Pipeline operation completed successfully")
        return Ok(None)

    return composed


@catch_errors_async(ProcessingException, "Validation failed")
async def validate_operation(context: ScraperContext) -> Result[None, ProcessingException]:
    """Validate scraper configuration."""
    await context.logger.info("Validating scraper configuration")
    if not context.config:
        return Error(ProcessingException("Missing configuration"))
    return Ok(None)


@catch_errors_async(ProcessingException, "Initialization failed")
async def initialize_operation(context: ScraperContext) -> Result[None, ProcessingException]:
    """Initialize scraper resources."""
    await context.logger.info("Initializing scraper")
    return await context.initialize()


@catch_errors_async(ProcessingException, "Queue processing failed")
async def process_queue_operation(context: ScraperContext) -> Result[None, ProcessingException]:
    """Process URL queue."""
    await context.logger.info("Starting URL queue processing")
    try:
        workers = []
        for i in range(context.config.max_concurrent):
            await context.logger.debug(f"Starting worker {i + 1}")
            worker_task = asyncio.create_task(worker(context))
            workers.append(worker_task)

        await context.url_queue.join()
        await context.logger.info("URL queue processing completed")

        for i, worker_task in enumerate(workers):
            worker_task.cancel()
            try:
                await worker_task
                await context.logger.debug(f"Worker {i + 1} stopped cleanly")
            except asyncio.CancelledError:
                await context.logger.debug(f"Worker {i + 1} cancelled")
            except Exception as e:
                await context.logger.error(f"Worker {i + 1} error during shutdown: {e!s}")

        return Ok(None)
    except Exception as e:
        return capture_exception(e, ProcessingException, "Queue processing failed")


@catch_errors_async(ProcessingException, "Cleanup failed")
async def cleanup_operation(context: ScraperContext) -> Result[None, ProcessingException]:
    """Clean up scraper resources."""
    await context.logger.info("Cleaning up scraper resources")
    return await context.cleanup()


def create_scraping_pipeline() -> Pipeline:
    """Create the main scraping pipeline."""
    return compose_pipeline(
        validate_operation, initialize_operation, process_queue_operation, cleanup_operation
    )
