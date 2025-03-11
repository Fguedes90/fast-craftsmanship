import ast
from unittest.mock import Mock, patch

from fcship.commands.compact.ast_utils import (
    get_base_classes,
    get_base_name,
    get_parameters,
    get_return_type,
    get_type_annotation
)


class TestGetBaseName:
    def test_get_base_name_from_name(self):
        # Arrange
        node = ast.Name(id='BaseClass', ctx=ast.Load())
        
        # Act
        result = get_base_name(node)
        
        # Assert
        assert result == 'BaseClass'
    
    def test_get_base_name_unknown(self):
        # Arrange
        node = ast.Constant(value=123)
        
        # Act
        result = get_base_name(node)
        
        # Assert
        assert result == 'Unknown'


class TestGetBaseClasses:
    def test_get_base_classes_empty(self):
        # Arrange
        node = ast.ClassDef(
            name='TestClass',
            bases=[],
            keywords=[],
            body=[],
            decorator_list=[]
        )
        
        # Act
        result = get_base_classes(node)
        
        # Assert
        assert result == ''
    
    def test_get_base_classes_single(self):
        # Arrange
        node = ast.ClassDef(
            name='TestClass',
            bases=[ast.Name(id='BaseClass', ctx=ast.Load())],
            keywords=[],
            body=[],
            decorator_list=[]
        )
        
        # Act
        result = get_base_classes(node)
        
        # Assert
        assert result == 'BaseClass'
    
    def test_get_base_classes_multiple(self):
        # Arrange
        node = ast.ClassDef(
            name='TestClass',
            bases=[
                ast.Name(id='Base1', ctx=ast.Load()),
                ast.Name(id='Base2', ctx=ast.Load())
            ],
            keywords=[],
            body=[],
            decorator_list=[]
        )
        
        # Act
        result = get_base_classes(node)
        
        # Assert
        assert result == 'Base1, Base2'


class TestGetParameters:
    def test_get_parameters_empty(self):
        # Arrange
        args = Mock(spec=ast.arguments)
        args.args = []
        args.defaults = []
        
        # Act
        result = get_parameters(args)
        
        # Assert
        assert result == ''
    
    def test_get_parameters_simple(self):
        # Arrange
        args = Mock(spec=ast.arguments)
        arg1 = Mock(spec=ast.arg)
        arg1.arg = 'param1'
        arg1.annotation = None
        args.args = [arg1]
        args.defaults = []
        
        # Act
        result = get_parameters(args)
        
        # Assert
        assert result == 'param1'
    
    def test_get_parameters_multiple(self):
        # Arrange
        args = Mock(spec=ast.arguments)
        arg1 = Mock(spec=ast.arg)
        arg1.arg = 'param1'
        arg1.annotation = None
        arg2 = Mock(spec=ast.arg)
        arg2.arg = 'param2'
        arg2.annotation = None
        args.args = [arg1, arg2]
        args.defaults = []
        
        # Act
        result = get_parameters(args)
        
        # Assert
        assert result == 'param1, param2'
    
    def test_get_parameters_with_annotations(self):
        # Arrange
        args = Mock(spec=ast.arguments)
        arg1 = Mock(spec=ast.arg)
        arg1.arg = 'param1'
        arg1.annotation = Mock(spec=ast.Name)
        arg1.annotation.id = 'int'
        arg2 = Mock(spec=ast.arg)
        arg2.arg = 'param2'
        arg2.annotation = Mock(spec=ast.Name)
        arg2.annotation.id = 'str'
        args.args = [arg1, arg2]
        args.defaults = []
        
        # Patch get_type_annotation to return the annotation string
        with patch('fcship.commands.compact.ast_utils.get_type_annotation', side_effect=lambda x: x.id):
            # Act
            result = get_parameters(args)
        
        # Assert
        assert result == 'param1: int, param2: str'
    
    def test_get_parameters_with_default_values(self):
        # Arrange
        args = Mock(spec=ast.arguments)
        arg1 = Mock(spec=ast.arg)
        arg1.arg = 'param1'
        arg1.annotation = None
        arg2 = Mock(spec=ast.arg)
        arg2.arg = 'param2'
        arg2.annotation = None
        args.args = [arg1, arg2]
        # O segundo argumento tem um valor padrão
        args.defaults = [arg2]
        
        # Act
        result = get_parameters(args)
        
        # Assert
        assert result == 'param1, param2?'  # '?' indica valor padrão


class TestGetReturnType:
    def test_get_return_type_none(self):
        # Act
        result = get_return_type(None)
        
        # Assert
        assert result == ''
    
    def test_get_return_type_simple(self):
        # Arrange
        node = ast.Name(id='int', ctx=ast.Load())
        
        # Act
        result = get_return_type(node)
        
        # Assert
        assert result == '-> int'


class TestGetTypeAnnotation:
    def test_get_type_annotation_name(self):
        # Arrange
        node = ast.Name(id='int', ctx=ast.Load())
        
        # Act
        result = get_type_annotation(node)
        
        # Assert
        assert result == 'int'
    
    def test_get_type_annotation_subscript(self):
        # Arrange
        # Equivalent to List[int]
        node = ast.Subscript(
            value=ast.Name(id='List', ctx=ast.Load()),
            slice=ast.Name(id='int', ctx=ast.Load()),
            ctx=ast.Load()
        )
        
        # Act
        result = get_type_annotation(node)
        
        # Assert
        assert result == 'List[int]'
    
    def test_get_type_annotation_unknown(self):
        # Arrange
        node = ast.Constant(value=123)
        
        # Act
        result = get_type_annotation(node)
        
        # Assert
        assert result == 'Unknown' 