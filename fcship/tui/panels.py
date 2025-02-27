from dataclasses import dataclass
from typing import TypeVar

from expression import Error, Ok, Result, effect, pipe
from rich.panel import Panel

from fcship.tui.errors import DisplayError
from fcship.tui.helpers import validate_panel_inputs

T = TypeVar("T")


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
        lambda r: r.map(lambda values: PanelConfig(*values)),
    )


def _create_panel_unsafe(config: PanelConfig) -> Result[Panel, DisplayError]:
    """Pure function to create a Panel"""
    try:
        return Ok(Panel(config.content, title=config.title, border_style=config.style))
    except Exception as e:
        return Error(
            DisplayError.Rendering(f"Failed to create panel with title '{config.title}'", e)
        )


def _create_panel_safe(config: PanelConfig) -> Result[Panel, DisplayError]:
    """Safe version of panel creation with error handling"""

    def validate_config(cfg: PanelConfig) -> Result[PanelConfig, DisplayError]:
        return (
            Ok(cfg)
            if isinstance(cfg, PanelConfig)
            and all(isinstance(v, str) for v in (cfg.title, cfg.content, cfg.style))
            else Error(
                DisplayError.Rendering(
                    "Invalid panel configuration: all fields must be strings", None
                )
            )
        )

    return pipe(
        Ok(config), lambda r: validate_config(config), lambda r: r.bind(_create_panel_unsafe)
    )


@effect.result[Panel, DisplayError]()
def _create_inner_panel(inner_style: str, section: PanelSection) -> Result[Panel, DisplayError]:
    """Create an inner panel with specific style"""
    return (yield from create_panel(section.title, section.content, inner_style))


def _join_panels(panels: list[Panel]) -> str:
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


def _create_sections(sections: list[tuple[str, str]]) -> list[PanelSection]:
    """Convert section tuples to PanelSection objects"""
    return [PanelSection(title=title, content=content) for title, content in sections]


@effect.result[list[Panel], DisplayError]()
def _create_inner_panels(
    sections: list[PanelSection], inner_style: str
) -> Result[list[Panel], DisplayError]:
    """Create all inner panels with error handling"""
    panels: list[Panel] = []
    for section in sections:
        panel_result = yield from _create_inner_panel(inner_style, section)
        if panel_result.is_error():
            return Error(panel_result.error)
        panels.append(panel_result.ok)
    return Ok(panels)


@effect.result[Panel, DisplayError]()
def create_nested_panel(
    title: str,
    sections: list[tuple[str, str]],
    outer_style: str = "blue",
    inner_style: str = "cyan",
) -> Result[Panel, DisplayError]:
    """
    Create a panel containing other panels.
    Each section is transformed into an inner panel.
    """
    # Convert sections to domain objects
    panel_sections = _create_sections(sections)

    # Create inner panels
    inner_panels_result = yield from _create_inner_panels(panel_sections, inner_style)
    if inner_panels_result.is_error():
        return Error(inner_panels_result.error)

    # Join panels and create outer panel
    content = _join_panels(inner_panels_result.ok)
    return (yield from create_panel(title, content, outer_style))
