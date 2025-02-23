from expression import effect
from rich.panel import Panel
from fcship.tui.panels import create_nested_panel
from fcship.tui.errors import DisplayError
from hypothesis import given, settings, strategies as st, HealthCheck

# Define Hypothesis strategies
valid_text = st.text(min_size=1, max_size=100).filter(lambda x: x.strip() != "")
valid_styles = st.sampled_from(["red", "green", "blue", "yellow", "cyan", "magenta", "white", "black"])

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
    # Check that the result is ok and then validate the panel
    assert result.is_ok(), f"Expected OK but got: {result.error if result.is_error() else ''}"
    panel = result.ok
    assert isinstance(panel, Panel)
    assert panel.title == title
    assert panel.border_style == outer_style
    return None 