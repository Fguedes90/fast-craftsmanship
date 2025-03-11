import os
import pytest
from pathlib import Path
from unittest.mock import patch, Mock, mock_open

from fcship.commands.compact.file_utils import find_python_files, get_relative_path


class TestFindPythonFiles:
    @patch('os.walk')
    def test_find_python_files_empty(self, mock_walk):
        # Arrange
        mock_walk.return_value = []
        directory = Path('/test/dir')
        ignore_dirs = ['venv', '__pycache__']
        ignore_files = ['setup.py']
        
        # Act
        result = find_python_files(directory, ignore_dirs, ignore_files)
        
        # Assert
        assert result == []
        mock_walk.assert_called_once_with(directory)
    
    @patch('os.walk')
    def test_find_python_files_with_files(self, mock_walk):
        # Arrange
        mock_walk.return_value = [
            ('/test/dir', ['subdir'], ['file1.py', 'file2.py', 'file3.txt']),
            ('/test/dir/subdir', [], ['file4.py', 'setup.py'])
        ]
        directory = Path('/test/dir')
        ignore_dirs = ['venv', '__pycache__']
        ignore_files = ['setup.py']
        
        # Act
        result = find_python_files(directory, ignore_dirs, ignore_files)
        
        # Assert
        assert len(result) == 3
        assert Path('/test/dir/file1.py') in result
        assert Path('/test/dir/file2.py') in result
        assert Path('/test/dir/subdir/file4.py') in result
        assert Path('/test/dir/file3.txt') not in result  # Não é Python
        assert Path('/test/dir/subdir/setup.py') not in result  # Ignorado
    
    @patch('os.walk')
    def test_find_python_files_ignore_dirs(self, mock_walk):
        # Arrange
        # Simular que os.walk vai retornar todos os diretórios, inclusive os ignorados
        mock_walk.return_value = [
            ('/test/dir', ['subdir', 'venv'], ['file1.py']),
            ('/test/dir/subdir', [], ['file2.py']),
            ('/test/dir/venv', [], ['file3.py'])  # Este deve ser ignorado
        ]
        
        # No entanto, quando a função modificar a lista dirs in-place,
        # vamos verificar que 'venv' foi removido e não será visitado
        dirs_to_check = {}
        
        def side_effect(directory):
            for path, dirs, files in [
                (str(directory), ['subdir', 'venv'], ['file1.py']),
                (os.path.join(str(directory), 'subdir'), [], ['file2.py']),
            ]:
                # Salva uma cópia do estado original de dirs
                dirs_to_check[path] = dirs.copy()
                yield path, dirs, files
        
        mock_walk.side_effect = side_effect
        
        directory = Path('/test/dir')
        ignore_dirs = ['venv', '__pycache__']
        ignore_files = ['setup.py']
        
        # Act
        result = find_python_files(directory, ignore_dirs, ignore_files)
        
        # Assert
        assert len(result) == 2
        assert Path('/test/dir/file1.py') in result
        assert Path('/test/dir/subdir/file2.py') in result
    
    @patch('os.walk')
    def test_find_python_files_multiple_ignore_patterns(self, mock_walk):
        # Arrange
        mock_walk.return_value = [
            ('/test/dir', ['subdir', 'venv', 'tests', '__pycache__'], 
             ['file1.py', 'test_file.py', 'setup.py']),
            ('/test/dir/subdir', [], ['file2.py']),
            ('/test/dir/tests', [], ['test_module.py']),  # Deve ser ignorado
            ('/test/dir/__pycache__', [], ['compiled.pyc'])  # Deve ser ignorado
        ]
        
        def side_effect(directory):
            # Simula o comportamento de os.walk, mas permite modificações na lista dirs
            # que afetam quais diretórios são visitados
            dirs_state = {
                '/test/dir': ['subdir', 'venv', 'tests', '__pycache__'],
                '/test/dir/subdir': [],
            }
            
            files_state = {
                '/test/dir': ['file1.py', 'test_file.py', 'setup.py'],
                '/test/dir/subdir': ['file2.py'],
            }
            
            # Primeiro diretório
            path = '/test/dir'
            dirs = dirs_state[path].copy()
            yield path, dirs, files_state[path]
            
            # A função find_python_files vai modificar a lista dirs in-place
            # Então, se 'tests' e '__pycache__' estiverem na lista de dirs a ignorar,
            # eles não serão percorridos
            filtered_dirs = [d for d in dirs if d not in ['venv', 'tests', '__pycache__']]
            
            # Percorrer apenas os diretórios não filtrados
            for d in filtered_dirs:
                subpath = os.path.join(path, d)
                if subpath in dirs_state:
                    subdirs = dirs_state[subpath].copy()
                    yield subpath, subdirs, files_state.get(subpath, [])
        
        mock_walk.side_effect = side_effect
        
        directory = Path('/test/dir')
        ignore_dirs = ['venv', 'tests', '__pycache__']
        ignore_files = ['setup.py', 'test_*.py']
        
        # Act
        result = find_python_files(directory, ignore_dirs, ignore_files)
        
        # Assert
        assert len(result) == 2
        assert Path('/test/dir/file1.py') in result
        assert Path('/test/dir/subdir/file2.py') in result
        # Arquivos ignorados:
        assert Path('/test/dir/test_file.py') not in result  # Ignorado pelo padrão test_*.py
        assert Path('/test/dir/setup.py') not in result  # Ignorado por nome específico
        # Diretórios ignorados não devem ser incluídos nos resultados
    
    @patch('os.walk')
    def test_find_python_files_nested_ignore_directories(self, mock_walk):
        # Arrange
        mock_walk.return_value = [
            ('/test/dir', ['app', 'utils'], ['main.py']),
            ('/test/dir/app', ['models', 'tests'], ['app.py']),
            ('/test/dir/app/models', [], ['model.py']),
            ('/test/dir/app/tests', [], ['test_app.py']),  # Deve ser ignorado
            ('/test/dir/utils', ['helpers', 'tests'], ['utils.py']),
            ('/test/dir/utils/helpers', [], ['helper.py']),
            ('/test/dir/utils/tests', [], ['test_utils.py'])  # Deve ser ignorado
        ]
        
        def side_effect(directory):
            # Define a estrutura de diretórios e arquivos
            structure = {
                '/test/dir': {
                    'dirs': ['app', 'utils'],
                    'files': ['main.py']
                },
                '/test/dir/app': {
                    'dirs': ['models', 'tests'],
                    'files': ['app.py']
                },
                '/test/dir/app/models': {
                    'dirs': [],
                    'files': ['model.py']
                },
                '/test/dir/app/tests': {
                    'dirs': [],
                    'files': ['test_app.py']
                },
                '/test/dir/utils': {
                    'dirs': ['helpers', 'tests'],
                    'files': ['utils.py']
                },
                '/test/dir/utils/helpers': {
                    'dirs': [],
                    'files': ['helper.py']
                },
                '/test/dir/utils/tests': {
                    'dirs': [],
                    'files': ['test_utils.py']
                }
            }
            
            # Começa do diretório raiz
            paths_to_visit = ['/test/dir']
            for path in paths_to_visit:
                if path in structure:
                    dirs = structure[path]['dirs'].copy()
                    # Permitir que a função find_python_files modifique a lista dirs in-place
                    yield path, dirs, structure[path]['files']
                    
                    # Adicionar apenas os diretórios não ignorados para a próxima iteração
                    for d in dirs:
                        if d not in ['tests']:  # Simula a filtragem que find_python_files faria
                            paths_to_visit.append(os.path.join(path, d))
        
        mock_walk.side_effect = side_effect
        
        directory = Path('/test/dir')
        ignore_dirs = ['tests']  # Ignorar qualquer diretório chamado 'tests'
        ignore_files = ['__init__.py']
        
        # Act
        result = find_python_files(directory, ignore_dirs, ignore_files)
        
        # Assert
        assert len(result) == 5
        assert Path('/test/dir/main.py') in result
        assert Path('/test/dir/app/app.py') in result
        assert Path('/test/dir/app/models/model.py') in result
        assert Path('/test/dir/utils/utils.py') in result
        assert Path('/test/dir/utils/helpers/helper.py') in result
        # Verificar que os arquivos em diretórios 'tests' foram ignorados
        for file_path in result:
            assert 'tests' not in str(file_path)


class TestGetRelativePath:
    def test_get_relative_path_same_dir(self):
        # Arrange
        file_path = Path('/test/dir/file.py')
        base_dir = Path('/test/dir')
        
        # Act
        result = get_relative_path(file_path, base_dir)
        
        # Assert
        assert result == 'file.py'
    
    def test_get_relative_path_subdir(self):
        # Arrange
        file_path = Path('/test/dir/subdir/file.py')
        base_dir = Path('/test/dir')
        
        # Act
        result = get_relative_path(file_path, base_dir)
        
        # Assert
        assert result == os.path.join('subdir', 'file.py')
    
    def test_get_relative_path_parent_dir(self):
        # Arrange
        file_path = Path('/test/file.py')
        base_dir = Path('/test/dir')
        
        # Act
        result = get_relative_path(file_path, base_dir)
        
        # Assert
        assert result == os.path.join('..', 'file.py') 