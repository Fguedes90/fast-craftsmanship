import ast


class CompactCodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
        self.functions = []
        self.methods = []  # Métodos dentro de classes
        self.enums = []    # Constantes/enums
        self.current_class = None  # Rastrear a classe atual durante a visita
        self.imports = []  # Importações
        self.import_lines = []  # Linhas onde os imports são definidos

    def visit_ClassDef(self, node):
        previous_class = self.current_class
        self.current_class = node
        self.classes.append(node)
        self.generic_visit(node)
        self.current_class = previous_class

    def visit_FunctionDef(self, node):
        if self.current_class:
            # Função dentro de uma classe = método
            self.methods.append((self.current_class, node))
        else:
            # Função de nível superior
            self.functions.append(node)
        self.generic_visit(node)
        
    def visit_Assign(self, node):
        # Procura por constantes/enums em nível de classe
        if self.current_class and isinstance(node.targets[0], ast.Name):
            self.enums.append((self.current_class, node))
        self.generic_visit(node)

    def visit_Import(self, node):
        self.imports.extend(node.names)
        self.import_lines.append(node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for name in node.names:
            self.imports.append((node.module, name.name, name.asname))
        self.import_lines.append(node.lineno)
        self.generic_visit(node)
