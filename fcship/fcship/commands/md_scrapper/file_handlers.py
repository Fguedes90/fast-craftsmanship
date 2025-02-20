"""File type handlers with functional approach."""
from dataclasses import dataclass
from typing import Optional, Dict, Any, Protocol, Callable
from expression import Result, Ok, Error, pipe
from bs4 import BeautifulSoup
import markdown
from .exceptions import (
    ContentException,
    ProcessingException,
    capture_exception
)
from .types import Content, Filename
from .result_utils import catch_errors_async

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
    async def transform(self, content: str) -> Result[str, ProcessingException]:
        try:
            soup = BeautifulSoup(content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return Ok(text)
        except Exception as e:
            return capture_exception(
                e,
                ContentException,
                "Failed to transform HTML to Markdown"
            )

class MarkdownTransformer:
    """Transform Markdown to HTML."""
    async def transform(self, content: str) -> Result[str, ProcessingException]:
        try:
            html = markdown.markdown(
                content,
                extensions=['extra', 'codehilite']
            )
            return Ok(html)
        except Exception as e:
            return capture_exception(
                e,
                ContentException,
                "Failed to transform Markdown to HTML"
            )

class PassthroughTransformer:
    """No transformation, pass content through."""
    async def transform(self, content: str) -> Result[str, ProcessingException]:
        return Ok(content)

class FileTypeRegistry:
    """Registry of file type handlers."""
    def __init__(self):
        self.handlers: Dict[str, FileTypeHandler] = {
            ".html": FileTypeHandler(
                extension=".html",
                transformer=PassthroughTransformer(),
                media_type="text/html"
            ),
            ".md": FileTypeHandler(
                extension=".md",
                transformer=HtmlToMarkdownTransformer(),
                media_type="text/markdown"
            )
        }
    
    def get_handler(self, filename: str) -> Result[FileTypeHandler, ProcessingException]:
        """Get handler for file extension."""
        from pathlib import Path
        ext = Path(filename).suffix.lower()
        
        if ext not in self.handlers:
            return Error(ContentException(f"Unsupported file type: {ext}"))
        
        return Ok(self.handlers[ext])
    
    def register_handler(
        self,
        extension: str,
        transformer: ContentTransformer,
        media_type: str
    ) -> None:
        """Register a new file type handler."""
        self.handlers[extension.lower()] = FileTypeHandler(
            extension=extension,
            transformer=transformer,
            media_type=media_type
        )

@catch_errors_async(ContentException, "Failed to process content")
async def process_content(
    content: Content,
    filename: Filename,
    registry: FileTypeRegistry
) -> Result[tuple[Content, Filename], ProcessingException]:
    """Process content using appropriate handler."""
    handler_result = registry.get_handler(filename)
    if isinstance(handler_result, Error):
        return handler_result
        
    handler = handler_result.value
    transform_result = await handler.transformer.transform(content)
    if isinstance(transform_result, Error):
        return transform_result
        
    return Ok((Content(transform_result.value), filename))