from expression import Ok, Error, Result, pipe
from rich.panel import Panel
from fcship.tui.helpers import validate_panel_inputs
from fcship.tui.errors import DisplayError

def _try_create_panel(content: str, title: str, style: str) -> Result[Panel, DisplayError]:
    try:
        return Ok(Panel(content, title=title, border_style=style))
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to create panel", e))

def create_panel(title: str, content: str, style: str) -> Result[Panel, DisplayError]:
    return Result.pipeline(
        lambda _: Ok(None),
        lambda _: validate_panel_inputs(title, content, style),
        lambda _: _try_create_panel(content, title, style)
    )(None)

def create_nested_panel(title: str, sections: list[tuple[str, str]], outer_style: str = "blue", inner_style: str = "cyan") -> Result[Panel, DisplayError]:
    inner_results = [create_panel(section_title, section_content, inner_style) for section_title, section_content in sections]
    if not all(r.is_ok() for r in inner_results):
        return Error(DisplayError.Validation("Failed to create inner panels"))
    content = "\n".join(str(r.ok) for r in inner_results if r.is_ok())
    return create_panel(title, content, outer_style)
