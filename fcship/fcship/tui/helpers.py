from collections.abc import Iterable
from expression import Ok, Error, Result, pipe
from fcship.tui.errors import DisplayError

def validate_input(value: str | None, name: str) -> Result[str, DisplayError]:
    return Ok(value) if value else Error(DisplayError.Validation(f"{name} cannot be empty"))

def is_valid_style(style: str) -> bool:
    VALID_STYLES = ("red", "green", "blue", "yellow", "cyan", "magenta", "white", "black")
    return style in VALID_STYLES

def validate_style(style: str) -> Result[str, DisplayError]:
    return pipe(
        validate_input(style, "Style"),
        lambda s: Ok(s) if is_valid_style(s)
            else Error(DisplayError.Validation(f"Invalid style: {s}. Must be one of: red, green, blue, yellow, cyan, magenta, white, black"))
    )

def validate_panel_inputs(title: str, content: str, style: str) -> Result[tuple[str, str, str], DisplayError]:
    return pipe(
        validate_input(title, "Title"),
        lambda t: validate_input(content, "Content").map(lambda c: (t, c)),
        lambda tc: validate_style(style).map(lambda s: (tc[0], tc[1], s))
    )

def validate_table_row(row: any) -> Result[tuple[str, str], DisplayError]:
    if isinstance(row, tuple) and len(row) == 2 and all(isinstance(x, str) for x in row):
        return Ok(row)
    else:
        return Error(DisplayError.Validation("Row must be a tuple of two strings"))

def validate_table_data(headers: list[str], rows: list[tuple[str, str]]) -> Result[None, DisplayError]:
    if not headers:
        return Error(DisplayError.Validation("Headers list cannot be empty"))
    if not all(isinstance(h, str) for h in headers):
        return Error(DisplayError.Validation("Headers must be strings"))
    if any(len(row) != len(headers) for row in rows):
        return Error(DisplayError.Validation("All rows must have same length as headers"))
    if not all(all(isinstance(cell, str) for cell in row) for row in rows):
        return Error(DisplayError.Validation("All cells must be strings"))
    return Ok(None)

def validate_progress_inputs(items: Iterable, process_fn: callable, description: str) -> Result[None, DisplayError]:
    try:
        items_list = list(items)
        return pipe(
            items_list,
            lambda i: Ok(i) if i else Error(DisplayError.Validation("Items list cannot be empty")),
            lambda _: Ok(None) if callable(process_fn) else Error(DisplayError.Validation("Process function must be callable")),
            lambda _: validate_input(description, "Description").map(lambda _: None)
        )
    except Exception as e:
        return Error(DisplayError.Validation(f"Invalid progress inputs: {str(e)}"))
