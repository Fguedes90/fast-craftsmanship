from expression import Ok, Error, Result, pipe, effect
from rich.panel import Panel
from dataclasses import dataclass
from typing import List, Tuple, Callable
from fcship.tui.helpers import validate_panel_inputs
from fcship.tui.errors import DisplayError

@dataclass(frozen=True)
class PanelConfig:
    title: str
    content: str
    style: str

def create_panel_config(title: str, content: str, style: str) -> Result[PanelConfig, DisplayError]:
    """Factory function que retorna um Result contendo o PanelConfig ou erro."""
    validation_result = validate_panel_inputs(title, content, style)
    if validation_result.is_error():
        return validation_result
    return Ok(PanelConfig(title=title, content=content, style=style))

def _create_panel_unsafe(config: PanelConfig) -> Panel:
    """Função pura que cria um Panel. Pode lançar exceção."""
    return Panel(config.content, title=config.title, border_style=config.style)

def _create_panel_safe(config: PanelConfig) -> Result[Panel, DisplayError]:
    """Versão segura da criação de Panel usando Result para tratamento de erros."""
    try:
        if not isinstance(config.title, str) or not isinstance(config.content, str) or not isinstance(config.style, str):
            return Error(DisplayError.Rendering("Invalid panel configuration: all fields must be strings", None))
        panel = _create_panel_unsafe(config)
        return Ok(panel)
    except Exception as e:
        return Error(DisplayError.Rendering(f"Failed to create panel with title '{config.title}'", e))

def _create_inner_panel(inner_style: str, section: Tuple[str, str]) -> Result[Panel, DisplayError]:
    """Cria um painel interno com estilo específico."""
    title, content = section
    return create_panel(title, content, inner_style)

def _join_panels(panels: List[Panel]) -> str:
    """Join multiple panels into a single string"""
    return "\n".join(str(panel.renderable) for panel in panels)

@effect.result[Panel, DisplayError]()
def create_panel(title: str, content: str, style: str) -> Result[Panel, DisplayError]:
    """
    Cria um painel com título, conteúdo e estilo.
    Valida as entradas e trata erros de forma segura.
    """
    config_result = yield from create_panel_config(title, content, style)
    panel_result = yield from _create_panel_safe(config_result)
    return Ok(panel_result)

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
    
    # Criar painel externo
    panel_result = yield from create_panel(title, content, outer_style)
    if panel_result.is_error():
        return panel_result
    return Ok(panel_result.ok)
