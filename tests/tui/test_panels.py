from typing import Any

import pytest

from expression import Error, Ok, effect
from rich.panel import Panel

from fcship.tui.errors import DisplayError
from fcship.tui.panels import (
    PanelConfig,
    PanelSection,
    _create_inner_panel,
    _create_panel_safe,
    _create_panel_unsafe,
    _join_panels,
    create_nested_panel,
    create_panel,
    create_panel_config,
)

# Suppress the PytestReturnNotNoneWarning for all test functions using effect.result
pytestmark = pytest.mark.filterwarnings("ignore::pytest.PytestReturnNotNoneWarning")

# Test Data
VALID_TITLE = "Test Title"
VALID_CONTENT = "Test Content"
VALID_STYLE = "blue"
VALID_CONFIG = PanelConfig(VALID_TITLE, VALID_CONTENT, VALID_STYLE)


@pytest.mark.parametrize(
    "title,content,style",
    [
        ("Title", "Content", "red"),
        ("Another", "Text", "green"),
        ("Test", "Panel", "blue"),
    ],
)
def test_panel_creation_properties(title: str, content: str, style: str):
    """Test panel creation with various valid inputs"""
    config = PanelConfig(title=title, content=content, style=style)
    result = _create_panel_unsafe(config)
    assert result.is_ok()
    panel = result.ok
    assert isinstance(panel, Panel)
    assert panel.title == title
    assert panel.border_style == style


@pytest.mark.parametrize(
    "title,content,style,should_succeed",
    [
        ("Title", "Content", "red", True),
        (123, "Content", "red", False),
        ("Title", None, "red", False),
        ("Title", "Content", "invalid", False),
    ],
)
def test_panel_config_validation(title: Any, content: Any, style: Any, should_succeed: bool):
    """Test panel config validation with various input types"""
    result = create_panel_config(title, content, style)
    assert result.is_ok() == should_succeed
    if should_succeed:
        assert isinstance(result.ok, PanelConfig)
        assert result.ok.title == title
        assert result.ok.content == content
        assert result.ok.style == style
    else:
        assert isinstance(result.error, DisplayError)


def test_join_panels():
    """Test panel joining with various panel combinations"""
    panels = [
        Panel("Content 1", title="Title 1", border_style="red"),
        Panel("Content 2", title="Title 2", border_style="blue"),
    ]
    result = _join_panels(panels)
    assert isinstance(result, str)
    assert result != ""
    for panel in panels:
        assert str(panel.renderable) in result


@effect.result[Panel, DisplayError]()
def test_nested_panel_properties():
    """Test nested panel creation with various inputs"""
    title = "Outer Panel"
    sections = [("Inner 1", "Content 1"), ("Inner 2", "Content 2")]
    result = yield from create_nested_panel(
        title, sections, outer_style="blue", inner_style="green"
    )
    assert result.is_ok()
    panel = result.ok
    assert isinstance(panel, Panel)
    assert panel.title == title
    assert panel.border_style == "blue"


# Test invalid type configurations
INVALID_CONFIG_TITLE = PanelConfig(title=123, content=VALID_CONTENT, style=VALID_STYLE)  # type: ignore
INVALID_CONFIG_CONTENT = PanelConfig(title=VALID_TITLE, content=456, style=VALID_STYLE)  # type: ignore
INVALID_CONFIG_STYLE = PanelConfig(title=VALID_TITLE, content=VALID_CONTENT, style=789)  # type: ignore


def test_create_panel_safe_invalid_title_type():
    """Test that _create_panel_safe handles invalid title type"""
    result = _create_panel_safe(INVALID_CONFIG_TITLE)
    assert result.is_error()
    assert "Invalid panel configuration" in str(result.error)


def test_create_panel_safe_invalid_content_type():
    """Test that _create_panel_safe handles invalid content type"""
    result = _create_panel_safe(INVALID_CONFIG_CONTENT)
    assert result.is_error()
    assert "Invalid panel configuration" in str(result.error)


def test_create_panel_safe_invalid_style_type():
    """Test that _create_panel_safe handles invalid style type"""
    result = _create_panel_safe(INVALID_CONFIG_STYLE)
    assert result.is_error()
    assert "Invalid panel configuration" in str(result.error)


def test_create_panel_safe_exception(monkeypatch):
    """Test that _create_panel_safe handles exceptions"""

    def mock_panel(*args, **kwargs):
        raise Exception("Mock panel creation error")

    monkeypatch.setattr("fcship.tui.panels.Panel", mock_panel)
    result = _create_panel_safe(VALID_CONFIG)
    assert result.is_error()
    assert "Failed to create panel" in str(result.error)


@effect.result[Panel, DisplayError]()
def test_create_inner_panel_error():
    """Test that _create_inner_panel handles errors"""
    section = PanelSection(title="", content=VALID_CONTENT)
    result = yield from _create_inner_panel(VALID_STYLE, section)
    assert result.is_error()
    assert "Title cannot be empty" in str(result.error)


@effect.result[Panel, DisplayError]()
def test_create_nested_panel_inner_panel_error():
    """Test that create_nested_panel handles inner panel creation errors"""
    sections = [("", VALID_CONTENT)]  # Invalid section with empty title
    result = yield from create_nested_panel(VALID_TITLE, sections)
    assert result.is_error()
    assert "Title cannot be empty" in str(result.error)


@effect.result[Panel, DisplayError]()
def test_create_nested_panel_outer_panel_error():
    """Test that create_nested_panel handles outer panel creation errors"""
    sections = [(VALID_TITLE, VALID_CONTENT)]
    result = yield from create_nested_panel("", sections)  # Invalid outer panel title
    assert result.is_error()
    assert "Title cannot be empty" in str(result.error)


@effect.result[Panel, DisplayError]()
def test_create_nested_panel_empty_sections():
    """Test that create_nested_panel handles empty sections list"""
    result = yield from create_nested_panel(VALID_TITLE, [])
    assert result.is_ok()
    assert isinstance(result.ok, Panel)


@effect.result[Panel, DisplayError]()
def test_create_nested_panel_multiple_sections():
    """Test that create_nested_panel handles multiple sections"""
    sections = [("Section 1", "Content 1"), ("Section 2", "Content 2")]
    result = yield from create_nested_panel(VALID_TITLE, sections)
    assert result.is_ok()
    assert isinstance(result.ok, Panel)


@effect.result[Panel, DisplayError]()
def test_create_panel_success():
    """Test that create_panel succeeds with valid input"""
    result = yield from create_panel(VALID_TITLE, VALID_CONTENT, VALID_STYLE)
    assert result.is_ok()
    assert isinstance(result.ok, Panel)


@effect.result[Panel, DisplayError]()
def test_create_panel_invalid_input():
    """Test that create_panel fails with invalid input"""
    result = yield from create_panel("", VALID_CONTENT, VALID_STYLE)
    assert result.is_error()
    assert "Title cannot be empty" in str(result.error)


@effect.result[Panel, DisplayError]()
def test_create_nested_panel_inner_panel_error_with_mock(monkeypatch):
    """Test that create_nested_panel handles inner panel creation errors with mock"""

    @effect.result[Panel, DisplayError]()
    def mock_create_inner_panel(*args, **kwargs):
        yield Error(DisplayError.Rendering("Mock inner panel error", None))

    monkeypatch.setattr("fcship.tui.panels._create_inner_panel", mock_create_inner_panel)
    sections = [(VALID_TITLE, VALID_CONTENT)]
    result = yield from create_nested_panel(VALID_TITLE, sections)
    assert result.is_error()
    assert "Mock inner panel error" in str(result.error)


@effect.result[Panel, DisplayError]()
def test_create_nested_panel_outer_panel_error_with_mock(monkeypatch):
    """Test that create_nested_panel handles outer panel creation errors with mock"""

    @effect.result[Panel, DisplayError]()
    def mock_create_inner_panel(*args, **kwargs):
        yield Ok(Panel("test"))

    @effect.result[Panel, DisplayError]()
    def mock_create_panel(*args, **kwargs):
        yield Error(DisplayError.Rendering("Mock outer panel error", None))

    monkeypatch.setattr("fcship.tui.panels._create_inner_panel", mock_create_inner_panel)
    monkeypatch.setattr("fcship.tui.panels.create_panel", mock_create_panel)
    sections = [(VALID_TITLE, VALID_CONTENT)]
    result = yield from create_nested_panel(VALID_TITLE, sections)
    assert result.is_error()
    assert "Mock outer panel error" in str(result.error)
