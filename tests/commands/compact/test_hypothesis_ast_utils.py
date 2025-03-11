import ast
import pytest
from typing import Optional, List
from hypothesis import given, strategies as st

from fcship.commands.compact.ast_utils import (
    get_base_classes,
    get_base_name,
    get_parameters,
    get_return_type,
    get_type_annotation
)


# Criando estratégias personalizadas para nós AST
@st.composite
def ast_name_nodes(draw):
    """Estratégia para gerar nós AST Name."""
    name = draw(st.text(min_size=1, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')) | st.just('_')))
    return ast.Name(id=name, ctx=ast.Load())


@st.composite
def ast_class_nodes(draw):
    """Estratégia para gerar nós AST ClassDef."""
    name = draw(st.text(min_size=1, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')) | st.just('_')))
    num_bases = draw(st.integers(min_value=0, max_value=3))
    bases = [draw(ast_name_nodes()) for _ in range(num_bases)]
    
    return ast.ClassDef(
        name=name,
        bases=bases,
        keywords=[],
        body=[],
        decorator_list=[]
    )


@st.composite
def ast_argument_nodes(draw):
    """Estratégia para gerar nós AST arguments."""
    num_args = draw(st.integers(min_value=0, max_value=5))
    
    args = []
    for _ in range(num_args):
        arg_name = draw(st.text(min_size=1, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')) | st.just('_')))
        has_annotation = draw(st.booleans())
        
        if has_annotation:
            annotation = draw(ast_name_nodes())
        else:
            annotation = None
            
        args.append(ast.arg(arg=arg_name, annotation=annotation))
    
    return ast.arguments(
        posonlyargs=[],
        args=args,
        kwonlyargs=[],
        kw_defaults=[],
        defaults=[],
        vararg=None,
        kwarg=None
    )


@st.composite
def ast_return_annotation(draw):
    """Estratégia para gerar anotações de tipo de retorno."""
    has_annotation = draw(st.booleans())
    if not has_annotation:
        return None
    
    use_basic = draw(st.booleans())
    if use_basic:
        return draw(ast_name_nodes())
    else:
        # Gerar um tipo genérico (ex: List[int])
        container = draw(st.sampled_from(["List", "Dict", "Optional", "Union"]))
        inner_type = draw(ast_name_nodes())
        
        return ast.Subscript(
            value=ast.Name(id=container, ctx=ast.Load()),
            slice=inner_type,
            ctx=ast.Load()
        )


class TestHypothesisAstUtils:
    
    @given(ast_name_nodes())
    def test_get_base_name_from_name(self, node):
        # Act
        result = get_base_name(node)
        
        # Assert
        assert result == node.id
        assert isinstance(result, str)
    
    @given(st.data())
    def test_get_base_classes(self, data):
        # Arrange
        class_node = data.draw(ast_class_nodes())
        expected = ", ".join(base.id for base in class_node.bases)
        
        # Act
        result = get_base_classes(class_node)
        
        # Assert
        assert result == expected
        
        # Propriedade: se não houver bases, a string será vazia
        if not class_node.bases:
            assert result == ""
    
    @given(ast_argument_nodes())
    def test_get_parameters_properties(self, args):
        # Act
        result = get_parameters(args)
        
        # Assert
        # Propriedade: o número de vírgulas deve ser um a menos que o número de argumentos (se há argumentos)
        if args.args:
            assert result.count(", ") == len(args.args) - 1
        else:
            assert result == ""
            
        # Propriedade: se há anotações, elas devem aparecer no resultado
        for arg in args.args:
            if arg.annotation:
                # Se há anotação, o argumento deve aparecer com anotação no formato arg: tipo
                assert f"{arg.arg}: {arg.annotation.id}" in result
            else:
                # Se não há anotação, o argumento deve aparecer sem anotação
                # Mas pode haver outros argumentos com o mesmo nome e que tenham anotação
                # Então vamos verificar apenas se o argumento aparece em algum lugar
                assert arg.arg in result
    
    @given(ast_return_annotation())
    def test_get_return_type_properties(self, returns):
        # Act
        result = get_return_type(returns)
        
        # Assert
        # Propriedade: se não há anotação de retorno, a string deve ser vazia
        if returns is None:
            assert result == ""
        else:
            # Se há anotação, a string deve começar com "->"
            assert result.startswith("-> ")
            
            # Se é um nome simples, deve conter esse nome
            if isinstance(returns, ast.Name):
                assert returns.id in result
            
            # Se é um tipo subscript (genérico), deve conter o nome do container
            elif isinstance(returns, ast.Subscript):
                assert returns.value.id in result
                
                # E deve ter colchetes para os tipos internos
                assert "[" in result and "]" in result
    
    @given(st.one_of(ast_name_nodes(), ast_return_annotation()))
    def test_get_type_annotation_properties(self, annotation):
        # Act
        if annotation is not None:
            result = get_type_annotation(annotation)
            
            # Assert
            assert isinstance(result, str)
            
            # Propriedade: se é um nome simples, o resultado deve ser exatamente esse nome
            if isinstance(annotation, ast.Name):
                assert result == annotation.id
                
            # Propriedade: se é um tipo subscript, deve conter colchetes e o nome do container
            elif isinstance(annotation, ast.Subscript):
                assert annotation.value.id in result
                assert "[" in result and "]" in result 