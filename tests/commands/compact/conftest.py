import ast
import pytest
from pathlib import Path

# Fixtures compartilhadas para todos os testes

@pytest.fixture
def sample_class_node():
    """Retorna um nó AST para uma classe simples."""
    return ast.ClassDef(
        name='TestClass',
        bases=[ast.Name(id='BaseClass', ctx=ast.Load())],
        keywords=[],
        body=[],
        decorator_list=[]
    )

@pytest.fixture
def sample_function_node():
    """Retorna um nó AST para uma função simples."""
    return ast.FunctionDef(
        name='test_function',
        args=ast.arguments(
            posonlyargs=[],
            args=[
                ast.arg(arg='a', annotation=ast.Name(id='int', ctx=ast.Load())),
                ast.arg(arg='b', annotation=ast.Name(id='str', ctx=ast.Load()))
            ],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
            vararg=None,
            kwarg=None
        ),
        body=[],
        decorator_list=[],
        returns=ast.Name(id='bool', ctx=ast.Load())
    )

@pytest.fixture
def sample_method_node():
    """Retorna um nó AST para um método simples."""
    return ast.FunctionDef(
        name='test_method',
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg='self', annotation=None)],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
            vararg=None,
            kwarg=None
        ),
        body=[],
        decorator_list=[],
        returns=None
    )

@pytest.fixture
def sample_enum_node():
    """Retorna um nó AST para uma constante/enum."""
    return ast.Assign(
        targets=[ast.Name(id='CONSTANT', ctx=ast.Store())],
        value=ast.Constant(value='value')
    )

@pytest.fixture
def sample_python_code():
    """Retorna um código Python simples para testes."""
    return '''
class TestClass(BaseClass):
    """Classe de teste."""
    
    CONSTANT = "value"
    
    def __init__(self, value):
        self.value = value
    
    def test_method(self) -> bool:
        return True

def test_function(a: int, b: str = "") -> bool:
    """Função de teste."""
    return a > 0
''' 