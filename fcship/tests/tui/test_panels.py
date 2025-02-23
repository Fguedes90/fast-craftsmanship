import pytest
from expression import Ok, Error, effect
from rich.panel import Panel
from fcship.tui.panels import (
    PanelConfig,
    create_panel_config,
    create_panel,
    create_nested_panel,
    _create_panel_unsafe,
    _create_panel_safe,
    _create_inner_panel,
    _join_panels
)
from fcship.tui.errors import DisplayError
from typing import Any
from hypothesis import given, strategies as st, settings, HealthCheck

# Suppress the PytestReturnNotNoneWarning for all test functions using effect.result
pytestmark = pytest.mark.filterwarnings("ignore::pytest.PytestReturnNotNoneWarning")

# Test Data
VALID_TITLE = "Test Title"
VALID_CONTENT = "Test Content"
VALID_STYLE = "blue"
VALID_CONFIG = PanelConfig(VALID_TITLE, VALID_CONTENT, VALID_STYLE)

# Hypothesis strategies
valid_text = st.text(min_size=1, max_size=100).filter(lambda x: x.strip() != "")
valid_styles = st.sampled_from(["red", "green", "blue", "yellow", "cyan", "magenta", "white", "black"])
invalid_types = st.one_of(st.integers(), st.floats(), st.binary(), st.lists(st.integers()))

# Property-based tests
@settings(max_examples=10)
@given(title=valid_text, content=valid_text, style=valid_styles)
def test_panel_creation_properties(title: str, content: str, style: str):
    """Test panel creation with various valid inputs"""
    config = PanelConfig(title=title, content=content, style=style)
    panel = _create_panel_unsafe(config)
    assert isinstance(panel, Panel)
    assert panel.title == title
    assert panel.border_style == style

@settings(max_examples=10)
@given(
    title=st.one_of(valid_text, invalid_types),
    content=st.one_of(valid_text, invalid_types),
    style=st.one_of(valid_styles, invalid_types)
)
def test_panel_config_validation_properties(title: Any, content: Any, style: Any):
    """Test panel config validation with various input types"""
    result = create_panel_config(title, content, style)
    
    if (isinstance(title, str) and title.strip() and 
        isinstance(content, str) and content.strip() and 
        isinstance(style, str) and style.strip()):
        assert result.is_ok()
        assert isinstance(result.ok, PanelConfig)
        assert result.ok.title == title
        assert result.ok.content == content
        assert result.ok.style == style
    else:
        assert result.is_error()
        assert isinstance(result.error, DisplayError)

@settings(max_examples=10)
@given(panels=st.lists(
    st.builds(
        Panel,
        st.text(min_size=1),
        title=st.text(min_size=1),
        border_style=valid_styles
    ),
    min_size=1,
    max_size=5
))
def test_join_panels_properties(panels: list[Panel]):
    """Test panel joining with various panel combinations"""
    result = _join_panels(panels)
    assert isinstance(result, str)
    assert result != ""
    for panel in panels:
        assert str(panel.renderable) in result

@settings(max_examples=10, suppress_health_check=[HealthCheck.return_value])
@given(
    title=valid_text,
    sections=st.lists(
        st.tuples(valid_text, valid_text),
        min_size=0,
        max_size=5
    ),
    outer_style=valid_styles,
    inner_style=valid_styles
)
@effect.result[Panel, DisplayError]()
def test_nested_panel_properties(
    title: str,
    sections: list[tuple[str, str]],
    outer_style: str,
    inner_style: str
):
    """Test nested panel creation with various inputs"""
    result = yield from create_nested_panel(
        title,
        sections,
        outer_style=outer_style,
        inner_style=inner_style
    )
    assert result.is_ok()
    assert isinstance(result.ok, Panel)
    assert result.ok.title == title
    assert result.ok.border_style == outer_style

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

class MockPanel:
    def __init__(self):
        raise Exception("Mock panel creation error")

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
    result = yield from _create_inner_panel(VALID_STYLE, ("", VALID_CONTENT))
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
    sections = [
        ("Section 1", "Content 1"),
        ("Section 2", "Content 2"),
        ("Section 3", "Content 3")
    ]
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