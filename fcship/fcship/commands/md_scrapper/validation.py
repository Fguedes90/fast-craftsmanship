"""Validation module with functional approach."""
from typing import List, Optional, Any
from expression import Result, Ok, Error, pipe, pipeline
from urllib.parse import urlparse
from .validation_exceptions import (
    ValidationError,
    ConfigValidationException,
    UrlValidationException,
    SelectorValidationException,
    PathValidationException
)
from .types import Url, Depth
from .type_helpers import ensure_url, ensure_depth

def collect_validation_errors(validations: list[Result[Any, ValidationError]]) -> Result[None, ConfigValidationException]:
    """Collect all validation errors into a single result."""
    errors = [error for result in validations if isinstance(result, Error) for error in [result.error]]
    return Error(ConfigValidationException(errors)) if errors else Ok(None)

def validate_url_format(url: str) -> Result[str, ValidationError]:
    """Validate URL format."""
    try:
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return Error(ValidationError(
                field="url",
                message="URL must include scheme and domain",
                value=url
            ))
        if parsed.scheme not in ('http', 'https'):
            return Error(ValidationError(
                field="url",
                message="URL scheme must be http or https",
                value=url
            ))
        return Ok(url)
    except Exception:
        return Error(ValidationError(
            field="url",
            message="Invalid URL format",
            value=url
        ))

def validate_paths(paths: list[str]) -> Result[list[str], ValidationError]:
    """Validate allowed paths."""
    if not paths:
        return Error(ValidationError(
            field="allowed_paths",
            message="At least one path must be provided",
            value=paths
        ))
    
    invalid_paths = [
        path for path in paths 
        if not path.startswith('/')
    ]
    
    if invalid_paths:
        return Error(ValidationError(
            field="allowed_paths",
            message="All paths must start with /",
            value=invalid_paths
        ))
    
    return Ok(paths)

def validate_positive_int(value: int, field: str) -> Result[int, ValidationError]:
    """Validate positive integer."""
    if value <= 0:
        return Error(ValidationError(
            field=field,
            message="Must be greater than 0",
            value=value
        ))
    return Ok(value)

def validate_timeout(value: float) -> Result[float, ValidationError]:
    """Validate timeout value."""
    if value <= 0:
        return Error(ValidationError(
            field="timeout",
            message="Must be greater than 0",
            value=value
        ))
    if value > 300:  # 5 minutes max
        return Error(ValidationError(
            field="timeout",
            message="Must not exceed 300 seconds",
            value=value
        ))
    return Ok(value)

def validate_content_selector(selector: Optional[str]) -> Result[Optional[str], ValidationError]:
    """Validate content selector if provided."""
    if selector is None:
        return Ok(None)

    if selector := selector.strip():
        return Ok(selector)
    else:
        return Error(ValidationError(
            field="content_selector",
            message="Cannot be empty if provided",
            value=selector
        ))

@pipeline
def validate_scraper_config(
    root_url: str,
    allowed_paths: list[str],
    max_concurrent: int,
    max_depth: int,
    timeout: float
) -> Result[None, ConfigValidationException]:
    """Validate all scraper configuration using ROP."""
    validations = [
        pipe(
            root_url,
            validate_url_format,
            lambda r: r.bind(ensure_url)
        ),
        validate_paths(allowed_paths),
        validate_positive_int(max_concurrent, "max_concurrent"),
        pipe(
            max_depth,
            lambda d: validate_positive_int(d, "max_depth"),
            lambda r: r.bind(ensure_depth)
        ),
        validate_timeout(timeout)
    ]
    
    return collect_validation_errors(validations)

def validate_extracted_url(url: str, base_url: str) -> Result[Url, UrlValidationException]:
    """Validate an extracted URL."""
    try:
        parsed = urlparse(url)
        if not parsed.scheme and not parsed.netloc:
            return Error(UrlValidationException(url, "Missing scheme and domain"))
        
        if parsed.scheme not in ('http', 'https'):
            return Error(UrlValidationException(url, "Invalid scheme"))
            
        if not url.startswith(base_url):
            return Error(UrlValidationException(url, "Outside of base domain"))
            
        return Ok(Url(url))
    except Exception as e:
        return Error(UrlValidationException(url, str(e)))