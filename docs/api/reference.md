# API Reference

Esta página contém a referência da API gerada automaticamente a partir do código.

## Estrutura do Módulo

A documentação a seguir é gerada automaticamente a partir das docstrings do código.

## Módulo fcship

::: fcship
    options:
      show_submodules: true

## CLI Principal

::: fcship.cli
    options:
      show_source: true
      members_order: source
      heading_level: 3

## Componentes Principais

Aqui estão os principais componentes da biblioteca:

### Commands

::: fcship.commands
    options:
      heading_level: 4
      members_order: alphabetical
      show_source: true

### Utils

::: fcship.utils
    options:
      heading_level: 4
      members_order: alphabetical
      show_submodules: true

## Como Documentar seu Código

Para que sua documentação seja automaticamente gerada com mkdocstrings, siga estas diretrizes:

1. Use o estilo Google para suas docstrings:

```python
def minha_funcao(param1, param2):
    """Breve descrição da função.
    
    Descrição mais longa e detalhada se necessário. Pode incluir
    múltiplos parágrafos.
    
    Args:
        param1 (tipo): Descrição do primeiro parâmetro.
        param2 (tipo): Descrição do segundo parâmetro.
    
    Returns:
        tipo: Descrição do valor retornado.
        
    Raises:
        ExcecaoTipo: Quando e por que esta exceção é levantada.
        
    Examples:
        >>> minha_funcao(1, 2)
        3
    """
    return param1 + param2
```

2. Documente suas classes com docstrings detalhadas:

```python
class MinhaClasse:
    """Breve descrição da classe.
    
    Descrição mais longa e detalhada da classe.
    
    Attributes:
        atributo1 (tipo): Descrição do atributo.
    """
    
    def __init__(self, param):
        """Inicializa a classe.
        
        Args:
            param (tipo): Descrição do parâmetro.
        """
        self.atributo1 = param
```

Para mais informações sobre documentação, consulte a [documentação oficial do mkdocstrings](https://mkdocstrings.github.io/). 