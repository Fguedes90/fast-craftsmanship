from typing import List, Tuple
from fcship.tui.panels import Panel, DisplayError
from fcship.tui.result import Result, Ok

def _create_panel_unsafe(config: PanelConfig) -> Panel:
    """Função pura que cria um Panel. Pode lançar exceção."""
    from importlib import import_module
    module = import_module('rich.panel')
    Panel = module.Panel
    return Panel(config.content, title=config.title, border_style=config.style)

@effect.result[Panel, DisplayError]()
def create_nested_panel(
    title: str, 
    sections: List[Tuple[str, str]], 
    outer_style: str = "blue", 
    inner_style: str = "cyan"
) -> Result[Panel, DisplayError]:
    """
    Cria um painel que contém outros painéis.
    Cada seção é transformada em um painel interno.
    """
    # Criar painéis internos
    inner_panels = []
    for section in sections:
        panel_result = yield from _create_inner_panel(inner_style, section)
        if panel_result.is_error():
            return panel_result
        inner_panels.append(panel_result.ok)
    
    # Juntar painéis em uma string
    content = _join_panels(inner_panels)
    if not content.strip():
        content = "No Content"
    
    # Criar painel externo
    panel_result = yield from create_panel(title, content, outer_style)
    if panel_result.is_error():
        return panel_result
    return Ok(panel_result.ok) 