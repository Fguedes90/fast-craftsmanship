from collections.abc import Iterable
from expression import Ok, Error, Result, pipe, tagged_union, effect
from fcship.tui.errors import DisplayError
from typing import Any, TypeVar, Callable, List, Tuple, Optional, Literal
from functools import partial, reduce
from dataclasses import dataclass

T = TypeVar('T')
U = TypeVar('U')

@tagged_union
class ValidationError:
    """Validation-related errors"""
    tag: Literal["type", "empty", "format", "length"]
    type: Tuple[str, type, Any] = None  # (name, expected_type, actual_value)
    empty: str = None  # field name
    format: Tuple[str, str] = None  # (field_name, expected_format)
    length: Tuple[str, int, int] = None  # (field_name, expected_length, actual_length)

    @staticmethod
    def Type(name: str, expected: type, actual: Any) -> "ValidationError":
        return ValidationError(tag="type", type=(name, expected, actual))

    @staticmethod
    def Empty(field: str) -> "ValidationError":
        return ValidationError(tag="empty", empty=field)

    @staticmethod
    def Format(field: str, expected: str) -> "ValidationError":
        return ValidationError(tag="format", format=(field, expected))

    @staticmethod
    def Length(field: str, expected: int, actual: int) -> "ValidationError":
        return ValidationError(tag="length", length=(field, expected, actual))

def to_display_error(error: ValidationError) -> DisplayError:
    """Convert ValidationError to DisplayError"""
    match error:
        case ValidationError(tag="type", type=(name, expected, _)):
            return DisplayError.Validation(f"{name} must be a {expected.__name__}")
        case ValidationError(tag="empty", empty=field):
            return DisplayError.Validation(f"{field} cannot be empty")
        case ValidationError(tag="format", format=(field, expected)):
            return DisplayError.Validation(f"{field} must be in format: {expected}")
        case ValidationError(tag="length", length=(field, expected, actual)):
            return DisplayError.Validation(f"{field} must have length {expected}, got {actual}")

def _check_type(value: Any, expected_type: type, name: str) -> Result[Any, DisplayError]:
    return (
        Ok(value)
        if isinstance(value, expected_type)
        else Error(to_display_error(ValidationError.Type(name, expected_type, value)))
    )

def _check_non_empty(value: str, name: str) -> Result[str, DisplayError]:
    return (
        Ok(value)
        if value.strip()
        else Error(to_display_error(ValidationError.Empty(name)))
    )

def validate_input(value: Optional[str], name: str) -> Result[str, DisplayError]:
    return pipe(
        _check_type(value, str, name),
        lambda r: r.bind(lambda v: _check_non_empty(v, name))
    )

VALID_STYLES = frozenset({"red", "green", "blue", "yellow", "cyan", "magenta", "white", "black", "bold red"})

def _contains_valid_style(style: str) -> bool:
    return any(s in style for s in VALID_STYLES)

def is_valid_style(style: str) -> bool:
    return isinstance(style, str) and _contains_valid_style(style)

def _validate_style_content(style: str) -> Result[str, DisplayError]:
    return (
        Ok(style)
        if _contains_valid_style(style)
        else Error(to_display_error(ValidationError.Format("style", f"one of: {', '.join(VALID_STYLES)}")))
    )

def validate_style(style: str) -> Result[str, DisplayError]:
    return pipe(
        validate_input(style, "Style"),
        lambda r: r.bind(_validate_style_content)
    )

def _combine_validation_results(results: List[Result[T, DisplayError]]) -> Result[List[T], DisplayError]:
    """Combines multiple validation results into a single Result"""
    def combine(acc: Result[List[T], DisplayError], curr: Result[T, DisplayError]) -> Result[List[T], DisplayError]:
        if acc.is_error():
            return acc
        if curr.is_error():
            return curr
        return Ok([*acc.ok, curr.ok])
    
    return pipe(
        results,
        lambda r: reduce(combine, r, Ok([]))
    )

def validate_panel_inputs(title: str, content: str, style: str) -> Result[Tuple[str, str, str], DisplayError]:
    validations = [
        validate_input(title, "Title"),
        validate_input(content, "Content"),
        validate_style(style)
    ]
    return pipe(
        _combine_validation_results(validations),
        lambda r: r.map(tuple)
    )

def _validate_row_type(row: Any) -> Result[Tuple[str, str], DisplayError]:
    return (
        Ok(row)
        if isinstance(row, tuple) and len(row) == 2 and all(isinstance(x, str) for x in row)
        else Error(to_display_error(ValidationError.Format("row", "tuple of two strings")))
    )

def validate_table_row(row: Any) -> Result[Tuple[str, str], DisplayError]:
    return _validate_row_type(row)

def _validate_headers(headers: List[str]) -> Result[List[str], DisplayError]:
    return (
        Ok(headers)
        if headers and all(isinstance(h, str) for h in headers)
        else Error(to_display_error(ValidationError.Format("headers", "non-empty list of strings")))
    )

def _validate_row_length(row: List[Any], header_length: int) -> Result[List[Any], DisplayError]:
    return (
        Ok(row)
        if len(row) == header_length
        else Error(to_display_error(ValidationError.Length("row", header_length, len(row))))
    )

def _validate_row_types(row: List[Any]) -> Result[List[str], DisplayError]:
    return (
        Ok(row)
        if all(isinstance(cell, str) for cell in row)
        else Error(to_display_error(ValidationError.Format("cells", "strings")))
    )

def validate_table_data(headers: List[str], rows: List[Tuple[str, str]]) -> Result[None, DisplayError]:
    def validate_row(row: List[Any], header_len: int) -> Result[List[str], DisplayError]:
        return pipe(
            _validate_row_length(row, header_len),
            lambda r: r.bind(_validate_row_types)
        )

    return pipe(
        _validate_headers(headers),
        lambda r: r.bind(lambda h: _combine_validation_results([
            validate_row(row, len(h)) for row in rows
        ])),
        lambda r: r.map(lambda _: None)
    )

def _validate_items_not_empty(items: List[Any]) -> Result[List[Any], DisplayError]:
    return (
        Ok(items)
        if items
        else Error(to_display_error(ValidationError.Empty("items list")))
    )

def _validate_callable(fn: Any) -> Result[Callable, DisplayError]:
    return (
        Ok(fn)
        if callable(fn)
        else Error(to_display_error(ValidationError.Type("process function", Callable, fn)))
    )

def validate_progress_inputs(items: Iterable, process_fn: Callable, description: str) -> Result[None, DisplayError]:
    return pipe(
        Ok(list(items)),
        lambda items_list: _combine_validation_results([
            _validate_items_not_empty(items_list),
            _validate_callable(process_fn),
            validate_input(description, "Description")
        ]),
        lambda r: r.map(lambda _: None)
    ).map_error(lambda e: DisplayError.Validation(str(e)))
