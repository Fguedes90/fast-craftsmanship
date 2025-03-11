import ast

from pathlib import Path

from .compact_code_visitor import CompactCodeVisitor
from .compactors import (
    get_compact_class_signature,
    get_compact_enum_signature,
    get_compact_function_signature,
    get_compact_method_signature,
)
from .file_utils import find_python_files


def read_compact_notation_guide(notation_file: str) -> str:
    """Lê o guia de notação compacta do arquivo."""
    try:
        with open(notation_file, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Erro ao ler o guia de notação compacta: {e}")
        return "Guia de notação não disponível."


def get_files_to_process(project_root, target, ignore_dirs, ignore_files, verbose):
    """Determina quais arquivos processar com base no alvo especificado."""
    if target:
        target_path = Path(target)
        if target_path.is_file() and target_path.suffix == '.py':
            # Processar apenas um arquivo específico
            python_files = [target_path]
        elif target_path.is_dir():
            # Processar arquivos em um diretório específico
            python_files = find_python_files(target_path, ignore_dirs, ignore_files)
        else:
            print(f"Erro: O alvo {target} não é um arquivo Python válido ou diretório.")
            return []
    else:
        # Comportamento padrão: encontrar todos os arquivos Python no projeto
        python_files = find_python_files(Path(project_root), ignore_dirs, ignore_files)
    
    if verbose:
        print(f"Encontrados {len(python_files)} arquivos Python para processar")
    
    return python_files


def process_files(python_files, verbose):
    """Processa os arquivos Python e gera as representações compactas."""
    all_compact_lines = []
    total_classes = 0
    total_functions = 0
    total_methods = 0
    total_enums = 0

    for file_path in python_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                file_content = f.read()
            
            # Parse do arquivo e processamento dos nós
            file_ast = ast.parse(file_content)
            visitor = CompactCodeVisitor()
            visitor.visit(file_ast)

            # Adicionar cabeçalho do arquivo
            compact_lines = [f"file:{file_path}"]
            
            # Processar importações (opcional) - apenas indicar o intervalo de linhas
            if visitor.imports and visitor.import_lines:
                min_line = min(visitor.import_lines)
                max_line = max(visitor.import_lines)
                imports_line = f"imports:ln{min_line}:{max_line}"
                compact_lines.append(imports_line)

            # Criar um dicionário para mapear classes para seus métodos e enums
            class_elements = {}
            
            # Inicializar entradas para todas as classes
            for class_node in visitor.classes:
                class_elements[class_node] = {
                    'methods': [],
                    'enums': []
                }
            
            # Agrupar métodos com suas classes
            for class_node, method_node in visitor.methods:
                if class_node in class_elements:
                    class_elements[class_node]['methods'].append(method_node)
                    total_methods += 1
            
            # Agrupar enums com suas classes
            for class_node, enum_node in visitor.enums:
                if class_node in class_elements:
                    class_elements[class_node]['enums'].append(enum_node)
                    total_enums += 1
            
            # Processar classes com seus elementos aninhados
            for class_node in visitor.classes:
                is_dataclass = any(
                    isinstance(dec, ast.Name) and dec.id == 'dataclass'
                    for dec in class_node.decorator_list
                )
                class_signature = get_compact_class_signature(class_node, is_dataclass)
                
                # Obter todos os métodos e enums desta classe
                methods = class_elements[class_node]['methods']
                enums = class_elements[class_node]['enums']
                
                # Se não houver elementos aninhados, apenas adicione a classe
                if not methods and not enums:
                    # Obter informações de linha
                    start_line = class_node.lineno
                    end_line = max([node.lineno for node in class_node.body] + [start_line]) if class_node.body else start_line
                    line_info = f";ln{start_line}:{end_line}"
                    
                    compact_lines.append(f"{class_signature}{line_info}")
                else:
                    # Separar métodos dunder e métodos regulares
                    dunder_methods = [m for m in methods if m.name.startswith('__') and m.name.endswith('__')]
                    regular_methods = [m for m in methods if not (m.name.startswith('__') and m.name.endswith('__'))]
                    
                    # Gerar representações compactas para cada tipo
                    dunder_signatures = [get_compact_method_signature(method) for method in dunder_methods]
                    method_signatures = [get_compact_method_signature(method) for method in regular_methods]
                    enum_signatures = [get_compact_enum_signature(enum) for enum in enums]
                    
                    # Criar grupos de elementos
                    nested_groups = []
                    if dunder_signatures:
                        nested_groups.append(f"{','.join(dunder_signatures)}")
                    if method_signatures:
                        nested_groups.append(f"{','.join(method_signatures)}")
                    if enum_signatures:
                        nested_groups.append(f"{','.join(enum_signatures)}")
                    
                    # Obter informações de linha
                    start_line = class_node.lineno
                    all_lines = [class_node.lineno]
                    for method in methods:
                        all_lines.append(method.lineno)
                        all_lines.extend([node.lineno for node in method.body if hasattr(node, 'lineno')])
                    for enum in enums:
                        all_lines.append(enum.lineno)
                    end_line = max(all_lines) if all_lines else start_line
                    line_info = f";ln{start_line}:{end_line}"
                    
                    # Combinar tudo em uma única linha
                    compact_line = f"{class_signature}[{'|'.join(nested_groups)}]{line_info}"
                    compact_lines.append(compact_line)
                
                total_classes += 1

            # Processar funções de nível superior
            for func_node in visitor.functions:
                # Obter informações de linha
                start_line = func_node.lineno
                end_line = max([node.lineno for node in func_node.body] + [start_line]) if func_node.body else start_line
                line_info = f";ln{start_line}:{end_line}"
                
                compact_lines.append(f"{get_compact_function_signature(func_node)}{line_info}")
                total_functions += 1
            
            # Adicionar separador ao final do arquivo em vez de linha vazia
            compact_lines.append("-")

            all_compact_lines.extend(compact_lines)

        except Exception as e:
            print(f"Erro ao processar {file_path}: {e}")
            all_compact_lines.append(f"# Erro ao processar {file_path}: {e}")

    return all_compact_lines, {
        'total_classes': total_classes,
        'total_functions': total_functions,
        'total_methods': total_methods,
        'total_enums': total_enums
    }


def write_output(all_compact_lines, output_file, stdout, verbose, stats):
    """Escreve o resultado no arquivo ou envia para o console."""
    # Encontrar o índice da linha separadora
    separator_index = -1
    for i, line in enumerate(all_compact_lines):
        if line.startswith("-" * 10):  # Linha separadora começa com pelo menos 10 hífens
            separator_index = i
            break
    
    # Se não encontrou o separador, aplicar replaces a tudo
    if separator_index == -1:
        clean_lines = []
        for line in all_compact_lines:
            # Preservar espaços em linhas de comentário
            if line.startswith('#'):
                clean_lines.append(line)
            else:
                clean_lines.append(line.replace("__", "").replace(" ", ""))
    else:
        # Manter o guia original (com espaços) e modificar apenas o conteúdo compactado
        guide_lines = all_compact_lines[:separator_index+1]  # Incluir o separador
        content_lines = []
        for line in all_compact_lines[separator_index+1:]:
            if line.startswith('#'):
                content_lines.append(line)
            else:
                content_lines.append(line.replace("__", "").replace(" ", ""))
        clean_lines = guide_lines + content_lines
    
    if stdout:
        # Enviar para o console (stdout)
        print("\n".join(clean_lines))
    else:
        # Escrever no arquivo
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(clean_lines))
        if verbose:
            print(f"\nGerado com sucesso: {output_file}")

    # Exibir estatísticas
    print("\nEstatísticas:")
    print(f"- Classes/Dataclasses: {stats['total_classes']}")
    print(f"- Funções: {stats['total_functions']}")
    print(f"- Métodos: {stats['total_methods']}")
    print(f"- Enums/Constantes: {stats['total_enums']}")
    print(f"- Total de elementos: {stats['total_classes'] + stats['total_functions'] + stats['total_methods'] + stats['total_enums']}")


def generate_compact_code_with_config(
    output_file,
    project_root,
    notation_file,
    ignore_dirs,
    ignore_files,
    include_guide=True,
    verbose=False,
    target=None,
    stdout=False
):
    """
    Gera o código compacto com base na configuração.
    
    Args:
        output_file: Caminho para o arquivo de saída
        project_root: Diretório raiz do projeto
        notation_file: Caminho para o arquivo de guia de notação
        ignore_dirs: Lista de padrões de diretórios a serem ignorados
        ignore_files: Lista de padrões de arquivos a serem ignorados
        include_guide: Se deve incluir o guia de notação no início
        verbose: Se deve exibir informações detalhadas
        target: Arquivo ou diretório específico a ser processado
        stdout: Se deve enviar a saída para stdout em vez de um arquivo
        
    Returns:
        str: Caminho para o arquivo de saída (None se stdout=True)
    """
    
    # Sempre incluir o guia de notação
    guide_content = read_compact_notation_guide(notation_file)
    guide_lines = guide_content.splitlines()
    
    # Obter os arquivos Python para processar
    python_files = get_files_to_process(project_root, target, ignore_dirs, ignore_files, verbose)
    
    # Processar os arquivos e gerar o conteúdo compacto
    compact_lines, stats = process_files(python_files, verbose)
    
    # Combinar o guia e o conteúdo compacto
    all_compact_lines = []
    
    # Adicionar o guia de notação
    all_compact_lines.extend(guide_lines)
    
    # Adicionar uma linha separadora simples entre o guia e o conteúdo
    all_compact_lines.append("-" * 80)
    
    # Adicionar o conteúdo compacto
    all_compact_lines.extend(compact_lines)
    
    # Escrever o resultado
    write_output(all_compact_lines, output_file, stdout, verbose, stats)
    
    # Retornar o caminho do arquivo se não estiver usando stdout
    return None if stdout else output_file


if __name__ == "__main__":
    generate_compact_code_with_config(
        output_file="compact_code.txt",
        project_root=".",
        notation_file="notation_guide.txt",
        ignore_dirs=["venv", ".git"],
        ignore_files=["__init__.py"],
        include_guide=True,
        verbose=True,
        target=None,
        stdout=False
    )
