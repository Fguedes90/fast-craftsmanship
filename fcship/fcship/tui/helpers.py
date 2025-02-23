from collections.abc import Iterable
from expression import Ok, Error, Result, pipe
from fcship.tui.errors import DisplayError
from typing import Any, TypeVar, Callable
from functools import partial

T = TypeVar('T')

def _check_type(value: Any, expected_type: type, name: str) -> Result[Any, DisplayError]:
    return Ok(value) if isinstance(value, expected_type) else Error(DisplayError.Validation(f"{name} must be a {expected_type.__name__}"))

def _check_non_empty(value: str, name: str) -> Result[str, DisplayError]:
    return Ok(value) if value.strip() else Error(DisplayError.Validation(f"{name} cannot be empty"))

def validate_input(value: str | None, name: str) -> Result[str, DisplayError]:
    return pipe(
        _check_type(value, str, name),
        lambda r: r.bind(lambda v: _check_non_empty(v, name))
    )

VALID_STYLES = ("red", "green", "blue", "yellow", "cyan", "magenta", "white", "black", "bold red")

def _contains_valid_style(style: str) -> bool:
    return any(s in style for s in VALID_STYLES)

def is_valid_style(style: str) -> bool:
    return isinstance(style, str) and _contains_valid_style(style)

def _validate_style_content(style: str) -> Result[str, DisplayError]:
    return (
        Ok(style) if _contains_valid_style(style)
        else Error(DisplayError.Validation(f"Invalid style: {style}. Must contain one of: {', '.join(VALID_STYLES)}"))
    )

def validate_style(style: str) -> Result[str, DisplayError]:
    return pipe(
        validate_input(style, "Style"),
        lambda r: r.bind(_validate_style_content)
    )

def _combine_validation_results(results: list[Result[T, DisplayError]]) -> Result[list[T], DisplayError]:
    """Combines multiple validation results into a single Result"""
    values = []
    for result in results:
        if result.is_error():
            return result
        values.append(result.ok)
    return Ok(values)

def validate_panel_inputs(title: str, content: str, style: str) -> Result[tuple[str, str, str], DisplayError]:
    validations = [
        validate_input(title, "Title"),
        validate_input(content, "Content"),
        validate_style(style)
    ]
    return pipe(
        _combine_validation_results(validations),
        lambda r: r.map(lambda values: tuple(values))
    )

def _validate_row_type(row: Any) -> Result[tuple[str, str], DisplayError]:
    return (
        Ok(row) if isinstance(row, tuple) and len(row) == 2 and all(isinstance(x, str) for x in row)
        else Error(DisplayError.Validation("Row must be a tuple of two strings"))
    )

def validate_table_row(row: Any) -> Result[tuple[str, str], DisplayError]:
    return _validate_row_type(row)

def _validate_headers(headers: list[str]) -> Result[list[str], DisplayError]:
    return (
        Ok(headers) if headers and all(isinstance(h, str) for h in headers)
        else Error(DisplayError.Validation("Headers must be non-empty list of strings"))
    )

def _validate_row_length(row: list[Any], header_length: int) -> Result[list[Any], DisplayError]:
    return (
        Ok(row) if len(row) == header_length
        else Error(DisplayError.Validation("All rows must have same length as headers"))
    )

def _validate_row_types(row: list[Any]) -> Result[list[str], DisplayError]:
    return (
        Ok(row) if all(isinstance(cell, str) for cell in row)
        else Error(DisplayError.Validation("All cells must be strings"))
    )

def validate_table_data(headers: list[str], rows: list[tuple[str, str]]) -> Result[None, DisplayError]:
    return pipe(
        _validate_headers(headers),
        lambda r: r.bind(lambda h: _combine_validation_results([
            pipe(
                _validate_row_length(row, len(h)),
                lambda r: r.bind(_validate_row_types)
            )
            for row in rows
        ])),
        lambda r: r.map(lambda _: None)
    )

def _validate_items_not_empty(items: list[Any]) -> Result[list[Any], DisplayError]:
    return (
        Ok(items) if items
        else Error(DisplayError.Validation("Items list cannot be empty"))
    )

def _validate_callable(fn: Any) -> Result[Callable, DisplayError]:
    return (
        Ok(fn) if callable(fn)
        else Error(DisplayError.Validation("Process function must be callable"))
    )

def validate_progress_inputs(items: Iterable, process_fn: callable, description: str) -> Result[None, DisplayError]:
    try:
        items_list = list(items)
        return pipe(
            _combine_validation_results([
                _validate_items_not_empty(items_list),
                _validate_callable(process_fn),
                validate_input(description, "Description")
            ]),
            lambda r: r.map(lambda _: None)
        )
    except Exception as e:
        return Error(DisplayError.Validation(f"Invalid progress inputs: {str(e)}"))
