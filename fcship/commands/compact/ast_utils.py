import ast

__all__ = [
    'get_base_classes',
    'get_base_name',
    'get_parameters',
    'get_return_type',
    'get_type_annotation',
]


def get_base_classes(class_node: ast.ClassDef) -> str:
    """Obtém as classes base de uma definição de classe."""
    return ', '.join(get_base_name(base) for base in class_node.bases)


def get_base_name(base_node: ast.expr) -> str:
    """Obtém o nome de uma classe base."""
    if isinstance(base_node, ast.Name):
        return base_node.id
    return 'Unknown'


def get_parameters(args: ast.arguments) -> str:
    """Gera a representação compacta dos parâmetros de uma função."""
    params = []
    for arg in args.args:
        param = arg.arg
        if arg.annotation:
            param += f': {get_type_annotation(arg.annotation)}'
        if arg in args.defaults:
            param += '?'
        params.append(param)
    return ', '.join(params)


def get_return_type(returns: ast.expr | None) -> str:
    """Obtém o tipo de retorno de uma função."""
    if returns is None:
        return ''
    return f'-> {get_type_annotation(returns)}'


def get_type_annotation(annotation: ast.expr) -> str:
    """Obtém a representação de uma anotação de tipo."""
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Subscript):
        return f'{annotation.value.id}[{get_type_annotation(annotation.slice)}]'
    return 'Unknown'
