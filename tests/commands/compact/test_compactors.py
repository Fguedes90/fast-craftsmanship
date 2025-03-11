import ast
import pytest
from unittest.mock import patch

from fcship.commands.compact.compactors import (
    get_compact_class_signature,
    get_compact_function_signature,
    get_compact_method_signature,
    get_compact_enum_signature,
    get_base_classes,
    get_base_name
)


class TestGetCompactClassSignature:
    def test_get_compact_class_signature_no_bases(self):
        # Arrange
        class_node = ast.ClassDef(
            name='TestClass',
            bases=[],
            keywords=[],
            body=[],
            decorator_list=[]
        )
        
        # Act
        result = get_compact_class_signature(class_node)
        
        # Assert
        assert result == 'C:TestClass'
    
    def test_get_compact_class_signature_with_bases(self):
        # Arrange
        class_node = ast.ClassDef(
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
        result = get_compact_class_signature(class_node)
        
        # Assert
        assert result == 'C:TestClass<Base1, Base2>'
    
    def test_get_compact_class_signature_dataclass(self):
        # Arrange
        class_node = ast.ClassDef(
            name='TestClass',
            bases=[],
            keywords=[],
            body=[],
            decorator_list=[]
        )
        
        # Act
        result = get_compact_class_signature(class_node, is_dataclass=True)
        
        # Assert
        assert result == 'D:TestClass'


class TestGetCompactFunctionSignature:
    @patch('fcship.commands.compact.compactors.get_parameters')
    @patch('fcship.commands.compact.compactors.get_return_type')
    def test_get_compact_function_signature_public(self, mock_get_return_type, mock_get_parameters):
        # Arrange
        mock_get_parameters.return_value = 'a, b: int'
        mock_get_return_type.return_value = '-> str'
        func_node = ast.FunctionDef(
            name='test_function',
            args=ast.arguments(
                posonlyargs=[],
                args=[],
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
        
        # Act
        result = get_compact_function_signature(func_node)
        
        # Assert
        assert result == 'F:test_function(a, b: int)-> str'
        mock_get_parameters.assert_called_once_with(func_node.args)
        mock_get_return_type.assert_called_once_with(func_node.returns)
    
    @patch('fcship.commands.compact.compactors.get_parameters')
    @patch('fcship.commands.compact.compactors.get_return_type')
    def test_get_compact_function_signature_private(self, mock_get_return_type, mock_get_parameters):
        # Arrange
        mock_get_parameters.return_value = 'a, b: int'
        mock_get_return_type.return_value = '-> str'
        func_node = ast.FunctionDef(
            name='_test_function',
            args=ast.arguments(
                posonlyargs=[],
                args=[],
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
        
        # Act
        result = get_compact_function_signature(func_node)
        
        # Assert
        assert result == 'f:_test_function(a, b: int)-> str'
        mock_get_parameters.assert_called_once_with(func_node.args)
        mock_get_return_type.assert_called_once_with(func_node.returns)


class TestGetCompactMethodSignature:
    @patch('fcship.commands.compact.compactors.get_parameters')
    @patch('fcship.commands.compact.compactors.get_return_type')
    def test_get_compact_method_signature_regular(self, mock_get_return_type, mock_get_parameters):
        # Arrange
        mock_get_parameters.return_value = 'self, a: int'
        mock_get_return_type.return_value = '-> str'
        method_node = ast.FunctionDef(
            name='test_method',
            args=ast.arguments(
                posonlyargs=[],
                args=[],
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
        
        # Act
        result = get_compact_method_signature(method_node)
        
        # Assert
        assert result == 'm:test_method(self, a: int)-> str'
        mock_get_parameters.assert_called_once_with(method_node.args)
        mock_get_return_type.assert_called_once_with(method_node.returns)
    
    @patch('fcship.commands.compact.compactors.get_parameters')
    @patch('fcship.commands.compact.compactors.get_return_type')
    def test_get_compact_method_signature_dunder(self, mock_get_return_type, mock_get_parameters):
        # Arrange
        mock_get_parameters.return_value = 'self, a: int'
        mock_get_return_type.return_value = ''
        method_node = ast.FunctionDef(
            name='__init__',
            args=ast.arguments(
                posonlyargs=[],
                args=[],
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
        
        # Act
        result = get_compact_method_signature(method_node)
        
        # Assert
        assert result == 'd:__init__(self, a: int)'
        mock_get_parameters.assert_called_once_with(method_node.args)
        mock_get_return_type.assert_called_once_with(method_node.returns)


class TestGetCompactEnumSignature:
    def test_get_compact_enum_signature(self):
        # Arrange
        enum_node = ast.Assign(
            targets=[ast.Name(id='CONSTANT', ctx=ast.Store())],
            value=ast.Constant(value='value')
        )
        
        # Act
        result = get_compact_enum_signature(enum_node)
        
        # Assert
        assert result == 'E:CONSTANT' 