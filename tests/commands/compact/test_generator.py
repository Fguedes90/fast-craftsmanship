import ast
import pytest
from pathlib import Path
from unittest.mock import patch, Mock, mock_open, call, MagicMock, PropertyMock
import tempfile

from fcship.commands.compact.generator import (
    read_compact_notation_guide,
    get_files_to_process,
    process_files,
    write_output,
    generate_compact_code_with_config
)


class TestReadCompactNotationGuide:
    def test_read_compact_notation_guide_success(self):
        # Arrange
        expected_content = "# Compact Notation Guide\nThis is a test guide."
        m = mock_open(read_data=expected_content)
        
        # Act/Assert
        with patch('builtins.open', m):
            result = read_compact_notation_guide('notation.txt')
            assert result == expected_content
            m.assert_called_once_with('notation.txt', encoding='utf-8')
    
    def test_read_compact_notation_guide_error(self):
        # Arrange
        m = mock_open()
        m.side_effect = Exception("Test error")
        
        # Act/Assert
        with patch('builtins.open', m):
            with patch('builtins.print') as mock_print:
                result = read_compact_notation_guide('notation.txt')
                assert result == "Guia de notação não disponível."
                mock_print.assert_called_once()
                assert "Erro ao ler o guia de notação compacta" in mock_print.call_args[0][0]


class TestGetFilesToProcess:
    @patch('fcship.commands.compact.generator.find_python_files')
    def test_get_files_to_process_no_target(self, mock_find):
        # Arrange
        mock_find.return_value = [Path('/project/file1.py'), Path('/project/file2.py')]
        project_root = '/project'
        target = None
        
        # Act
        result = get_files_to_process(
            project_root,
            target, 
            ignore_dirs=['venv'],
            ignore_files=['setup.py'],
            verbose=False
        )
        
        # Assert
        assert result == mock_find.return_value
        mock_find.assert_called_once_with(Path(project_root), ['venv'], ['setup.py'])
    
    @patch('fcship.commands.compact.generator.find_python_files')
    @patch('pathlib.Path.is_file')
    def test_get_files_to_process_target_file(self, mock_is_file, mock_find):
        # Arrange
        mock_find.return_value = [Path('/project/file1.py')]
        mock_is_file.return_value = True
        project_root = '/project'
        target = '/project/file1.py'
        
        # Act
        result = get_files_to_process(
            project_root,
            target, 
            ignore_dirs=['venv'],
            ignore_files=['setup.py'],
            verbose=False
        )
        
        # Assert
        assert result == [Path(target)]
        mock_find.assert_not_called()
        mock_is_file.assert_called_once()
    
    @patch('fcship.commands.compact.generator.find_python_files')
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.is_file')
    def test_get_files_to_process_target_dir(self, mock_is_file, mock_is_dir, mock_find):
        # Arrange
        mock_find.return_value = [
            Path('/project/subdir/file1.py'),
            Path('/project/subdir/file2.py')
        ]
        mock_is_file.return_value = False
        mock_is_dir.return_value = True
        project_root = '/project'
        target = '/project/subdir'
        
        # Act
        result = get_files_to_process(
            project_root,
            target,
            ignore_dirs=['venv'],
            ignore_files=['setup.py'],
            verbose=False
        )
        
        # Assert
        assert result == mock_find.return_value
        mock_find.assert_called_once_with(Path(target), ['venv'], ['setup.py'])
        mock_is_file.assert_called_once()
        mock_is_dir.assert_called_once()
    
    @patch('fcship.commands.compact.generator.find_python_files')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.is_dir')
    @patch('builtins.print')
    def test_get_files_to_process_invalid_target_type(self, mock_print, mock_is_dir, mock_is_file, mock_find):
        # Arrange
        project_root = '/project'
        target = '/project/not_python_file.txt'
        
        # Configurar o mock para indicar que não é um diretório nem um arquivo Python válido
        mock_is_file.return_value = True
        mock_is_dir.return_value = False
        
        # Act
        result = get_files_to_process(
            project_root,
            target, 
            ignore_dirs=['venv'],
            ignore_files=['setup.py'],
            verbose=False
        )
        
        # Assert
        assert result == []  # Deve retornar uma lista vazia
        mock_print.assert_called_once_with(f"Erro: O alvo {target} não é um arquivo Python válido ou diretório.")
        mock_find.assert_not_called()
    
    @patch('fcship.commands.compact.generator.find_python_files')
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.is_file')
    def test_get_files_to_process_with_glob_ignore_patterns(self, mock_is_file, mock_is_dir, mock_find):
        # Arrange
        mock_find.return_value = [
            Path('/project/file1.py'),
            Path('/project/file2.py')
        ]
        mock_is_file.return_value = False
        mock_is_dir.return_value = True
        project_root = '/project'
        target = '/project'
        
        # Padrões glob para ignorar todos os diretórios de teste
        ignore_dirs = ['**/tests/*', '**/test/*', 'tests/*', 'test/*', '*tests*', '*test*']
        # Padrões para ignorar arquivos de teste e configuração
        ignore_files = ['test_*.py', '*_test.py', 'conftest.py', 'setup.py']
        
        # Act
        result = get_files_to_process(
            project_root,
            target,
            ignore_dirs=ignore_dirs,
            ignore_files=ignore_files,
            verbose=True  # Teste com verbose=True para cobrir esse caminho
        )
        
        # Assert
        assert result == mock_find.return_value
        mock_find.assert_called_once_with(Path(target), ignore_dirs, ignore_files)
        mock_is_file.assert_called_once()
        mock_is_dir.assert_called_once()
    
    @patch('fcship.commands.compact.generator.find_python_files')
    @patch('os.path.exists')
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.is_file')
    def test_get_files_to_process_with_default_ignores(self, mock_is_file, mock_is_dir, mock_exists, mock_find):
        # Arrange
        from fcship.commands.compact.config import IGNORE_DIRS, IGNORE_FILES
        
        mock_find.return_value = [
            Path('/project/file1.py'),
            Path('/project/file2.py')
        ]
        mock_exists.return_value = True
        mock_is_file.return_value = False
        mock_is_dir.return_value = True
        project_root = '/project'
        target = '/project'
        
        # Act - usando os ignorados padrão do config
        result = get_files_to_process(
            project_root,
            target, 
            ignore_dirs=IGNORE_DIRS,  # Usando as constantes do módulo
            ignore_files=IGNORE_FILES,
            verbose=False
        )
        
        # Assert
        assert result == mock_find.return_value
        mock_find.assert_called_once_with(Path(target), IGNORE_DIRS, IGNORE_FILES)
        # Verificar que os padrões padrão foram usados


class TestProcessFiles:
    def test_process_files(self):
        # Vamos simplificar esse teste usando arquivos reais
        # Arrange - criar arquivos de teste temporários
        with tempfile.TemporaryDirectory() as tmpdir:
            # Criar arquivos de teste
            file1_path = Path(tmpdir) / "file1.py"
            file2_path = Path(tmpdir) / "file2.py"
            
            # Escrever conteúdo de teste
            file_content = """
class TestClass:
    def __init__(self):
        pass
        
def test_function():
    return True
"""
            with open(file1_path, "w") as f:
                f.write(file_content)
            with open(file2_path, "w") as f:
                f.write(file_content)
            
            # Act
            result, stats = process_files([file1_path, file2_path], verbose=False)
            
            # Assert
            # Verificar que temos as linhas esperadas para cada arquivo
            assert any(str(file1_path) in line for line in result)
            assert any(str(file2_path) in line for line in result)
            
            # Verificar estatísticas
            assert stats['total_classes'] == 2  # 1 por arquivo
            assert stats['total_functions'] == 2  # 1 por arquivo
            
            # Verificar linhas de código compacto (aproximadamente)
            class_lines = [line for line in result if line.startswith('C:')]
            func_lines = [line for line in result if line.startswith('F:')]
            assert len(class_lines) == 2  # 1 por arquivo
            assert len(func_lines) == 2  # 1 por arquivo
    
    @patch('builtins.open')
    @patch('builtins.print')
    def test_process_files_error(self, mock_print, mock_open):
        # Arrange
        python_files = [Path('/test/file1.py')]
        mock_open.side_effect = Exception("Test error")
        
        # Act
        result, stats = process_files(python_files, verbose=False)
        
        # Assert
        assert len(result) == 1
        assert "# Erro ao processar" in result[0]
        mock_print.assert_called_once()
        assert "Erro ao processar" in mock_print.call_args[0][0]


class TestWriteOutput:
    def test_write_output_to_file(self):
        # Arrange
        all_compact_lines = ["# Arquivo: file1.py", "C:TestClass", "F:test_function()"]
        output_file = 'output.txt'
        stats = {
            'total_classes': 1,
            'total_functions': 1,
            'total_methods': 0,
            'total_enums': 0
        }
        
        # Act
        with patch('builtins.open', mock_open()) as m:
            with patch('builtins.print') as mock_print:
                write_output(all_compact_lines, output_file, False, False, stats)
        
        # Assert
        m.assert_called_once_with(output_file, 'w', encoding='utf-8')
        m().write.assert_called_once_with('\n'.join(all_compact_lines))
        assert mock_print.call_count >= 5  # Várias chamadas para imprimir estatísticas
    
    def test_write_output_to_stdout(self):
        # Arrange
        all_compact_lines = ["# Arquivo: file1.py", "C:TestClass", "F:test_function()"]
        output_file = 'output.txt'
        stats = {
            'total_classes': 1,
            'total_functions': 1,
            'total_methods': 0,
            'total_enums': 0
        }
        
        # Act
        with patch('builtins.open', mock_open()) as m:
            with patch('builtins.print') as mock_print:
                write_output(all_compact_lines, output_file, True, False, stats)
        
        # Assert
        m.assert_not_called()  # Não deve chamar open
        mock_print.assert_any_call('\n'.join(all_compact_lines))
        assert mock_print.call_count >= 6  # Uma chamada adicional para os compact_lines
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_write_output_to_file_verbose(self, mock_print, mock_file_open):
        # Arrange
        all_compact_lines = ["# Arquivo: file1.py", "C:TestClass", "F:test_function()"]
        output_file = 'output.txt'
        stats = {
            'total_classes': 1,
            'total_functions': 1,
            'total_methods': 0,
            'total_enums': 0
        }
        
        # Act
        write_output(all_compact_lines, output_file, stdout=False, verbose=True, stats=stats)
        
        # Assert
        mock_file_open.assert_called_once_with(output_file, 'w', encoding='utf-8')
        mock_file_open().write.assert_called_once_with('\n'.join(all_compact_lines))
        
        # Verificar que a mensagem de sucesso foi exibida (verbose=True)
        success_message = f"\nGerado com sucesso: {output_file}"
        mock_print.assert_any_call(success_message)


class TestGenerateCompactCodeWithConfig:
    @patch('fcship.commands.compact.generator.read_compact_notation_guide')
    @patch('fcship.commands.compact.generator.get_files_to_process')
    @patch('fcship.commands.compact.generator.process_files')
    @patch('fcship.commands.compact.generator.write_output')
    def test_generate_compact_code_with_config(self, mock_write, mock_process, mock_get_files, mock_read_guide):
        # Arrange
        mock_read_guide.return_value = "# Notation Guide"
        mock_get_files.return_value = [Path('/test/file1.py')]
        mock_process.return_value = (["# Arquivo: file1.py", "C:TestClass"], {
            'total_classes': 1,
            'total_functions': 0,
            'total_methods': 0,
            'total_enums': 0
        })
        
        # Act
        generate_compact_code_with_config(
            output_file='output.txt',
            project_root='/test',
            notation_file='notation.txt',
            ignore_dirs=['venv'],
            ignore_files=['setup.py'],
            include_guide=True,
            verbose=False
        )
        
        # Assert
        mock_read_guide.assert_called_once_with('notation.txt')
        mock_get_files.assert_called_once_with('/test', None, ['venv'], ['setup.py'], False)
        mock_process.assert_called_once_with([Path('/test/file1.py')], False)
        mock_write.assert_called_once()
        
    @patch('fcship.commands.compact.generator.read_compact_notation_guide')
    @patch('fcship.commands.compact.generator.get_files_to_process')
    @patch('fcship.commands.compact.generator.process_files')
    @patch('fcship.commands.compact.generator.write_output')
    def test_generate_compact_code_with_target(self, mock_write, mock_process, mock_get_files, mock_read_guide):
        # Arrange
        mock_read_guide.return_value = "# Notation Guide"
        mock_get_files.return_value = [Path('/test/target.py')]
        mock_process.return_value = (["# Arquivo: target.py", "C:TestClass"], {
            'total_classes': 1,
            'total_functions': 0,
            'total_methods': 0,
            'total_enums': 0
        })
        
        # Act
        generate_compact_code_with_config(
            output_file='output.txt',
            project_root='/test',
            notation_file='notation.txt',
            ignore_dirs=['venv'],
            ignore_files=['setup.py'],
            include_guide=True,
            verbose=False,
            target='/test/target.py'
        )
        
        # Assert
        mock_read_guide.assert_called_once_with('notation.txt')
        mock_get_files.assert_called_once_with('/test', '/test/target.py', ['venv'], ['setup.py'], False)
        mock_process.assert_called_once_with([Path('/test/target.py')], False)
        mock_write.assert_called_once()
    
    @patch('fcship.commands.compact.generator.read_compact_notation_guide')
    @patch('fcship.commands.compact.generator.get_files_to_process')
    @patch('fcship.commands.compact.generator.process_files')
    @patch('fcship.commands.compact.generator.write_output')
    def test_generate_compact_code_return_path(self, mock_write_output, mock_process_files, mock_get_files, mock_read_guide):
        # Arrange
        output_file = '/project/output.txt'
        mock_read_guide.return_value = "Guide content"
        mock_get_files.return_value = [Path('/project/file1.py')]
        mock_process_files.return_value = (["Line 1"], {"total_classes": 1, "total_functions": 1, "total_methods": 0, "total_enums": 0})
        
        # Act
        result = generate_compact_code_with_config(
            output_file=output_file,
            project_root="/project",
            notation_file="notation.txt",
            ignore_dirs=["venv"],
            ignore_files=["setup.py"],
            include_guide=True,
            verbose=False,
            target=None,
            stdout=False
        )
        
        # Assert
        assert result == output_file  # Deve retornar o caminho do arquivo quando stdout=False
        mock_write_output.assert_called_once() 