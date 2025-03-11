import ast
import pytest
from unittest.mock import patch
from hypothesis import given, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule

from fcship.commands.compact.compactors import (
    get_compact_class_signature,
    get_compact_function_signature,
    get_compact_method_signature,
    get_compact_enum_signature
)

# Reusando as estratégias de geração de AST
from .test_hypothesis_ast_utils import (
    ast_name_nodes,
    ast_class_nodes,
    ast_argument_nodes,
    ast_return_annotation
)


@st.composite
def ast_function_nodes(draw):
    """Estratégia para gerar nós AST FunctionDef."""
    # Nome da função
    name_options = ["test_function", "_private_func", "normal_function", "helper"]
    name = draw(st.sampled_from(name_options))
    
    # Argumentos da função
    args = draw(ast_argument_nodes())
    
    # Anotação de retorno (pode ser None)
    returns = draw(st.none() | ast_return_annotation())
    
    return ast.FunctionDef(
        name=name,
        args=args,
        body=[],
        decorator_list=[],
        returns=returns
    )


@st.composite
def ast_method_nodes(draw):
    """Estratégia para gerar nós AST FunctionDef para métodos."""
    # Decidir se é um método dunder, privado ou regular
    method_type = draw(st.sampled_from(["dunder", "private", "regular"]))
    
    if method_type == "dunder":
        name_options = ["__init__", "__str__", "__repr__", "__eq__"]
        name = draw(st.sampled_from(name_options))
    elif method_type == "private":
        name_options = ["_validate", "_process", "_helper", "_calculate"]
        name = draw(st.sampled_from(name_options))
    else:
        name_options = ["get_data", "process", "validate", "calculate"]
        name = draw(st.sampled_from(name_options))
    
    # Argumentos do método (começando com self)
    args = draw(ast_argument_nodes())
    # Adicionar self como primeiro argumento se ainda não existe
    if not args.args or args.args[0].arg != "self":
        self_arg = ast.arg(arg="self", annotation=None)
        args.args.insert(0, self_arg)
    
    # Anotação de retorno (pode ser None)
    returns = draw(st.none() | ast_return_annotation())
    
    return ast.FunctionDef(
        name=name,
        args=args,
        body=[],
        decorator_list=[],
        returns=returns
    )


@st.composite
def ast_enum_nodes(draw):
    """Estratégia para gerar nós AST Assign para enums/constantes."""
    # Nome da constante (geralmente em UPPERCASE)
    name_options = ["CONSTANT", "DEFAULT_VALUE", "MAX_CONNECTIONS", "ERROR_CODE"]
    name = draw(st.sampled_from(name_options))
    
    # Valor da constante
    value_options = [
        ast.Constant(value="value"),
        ast.Constant(value=42),
        ast.Constant(value=True),
        ast.Constant(value=None)
    ]
    value = draw(st.sampled_from(value_options))
    
    return ast.Assign(
        targets=[ast.Name(id=name, ctx=ast.Store())],
        value=value
    )


class TestHypothesisCompactors:
    
    @given(st.data())
    def test_get_compact_class_signature_properties(self, data):
        # Arrange
        class_node = data.draw(ast_class_nodes())
        is_dataclass = data.draw(st.booleans())
        
        # Act
        with patch('fcship.commands.compact.compactors.get_base_classes') as mock_get_base_classes:
            # Simular o comportamento real para base_classes
            mock_get_base_classes.return_value = ", ".join(base.id for base in class_node.bases)
            
            result = get_compact_class_signature(class_node, is_dataclass)
        
        # Assert
        # Propriedade 1: Deve começar com o prefixo correto
        if is_dataclass:
            assert result.startswith("D:")
        else:
            assert result.startswith("C:")
            
        # Propriedade 2: Deve conter o nome da classe
        assert class_node.name in result
        
        # Propriedade 3: Se tem classes base, elas devem aparecer entre <>
        if class_node.bases:
            assert "<" in result and ">" in result
            
            # Todas as bases devem estar no resultado
            for base in class_node.bases:
                assert base.id in result
        else:
            # Sem bases, não deve ter <>
            assert "<" not in result and ">" not in result
    
    @given(ast_function_nodes())
    def test_get_compact_function_signature_properties(self, func_node):
        # Act
        with patch('fcship.commands.compact.compactors.get_parameters') as mock_get_params:
            with patch('fcship.commands.compact.compactors.get_return_type') as mock_get_return:
                # Simular retornos realistas
                params = ", ".join(arg.arg for arg in func_node.args.args)
                mock_get_params.return_value = params
                
                return_type = ""
                if func_node.returns and isinstance(func_node.returns, ast.Name):
                    return_type = f"-> {func_node.returns.id}"
                mock_get_return.return_value = return_type
                
                result = get_compact_function_signature(func_node)
        
        # Assert
        # Propriedade 1: Prefixo correto baseado no nome da função
        if func_node.name.startswith('_'):
            assert result.startswith("f:")
        else:
            assert result.startswith("F:")
            
        # Propriedade 2: Nome da função está presente
        assert func_node.name in result
        
        # Propriedade 3: Parâmetros estão entre parênteses
        assert "(" in result and ")" in result
        
        # Propriedade 4: Se usamos mock com tipo de retorno, ele está presente
        if return_type:
            assert "->" in result
    
    @given(ast_method_nodes())
    def test_get_compact_method_signature_properties(self, method_node):
        # Act
        with patch('fcship.commands.compact.compactors.get_parameters') as mock_get_params:
            with patch('fcship.commands.compact.compactors.get_return_type') as mock_get_return:
                # Simular retornos realistas
                params = "self" + (", " + ", ".join(arg.arg for arg in method_node.args.args[1:]) if len(method_node.args.args) > 1 else "")
                mock_get_params.return_value = params
                
                return_type = ""
                if method_node.returns and isinstance(method_node.returns, ast.Name):
                    return_type = f"-> {method_node.returns.id}"
                mock_get_return.return_value = return_type
                
                result = get_compact_method_signature(method_node)
        
        # Assert
        # Propriedade 1: Prefixo correto baseado no tipo de método
        if method_node.name.startswith('__') and method_node.name.endswith('__'):
            assert result.startswith("d:")
        else:
            assert result.startswith("m:")
            
        # Propriedade 2: Nome do método está presente
        assert method_node.name in result
        
        # Propriedade 3: Parâmetros estão entre parênteses
        assert "(" in result and ")" in result
        
        # Propriedade 4: self está nos parâmetros
        assert "self" in result
        
        # Propriedade 5: Se usamos mock com tipo de retorno, ele está presente
        if return_type:
            assert "->" in result
    
    @given(ast_enum_nodes())
    def test_get_compact_enum_signature_properties(self, enum_node):
        # Act
        result = get_compact_enum_signature(enum_node)
        
        # Assert
        # Propriedade 1: Prefixo correto
        assert result.startswith("E:")
        
        # Propriedade 2: Nome da constante está presente
        target_name = enum_node.targets[0].id
        assert target_name in result
        
        # Propriedade 3: Formato completo E:NOME
        assert result == f"E:{target_name}" 