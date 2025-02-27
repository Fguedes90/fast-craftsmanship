"""Worker module with functional approach."""

from typing import Any

from expression import Result

from fcship.utils.functional import catch_errors_async, ensure_async, pipe_async

from .content_manager import extract_content, save_content
from .context import ScraperContext
from .exceptions import NetworkException, ProcessingException
from .progress import increment_total
from .retry import retry_with_timeout
from .types import Depth, LinkResult, NetworkException, ProcessingError, Url, make_error
from .url_tracker import (
    is_url_processed,
    mark_url_failed,
    mark_url_processed,
    mark_url_visited,
    process_page_links,
)
from .url_utils import normalize_url, validate_url


@catch_errors_async(NetworkException, "Failed to access page")
async def access_page(page: Any, url: str, timeout: float) -> Result[bool, ProcessingException]:
    """Access a page with retry and timeout."""
    response = await page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
    return Ok(response is not None and response.ok)


async def process_page(url: Url, depth: Depth, page: Any, context: ScraperContext) -> LinkResult:
    """Process page using ROP with retry capabilities."""
    await context.logger.log_url_processing(url, depth)

    try:
        # Normalize and validate URL
        async def validate_normalized(normalized):
            return (
                Ok(None)
                if await is_url_processed(normalized, context.url_tracker)
                else Ok(normalized)
            )

        url_validation = await pipe_async(
            lambda u: ensure_async(normalize_url(u)), validate_normalized
        )(url)

        if not isinstance(url_validation, Ok) or not url_validation.value:
            return Ok([])

        base_url = url_validation.value
        await mark_url_visited(base_url, context.url_tracker)

        # Validate URL against config
        valid_url = validate_url(base_url, context.config.root_url, context.config.allowed_paths)
        if not isinstance(valid_url, Ok) or not valid_url.value:
            await context.logger.info(f"Skipping invalid URL: {base_url}")
            return Ok([])

        # Access page with retry
        access_result = await retry_with_timeout(
            access_page,
            context.config.max_retries,
            context.config.timeout,
            page,
            base_url,
            context.config.timeout,
        )

        if isinstance(access_result, Error) or not access_result.value:
            await context.logger.warning(f"Failed to access URL: {base_url}")
            return Ok([])

        # Extract and save content with retry
        content_result = await retry_with_timeout(
            extract_content,
            context.config.max_retries,
            context.config.timeout,
            page,
            url,
            context.config.content_selector,
        )

        match content_result:
            case Ok((content, filename)):
                save_result = await save_content(
                    content, filename, context.config.output_dir, context.file_lock
                )
                if isinstance(save_result, Error):
                    await context.logger.error(f"Failed to save content for URL: {url}")
                    return save_result
            case Error(e):
                await context.logger.error(f"Failed to extract content from URL: {url}")
                return Error(e)

        await mark_url_processed(base_url, context.url_tracker)
        await context.logger.log_url_success(url)

        # Check depth and process links
        if depth >= Depth(context.config.max_depth):
            return Ok([])

        return await process_page_links(
            page,
            base_url,
            depth,
            context.config.allowed_paths,
            context.url_tracker,
            lambda: increment_total(context.progress),
        )

    except Exception as e:
        await context.logger.log_url_failure(url, e)
        await mark_url_failed(url, str(e), context.url_tracker)
        return make_error(ProcessingError, f"Error processing {url}: {e!s}")


async def worker(context: ScraperContext) -> None:
    """Worker using ROP pattern with improved error handling."""
    page = await context.browser_context.new_page()
    try:
        while True:
            try:
                url, depth = await context.url_queue.get()
                process_result = await process_page(Url(url), Depth(depth), page, context)

                match process_result:
                    case Ok(new_links):
                        for link, link_depth in new_links:
                            await context.url_queue.put((link, link_depth))
                    case Error(e):
                        await context.logger.error(f"Error processing {url}: {e!s}")
                        await mark_url_failed(Url(url), str(e), context.url_tracker)

                context.url_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                await context.logger.error(f"Worker error: {e!s}")
                continue
    finally:
        await page.close()
