from collections.abc import Iterable
from expression import Ok, Error, Result, pipe
from fcship.tui.errors import DisplayError

def validate_input(value: str | None, name: str) -> Result[str, DisplayError]:
    return Ok(value) if value else Error(DisplayError.Validation(f"{name} cannot be empty"))

def is_valid_style(style: str) -> bool:
    VALID_STYLES = ("red", "green", "blue", "yellow", "cyan", "magenta", "white", "black", "bold red")
    return any(s in style for s in VALID_STYLES)

def validate_style(style: str) -> Result[str, DisplayError]:
    validation = validate_input(style, "Style")
    if validation.is_error():
        return validation
    if not is_valid_style(style):
        return Error(DisplayError.Validation(f"Invalid style: {style}. Must contain one of: red, green, blue, yellow, cyan, magenta, white, black"))
    return Ok(style)

def validate_panel_inputs(title: str, content: str, style: str) -> Result[tuple[str, str, str], DisplayError]:
    title_result = validate_input(title, "Title")
    if title_result.is_error():
        return title_result
    
    content_result = validate_input(content, "Content")
    if content_result.is_error():
        return content_result
    
    style_result = validate_style(style)
    if style_result.is_error():
        return style_result
    
    return Ok((title_result.ok, content_result.ok, style_result.ok))

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
        if not items_list:
            return Error(DisplayError.Validation("Items list cannot be empty"))
        if not callable(process_fn):
            return Error(DisplayError.Validation("Process function must be callable"))
        
        desc_result = validate_input(description, "Description")
        if desc_result.is_error():
            return desc_result
            
        return Ok(None)
    except Exception as e:
        return Error(DisplayError.Validation(f"Invalid progress inputs: {str(e)}"))
