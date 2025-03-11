# Guia de Documentação com mkdocstrings

Este guia explica como documentar seu código Python para gerar uma documentação excelente com o mkdocstrings.

## Estilo de Documentação

O Fast Craftsmanship usa o estilo Google para docstrings. Este estilo é bem estruturado, fácil de ler no código-fonte e é renderizado de forma excelente pelo mkdocstrings.

## Exemplos de Docstrings

### Documentação de Módulo

```python
"""
Módulo para gerenciamento de projetos.

Este módulo contém funções e classes para criação,
modificação e análise de estruturas de projetos.
"""
```

### Documentação de Classe

```python
class Project:
    """Representa um projeto gerenciado pelo Fast Craftsmanship.
    
    Esta classe encapsula todas as operações e dados relacionados
    a um projeto específico.
    
    Attributes:
        name (str): Nome do projeto.
        path (Path): Caminho no sistema de arquivos.
        config (Dict[str, Any]): Configurações do projeto.
    """
```

### Documentação de Método/Função

```python
def create_project(name: str, path: Path, template: str = "default") -> Project:
    """Cria um novo projeto a partir de um template.
    
    Args:
        name: Nome do projeto a ser criado.
        path: Diretório onde o projeto será criado.
        template: Nome do template a ser usado (padrão: "default").
        
    Returns:
        Uma instância de Project representando o projeto criado.
        
    Raises:
        ProjectError: Se o projeto já existir ou se o template for inválido.
        
    Examples:
        >>> create_project("meu-app", Path("./projetos"), "fastapi")
        Project(name="meu-app", path=Path("./projetos/meu-app"))
    """
```

## Seções de Docstrings

As docstrings no estilo Google podem incluir várias seções:

- **Args**: Descreve os parâmetros da função/método
- **Returns**: Descreve o valor de retorno
- **Raises**: Lista as exceções que podem ser lançadas
- **Attributes**: Define os atributos da classe (em docstrings de classe)
- **Examples**: Mostra exemplos de uso
- **Notes**: Informações adicionais importantes
- **Warnings**: Avisos sobre uso ou comportamento
- **Todo**: Tarefas pendentes relacionadas ao código

## Dicas para Documentação Eficaz

1. **Seja conciso na primeira linha**: A primeira linha da docstring deve ser um resumo curto e claro.

2. **Seja detalhado no restante**: Após a primeira linha, forneça uma descrição completa.

3. **Documente todos os parâmetros**: Cada parâmetro deve ter seu tipo e descrição.

4. **Inclua exemplos**: Exemplos de uso ajudam muito os usuários.

5. **Documente exceções**: Se seu código lança exceções, documente quando e por quê.

6. **Use type hints**: Combine docstrings com type hints para uma documentação ainda melhor.

## Exemplo de Uso

Aqui está um exemplo de como o mkdocstrings renderiza nossa classe de exemplo:

::: fcship.utils.docstring_example.ExampleClass
    options:
      show_source: true
      heading_level: 3

## Documentação de Função de Exemplo

::: fcship.utils.docstring_example.utility_function
    options:
      show_source: true
      heading_level: 3 