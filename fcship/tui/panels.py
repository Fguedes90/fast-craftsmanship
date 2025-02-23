from expression import Ok, Error, Result, pipe, effect
from expression.collections import seq
from rich.panel import Panel
from dataclasses import dataclass
from typing import List, Tuple, Callable, TypeVar, Optional
from fcship.tui.helpers import validate_panel_inputs
from fcship.tui.errors import DisplayError

T = TypeVar('T')

@dataclass(frozen=True)
class PanelConfig:
    """Configuration for a panel"""
    title: str
    content: str
    style: str

@dataclass(frozen=True)
class PanelSection:
    """A section in a nested panel"""
    title: str
    content: str

def create_panel_config(title: str, content: str, style: str) -> Result[PanelConfig, DisplayError]:
    """Create a panel configuration with validation"""
    return pipe(
        validate_panel_inputs(title, content, style),
        lambda r: r.map(lambda values: PanelConfig(*values))
    )

def _create_panel_unsafe(config: PanelConfig) -> Result[Panel, DisplayError]:
    """Pure function to create a Panel"""
    return pipe(
        Ok(config),
        lambda c: Ok(Panel(c.content, title=c.title, border_style=c.style))
    ).map_error(lambda e: DisplayError.Rendering(f"Failed to create panel with title '{config.title}'", e))

def _create_panel_safe(config: PanelConfig) -> Result[Panel, DisplayError]:
    """Safe version of panel creation with error handling"""
    def validate_config(cfg: PanelConfig) -> Result[PanelConfig, DisplayError]:
        return (
            Ok(cfg)
            if all(isinstance(v, str) for v in (cfg.title, cfg.content, cfg.style))
            else Error(DisplayError.Rendering("Invalid panel configuration: all fields must be strings", None))
        )
    
    return pipe(
        Ok(config),
        lambda c: validate_config(c),
        lambda r: r.bind(_create_panel_unsafe)
    )

def _create_inner_panel(inner_style: str, section: PanelSection) -> Result[Panel, DisplayError]:
    """Create an inner panel with specific style"""
    return create_panel(section.title, section.content, inner_style)

def _join_panels(panels: List[Panel]) -> str:
    """Join multiple panels into a single string"""
    return "\n".join(str(panel.renderable) for panel in panels)

@effect.result[Panel, DisplayError]()
def create_panel(title: str, content: str, style: str) -> Result[Panel, DisplayError]:
    """
    Create a panel with title, content and style.
    Validates inputs and handles errors safely.
    """
    config = yield from create_panel_config(title, content, style)
    panel = yield from _create_panel_safe(config)
    return Ok(panel)

def _create_sections(sections: List[Tuple[str, str]]) -> List[PanelSection]:
    """Convert section tuples to PanelSection objects"""
    return [PanelSection(title=title, content=content) for title, content in sections]

def _create_inner_panels(sections: List[PanelSection], inner_style: str) -> Result[List[Panel], DisplayError]:
    """Create all inner panels with error handling"""
    def create_panels(acc: Result[List[Panel], DisplayError], section: PanelSection) -> Result[List[Panel], DisplayError]:
        match acc:
            case Error(e):
                return Error(e)
            case Ok(panels):
                return pipe(
                    _create_inner_panel(inner_style, section),
                    lambda r: r.map(lambda p: [*panels, p])
                )
    
    return pipe(
        sections,
        lambda s: seq.fold(create_panels, Ok([]), s)
    )

@effect.result[Panel, DisplayError]()
def create_nested_panel(
    title: str,
    sections: List[Tuple[str, str]],
    outer_style: str = "blue",
    inner_style: str = "cyan"
) -> Result[Panel, DisplayError]:
    """
    Create a panel containing other panels.
    Each section is transformed into an inner panel.
    """
    # Convert sections to domain objects
    panel_sections = _create_sections(sections)
    
    # Create inner panels
    inner_panels = yield from _create_inner_panels(panel_sections, inner_style)
    
    # Join panels and create outer panel
    content = _join_panels(inner_panels)
    panel = yield from create_panel(title, content, outer_style)
    
    return Ok(panel)
