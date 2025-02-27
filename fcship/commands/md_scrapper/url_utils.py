"""URL handling with Railway Oriented Programming."""

from urllib.parse import urljoin, urlparse

from expression import Ok, Result

from .types import (
    Url,
    ValidationError,
    make_error,
)


def validate_url(url: Url, base_url: str, allowed_paths: list[str]) -> Result[bool, Exception]:
    """Validate URL using ROP."""
    if not url or not isinstance(url, str):
        return Ok(False)

    try:
        parsed = urlparse(url)

        if parsed.scheme and parsed.netloc and not url.startswith(base_url):
            return Ok(False)

        path = parsed.path
        if path.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".pdf", ".zip")):
            return Ok(False)

        return Ok(any(allowed_path in path for allowed_path in allowed_paths))
    except Exception as e:
        return make_error(ValidationError, f"Failed to validate URL {url}: {e!s}")


def normalize_url(url: str) -> Result[Url, Exception]:
    """Normalize URL using ROP."""
    try:
        base_url = url.split("#")[0]
        return Ok(Url(base_url))
    except Exception as e:
        return make_error(ValidationError, f"Failed to normalize URL {url}: {e!s}")


def join_urls(base: str, path: str) -> Result[Url, Exception]:
    """Join URLs using ROP."""
    try:
        return Ok(Url(urljoin(base, path)))
    except Exception as e:
        return make_error(ValidationError, f"Failed to join URLs {base} and {path}: {e!s}")


def extract_base_url(url: str) -> Result[Url, Exception]:
    """Extract base URL using ROP."""
    try:
        parsed = urlparse(url)
        return Ok(Url(f"{parsed.scheme}://{parsed.netloc}"))
    except Exception as e:
        return make_error(ValidationError, f"Failed to extract base URL from {url}: {e!s}")


def get_safe_filename(url: str, is_markdown: bool = False) -> Result[str, Exception]:
    """Generate safe filename from URL using ROP."""
    try:
        url_without_fragment = url.split("#")[0]
        path = urlparse(url_without_fragment).path.strip("/") or "index"

        safe_path = "".join(c if c.isalnum() or c == "/" else "_" for c in path)
        safe_path = safe_path.replace("/", "_")

        return Ok(f"{safe_path}.md" if is_markdown else f"{safe_path}.html")
    except Exception as e:
        return make_error(ValidationError, f"Failed to generate safe filename for {url}: {e!s}")
