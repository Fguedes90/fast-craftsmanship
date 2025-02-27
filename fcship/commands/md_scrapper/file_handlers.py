"""File type handlers with functional approach."""

from dataclasses import dataclass
from typing import Protocol

import markdown

from bs4 import BeautifulSoup
from expression import Error, Ok, Result

from fcship.utils.functional import catch_errors_async

from .exceptions import ContentException, ProcessingException
from .types import Content, Filename


class ContentTransformer(Protocol):
    """Protocol for content transformers."""

    async def transform(self, content: str) -> Result[str, ProcessingException]:
        """Transform content."""
        ...


@dataclass
class FileTypeHandler:
    """Handler for specific file type."""

    extension: str
    transformer: ContentTransformer
    media_type: str


class HtmlToMarkdownTransformer:
    """Transform HTML to Markdown."""

    @catch_errors_async(ContentException, "HTML to Markdown transformation failed")
    async def transform(self, content: str) -> Result[str, ProcessingException]:
        try:
            soup = BeautifulSoup(content, "html.parser")
            return Ok(soup.get_text())
        except Exception as e:
            return Error(ContentException("Failed to parse HTML", e))


class MarkdownTransformer:
    """Transform Markdown to HTML."""

    @catch_errors_async(ContentException, "Markdown to HTML transformation failed")
    async def transform(self, content: str) -> Result[str, ProcessingException]:
        try:
            return Ok(markdown.markdown(content))
        except Exception as e:
            return Error(ContentException("Failed to parse Markdown", e))


class PassthroughTransformer:
    """No transformation, pass content through."""

    async def transform(self, content: str) -> Result[str, ProcessingException]:
        return Ok(content)


class FileTypeRegistry:
    """Registry of file type handlers."""

    def __init__(self):
        self.handlers: dict[str, FileTypeHandler] = {}

    def register(self, handler: FileTypeHandler) -> None:
        """Register a file type handler."""
        self.handlers[handler.extension] = handler

    def get_handler(self, filename: str) -> FileTypeHandler | None:
        """Get handler for file type."""
        ext = filename.split(".")[-1].lower()
        return self.handlers.get(ext)


@catch_errors_async(ContentException, "Failed to process content")
async def process_content(
    content: Content, filename: Filename, registry: FileTypeRegistry
) -> Result[tuple[Content, Filename], ProcessingException]:
    """Process content based on file type."""
    handler = registry.get_handler(filename)
    if not handler:
        return Ok((content, filename))

    transformed = await handler.transformer.transform(content)
    if isinstance(transformed, Error):
        return transformed

    new_filename = f"{filename.rsplit('.', 1)[0]}.{handler.extension}"
    return Ok((Content(transformed.value), Filename(new_filename)))
