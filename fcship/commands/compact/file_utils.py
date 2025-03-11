import fnmatch
import os

from pathlib import Path


def find_python_files(directory: Path, ignore_dirs: list[str], ignore_files: list[str]) -> list[Path]:
    """Encontra todos os arquivos Python no diretório, ignorando diretórios e arquivos com padrões especificados."""
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        # Converter o caminho para string para facilitar a comparação com padrões
        root_str = str(root)
        
        # Filtrar os diretórios usando padrões glob
        dirs_to_keep = []
        for d in dirs:
            dir_path = os.path.join(root_str, d)
            # Verificar se o diretório deve ser ignorado
            should_ignore = False
            for pattern in ignore_dirs:
                if fnmatch.fnmatch(dir_path, pattern) or fnmatch.fnmatch(d, pattern):
                    should_ignore = True
                    break
            if not should_ignore:
                dirs_to_keep.append(d)
        
        # Atualizar a lista de diretórios in-place
        dirs[:] = dirs_to_keep
        
        # Filtrar os arquivos Python usando padrões glob
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root_str, file)
                # Verificar se o arquivo deve ser ignorado
                should_ignore = False
                for pattern in ignore_files:
                    if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(file, pattern):
                        should_ignore = True
                        break
                if not should_ignore:
                    python_files.append(Path(file_path))
    
    return python_files


def get_relative_path(file_path: Path, base_dir: Path) -> str:
    """Obtém o caminho relativo de um arquivo em relação a um diretório base."""
    return os.path.relpath(file_path, base_dir)
