import ast
import pytest

from fcship.commands.compact.compact_code_visitor import CompactCodeVisitor


class TestCompactCodeVisitor:
    def test_visit_class_def(self):
        # Arrange
        visitor = CompactCodeVisitor()
        class_node = ast.ClassDef(
            name='TestClass',
            bases=[],
            keywords=[],
            body=[],
            decorator_list=[]
        )
        
        # Act
        visitor.visit_ClassDef(class_node)
        
        # Assert
        assert len(visitor.classes) == 1
        assert visitor.classes[0] == class_node
        assert visitor.current_class is None  # Restaura o valor anterior
    
    def test_visit_function_def_top_level(self):
        # Arrange
        visitor = CompactCodeVisitor()
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
        visitor.visit_FunctionDef(func_node)
        
        # Assert
        assert len(visitor.functions) == 1
        assert visitor.functions[0] == func_node
        assert len(visitor.methods) == 0
    
    def test_visit_function_def_method(self):
        # Arrange
        visitor = CompactCodeVisitor()
        class_node = ast.ClassDef(
            name='TestClass',
            bases=[],
            keywords=[],
            body=[],
            decorator_list=[]
        )
        visitor.current_class = class_node
        
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
        visitor.visit_FunctionDef(method_node)
        
        # Assert
        assert len(visitor.functions) == 0
        assert len(visitor.methods) == 1
        assert visitor.methods[0][0] == class_node
        assert visitor.methods[0][1] == method_node
    
    def test_visit_assign_enum(self):
        # Arrange
        visitor = CompactCodeVisitor()
        class_node = ast.ClassDef(
            name='TestClass',
            bases=[],
            keywords=[],
            body=[],
            decorator_list=[]
        )
        visitor.current_class = class_node
        
        enum_node = ast.Assign(
            targets=[ast.Name(id='CONSTANT', ctx=ast.Store())],
            value=ast.Constant(value='value')
        )
        
        # Act
        visitor.visit_Assign(enum_node)
        
        # Assert
        assert len(visitor.enums) == 1
        assert visitor.enums[0][0] == class_node
        assert visitor.enums[0][1] == enum_node
    
    def test_visit_assign_not_enum(self):
        # Arrange - assignment fora de classe não é considerado enum
        visitor = CompactCodeVisitor()
        visitor.current_class = None
        
        assign_node = ast.Assign(
            targets=[ast.Name(id='variable', ctx=ast.Store())],
            value=ast.Constant(value='value')
        )
        
        # Act
        visitor.visit_Assign(assign_node)
        
        # Assert
        assert len(visitor.enums) == 0
    
    def test_visit_import(self):
        # Arrange
        visitor = CompactCodeVisitor()
        import_node = ast.Import(
            names=[
                ast.alias(name='os', asname=None),
                ast.alias(name='sys', asname=None)
            ]
        )
        import_node.lineno = 1  # Set the line number
        
        # Act
        visitor.visit_Import(import_node)
        
        # Assert
        assert len(visitor.imports) == 2
        assert visitor.imports[0].name == 'os'
        assert visitor.imports[1].name == 'sys'
        assert visitor.import_lines == [1]  # Check that the line number was recorded
    
    def test_visit_import_from(self):
        # Arrange
        visitor = CompactCodeVisitor()
        import_from_node = ast.ImportFrom(
            module='os',
            names=[
                ast.alias(name='path', asname=None),
                ast.alias(name='environ', asname='env')
            ],
            level=0
        )
        import_from_node.lineno = 2  # Set the line number
        
        # Act
        visitor.visit_ImportFrom(import_from_node)
        
        # Assert
        assert len(visitor.imports) == 2
        assert visitor.imports[0] == ('os', 'path', None)
        assert visitor.imports[1] == ('os', 'environ', 'env')
        assert visitor.import_lines == [2]  # Check that the line number was recorded
    
    def test_nested_class_visit(self):
        # Arrange - Testar o contexto correto ao visitar classes aninhadas
        source_code = """
class OuterClass:
    class InnerClass:
        def inner_method(self):
            pass

    def outer_method(self):
        pass
"""
        tree = ast.parse(source_code)
        visitor = CompactCodeVisitor()
        
        # Act
        visitor.visit(tree)
        
        # Assert
        assert len(visitor.classes) == 2  # OuterClass e InnerClass
        assert len(visitor.methods) == 2  # inner_method e outer_method
        
        # Verificar se os métodos foram associados às classes corretas
        outer_class = None
        inner_class = None
        for cls in visitor.classes:
            if cls.name == 'OuterClass':
                outer_class = cls
            elif cls.name == 'InnerClass':
                inner_class = cls
        
        outer_methods = [m[1].name for m in visitor.methods if m[0] == outer_class]
        inner_methods = [m[1].name for m in visitor.methods if m[0] == inner_class]
        
        assert 'outer_method' in outer_methods
        assert 'inner_method' in inner_methods 