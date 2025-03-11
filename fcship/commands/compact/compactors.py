import ast

from .ast_utils import get_base_classes, get_parameters, get_return_type


def get_compact_class_signature(class_node: ast.ClassDef, is_dataclass: bool = False) -> str:
    """Gera a assinatura compacta de uma classe."""
    prefix = 'D:' if is_dataclass else 'C:'
    bases = f'<{get_base_classes(class_node)}>' if class_node.bases else ''
    return f"{prefix}{class_node.name}{bases}"


def get_compact_function_signature(func_node: ast.FunctionDef) -> str:
    """Gera a assinatura compacta de uma função."""
    prefix = 'f:' if func_node.name.startswith('_') else 'F:'
    params = get_parameters(func_node.args)
    return_type = get_return_type(func_node.returns)
    return f"{prefix}{func_node.name}({params}){return_type}"


def get_compact_method_signature(method_node: ast.FunctionDef) -> str:
    """Gera a assinatura compacta de um método."""
    prefix = 'm:'
    if method_node.name.startswith('__') and method_node.name.endswith('__'):
        prefix = 'd:'
    params = get_parameters(method_node.args)
    return_type = get_return_type(method_node.returns)
    return f"{prefix}{method_node.name}({params}){return_type}"


def get_compact_enum_signature(enum_node: ast.Assign) -> str:
    """Gera a assinatura compacta de uma constante/enum."""
    return f"E:{enum_node.targets[0].id}"


def get_base_classes(class_node: ast.ClassDef) -> str:
    """Obtém as classes base de uma definição de classe."""
    return ', '.join(get_base_name(base) for base in class_node.bases)


def get_base_name(base_node: ast.expr) -> str:
    """Obtém o nome de uma classe base."""
    if isinstance(base_node, ast.Name):
        return base_node.id
    return 'Unknown'
