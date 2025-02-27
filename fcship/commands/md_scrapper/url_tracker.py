"""URL tracking module with functional approach."""

import asyncio

from typing import Any, dict, list, set, tuple

from expression import Ok, Result, pipe

from fcship.utils.functional import ensure_async, log_and_continue, pipe_async

from .types import Depth, LinkResult, ProcessingError, ScraperResult, Url, make_error
from .url_utils import join_urls, normalize_url, validate_url


class UrlTracker:
    def __init__(self):
        self.visited_urls: set[Url] = set()
        self.processed_urls: set[Url] = set()
        self.failed_urls: dict[Url, str] = {}

        self.visited_lock = asyncio.Lock()
        self.processed_lock = asyncio.Lock()
        self.failed_lock = asyncio.Lock()


async def process_link(
    link: Any, base_url: Url, depth: Depth, allowed_paths: list[str], tracker: UrlTracker
) -> Result[tuple[Url, Depth], Exception]:
    """Process a single link using ROP."""
    try:
        href = await link.get_attribute("href")
        if not href:
            return Ok(None)

        next_url_result = await pipe(
            join_urls(base_url, href),
            lambda url: ensure_async(url) if isinstance(url, Ok) else ensure_async(Ok(None)),
        )

        if not isinstance(next_url_result, Ok) or not next_url_result.value:
            return Ok(None)

        next_url = next_url_result.value
        normalized_url = await ensure_async(normalize_url(next_url))

        if not isinstance(normalized_url, Ok):
            return log_and_continue(normalized_url, "URL normalization")

        next_base_url = normalized_url.value
        validation_result = await pipe_async(
            lambda url: ensure_async(validate_url(url, base_url, allowed_paths)),
            lambda valid: ensure_async(
                Ok(valid and not (is_url_processed(next_base_url, tracker)))
            ),
        )(next_base_url)

        if isinstance(validation_result, Ok) and validation_result.value:
            return Ok((next_url, Depth(depth + 1)))

        return Ok(None)

    except Exception as e:
        return make_error(ProcessingError, f"Failed to process link: {e!s}")


async def process_page_links(
    page: Any,
    base_url: Url,
    depth: Depth,
    allowed_paths: list[str],
    tracker: UrlTracker,
    progress_callback: callable,
) -> LinkResult:
    """Process page links using ROP."""
    try:
        links = await page.query_selector_all("a[href]")
        new_links: list[tuple[Url, Depth]] = []

        for link in links:
            link_result = await process_link(link, base_url, depth, allowed_paths, tracker)

            if link_result.is_ok():
                new_links.append(link_result.ok)
                await progress_callback()

        return Ok(new_links)
    except Exception as e:
        return make_error(ProcessingError, f"Failed to process page links: {e!s}")


async def is_url_processed(url: Url, tracker: UrlTracker) -> Result[bool, Exception]:
    """Check if URL is processed using ROP."""
    try:
        base_url = url.split("#")[0]

        async with tracker.visited_lock:
            if Url(base_url) in tracker.visited_urls:
                return Ok(True)

        async with tracker.processed_lock:
            if Url(base_url) in tracker.processed_urls:
                return Ok(True)

        return Ok(False)
    except Exception as e:
        return make_error(ProcessingError, f"Failed to check URL status: {e!s}")


async def mark_url_visited(url: Url, tracker: UrlTracker) -> ScraperResult:
    """Mark URL as visited using ROP."""
    try:
        async with tracker.visited_lock:
            tracker.visited_urls.add(url)
        return Ok(None)
    except Exception as e:
        return make_error(ProcessingError, f"Failed to mark URL as visited: {e!s}")


async def mark_url_processed(url: Url, tracker: UrlTracker) -> ScraperResult:
    """Mark URL as processed using ROP."""
    try:
        async with tracker.processed_lock:
            tracker.processed_urls.add(url)
        return Ok(None)
    except Exception as e:
        return make_error(ProcessingError, f"Failed to mark URL as processed: {e!s}")


async def mark_url_failed(url: Url, error: str, tracker: UrlTracker) -> ScraperResult:
    """Mark URL as failed using ROP."""
    try:
        async with tracker.failed_lock:
            tracker.failed_urls[url] = error
        return Ok(None)
    except Exception as e:
        return make_error(ProcessingError, f"Failed to mark URL as failed: {e!s}")
