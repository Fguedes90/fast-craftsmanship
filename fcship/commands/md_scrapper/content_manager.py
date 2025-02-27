"""Content management module with functional approach."""

import logging
import os

from expression import Ok, pipe

from fcship.utils.functional import handle_error

from .result_utils import catch_errors
from .types import (
    Content,
    ContentExtractionError,
    ContentResult,
    Filename,
    ScraperResult,
    Url,
    make_error,
)
from .url_utils import get_safe_filename


async def extract_content(page, url: Url, content_selector: str = None) -> ContentResult:
    """Extract content using ROP."""
    try:
        if content_selector:
            try:
                await page.wait_for_selector(content_selector, timeout=5000)
                content = await page.locator(content_selector).inner_text()
                if content:
                    return pipe(
                        get_safe_filename(url, is_markdown=True),
                        lambda filename: Ok((Content(content), Filename(filename))),
                    )
            except Exception as e:
                logging.warning(f"Content selector error for {url}: {e!s}")

        content = await page.content()
        return pipe(
            get_safe_filename(url), lambda filename: Ok((Content(content), Filename(filename)))
        )
    except Exception as e:
        return make_error(ContentExtractionError, f"Failed to extract content from {url}: {e!s}")


@catch_errors(ContentExtractionError, "Failed to save content")
async def save_content(
    content: Content, filename: Filename, output_dir: str, file_lock
) -> ScraperResult:
    """Save content using ROP."""
    filepath = os.path.join(output_dir, filename)
    try:
        async with file_lock:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        logging.info(f"Saved content to: {filepath}")
        return Ok(None)
    except Exception as e:
        return handle_error(e, f"Failed to save content to {filepath}")
