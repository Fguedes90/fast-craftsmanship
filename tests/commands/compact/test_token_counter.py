import os
import re
import pytest
from unittest.mock import patch, mock_open, MagicMock, Mock
from pathlib import Path

from fcship.commands.compact.token_counter import (
    count_tokens,
    estimate_tokens_approx,
    estimate_cost,
    analyze_file,
    print_token_analysis
)


class TestTokenCounter:
    
    @patch('fcship.commands.compact.token_counter.tiktoken')
    @patch('fcship.commands.compact.token_counter.HAS_TIKTOKEN', True)
    def test_count_tokens_with_tiktoken(self, mock_tiktoken):
        # Arrange
        text = "Este é um texto para testar a contagem de tokens."
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = list(range(10))  # Simula 10 tokens
        mock_tiktoken.encoding_for_model.return_value = mock_encoding
        
        # Act
        result = count_tokens(text, model="gpt-4o")
        
        # Assert
        assert result == 10
        mock_tiktoken.encoding_for_model.assert_called_once_with("gpt-4o")
        mock_encoding.encode.assert_called_once_with(text)
    
    @patch('fcship.commands.compact.token_counter.tiktoken')
    @patch('fcship.commands.compact.token_counter.HAS_TIKTOKEN', True)
    def test_count_tokens_with_tiktoken_fallback(self, mock_tiktoken):
        # Arrange
        text = "Este é um texto para testar a contagem de tokens."
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = list(range(10))  # Simula 10 tokens
        mock_tiktoken.encoding_for_model.side_effect = KeyError("Modelo não encontrado")
        mock_tiktoken.get_encoding.return_value = mock_encoding
        
        # Act
        result = count_tokens(text, model="modelo-inexistente")
        
        # Assert
        assert result == 10
        mock_tiktoken.encoding_for_model.assert_called_once_with("modelo-inexistente")
        mock_tiktoken.get_encoding.assert_called_once_with("cl100k_base")
        mock_encoding.encode.assert_called_once_with(text)
    
    @patch('fcship.commands.compact.token_counter.HAS_TIKTOKEN', False)
    @patch('fcship.commands.compact.token_counter.estimate_tokens_approx')
    def test_count_tokens_without_tiktoken(self, mock_estimate):
        # Arrange
        text = "Este é um texto para testar a contagem de tokens."
        mock_estimate.return_value = 12  # Simulação da estimativa
        
        # Act
        result = count_tokens(text, model="gpt-4o")
        
        # Assert
        assert result == 12
        mock_estimate.assert_called_once_with(text)
    
    def test_estimate_tokens_approx(self):
        # Arrange
        texts = [
            "Isto é um teste simples.",  # 5 palavras, 18 caracteres sem espaços
            "Um texto maior com algumas palavras mais longas e símbolos especiais: !@#$%",  # 11 palavras, 56 caracteres sem espaços
            "a b c d e",  # 5 palavras, 5 caracteres sem espaços
            "token",  # 1 palavra, 5 caracteres
            "",  # Texto vazio
            "Texto\ncom\nquebras\nde\nlinha", # 5 palavras, 19 caracteres sem quebras
        ]
        
        # Act & Assert
        for text in texts:
            # Calcular valores esperados
            words = len(re.findall(r'\S+', text))
            chars = len(re.sub(r'\s', '', text))
            tokens_by_words = words / 0.75
            tokens_by_chars = chars / 4
            expected = int((tokens_by_words + tokens_by_chars) / 2)
            
            # Verificar resultado
            result = estimate_tokens_approx(text)
            assert result == expected, f"Falha para o texto: '{text}'"
    
    def test_estimate_cost(self):
        # Arrange
        token_counts = [100, 1000, 10000, 100000]
        
        # Act & Assert
        for num_tokens in token_counts:
            result = estimate_cost(num_tokens)
            
            # Verificar estrutura do resultado
            assert isinstance(result, dict)
            assert "gpt-4o" in result
            assert "gpt-3.5-turbo" in result
            assert "claude-3-opus" in result
            
            # Verificar cálculos para um modelo específico
            gpt4o = result["gpt-4o"]
            assert "cost_usd" in gpt4o
            assert "percentage_context" in gpt4o
            
            # Verificar se o cálculo está correto
            expected_cost = (num_tokens / 1_000_000) * 5  # $5/1M tokens para GPT-4o
            expected_percentage = (num_tokens / 128000) * 100  # Context size de 128K para GPT-4o
            
            assert gpt4o["cost_usd"] == expected_cost
            assert gpt4o["percentage_context"] == expected_percentage
    
    @patch('fcship.commands.compact.token_counter.os.path.isfile')
    @patch('fcship.commands.compact.token_counter.os.path.getsize')
    @patch('builtins.open', new_callable=mock_open, read_data="Conteúdo do arquivo para teste")
    @patch('fcship.commands.compact.token_counter.count_tokens')
    @patch('fcship.commands.compact.token_counter.estimate_cost')
    def test_analyze_file_success(self, mock_estimate_cost, mock_count_tokens, mock_file, mock_getsize, mock_isfile):
        # Arrange
        file_path = '/test/file.py'
        file_size = 1024  # 1 KB
        num_tokens = 200
        mock_isfile.return_value = True
        mock_getsize.return_value = file_size
        mock_count_tokens.return_value = num_tokens
        mock_estimate_cost.return_value = {
            "gpt-4o": {"cost_usd": 0.001, "percentage_context": 0.15}
        }
        
        # Act
        result = analyze_file(file_path, model="gpt-4o")
        
        # Assert
        assert result is not None
        assert result["file"] == "file.py"
        assert result["size_bytes"] == file_size
        assert result["size_kb"] == file_size / 1024
        assert result["size_mb"] == file_size / (1024 * 1024)
        assert result["tokens"] == num_tokens
        assert result["tokens_per_byte"] == num_tokens / file_size
        assert result["tokens_per_kb"] == num_tokens / (file_size / 1024)
        assert "using_tiktoken" in result
        assert result["model"] == "gpt-4o"
        assert result["costs"] == mock_estimate_cost.return_value
        
        # Verificar chamadas de funções
        mock_isfile.assert_called_once_with(file_path)
        mock_getsize.assert_called_once_with(file_path)
        mock_file.assert_called_once_with(file_path, encoding='utf-8')
        mock_count_tokens.assert_called_once()
        assert mock_count_tokens.call_args[0][0] == "Conteúdo do arquivo para teste"
        assert mock_count_tokens.call_args[0][1] == "gpt-4o"
        mock_estimate_cost.assert_called_once_with(num_tokens)
    
    @patch('fcship.commands.compact.token_counter.os.path.isfile')
    @patch('builtins.print')
    def test_analyze_file_nonexistent(self, mock_print, mock_isfile):
        # Arrange
        file_path = '/test/nonexistent.py'
        mock_isfile.return_value = False
        
        # Act
        result = analyze_file(file_path)
        
        # Assert
        assert result is None
        mock_print.assert_called_once()
        assert "não existe" in mock_print.call_args[0][0]
    
    @patch('builtins.print')
    def test_print_token_analysis_with_tiktoken(self, mock_print):
        # Arrange
        stats = {
            "file": "test.py",
            "size_bytes": 1024,
            "size_kb": 1,
            "size_mb": 0.001,
            "tokens": 200,
            "tokens_per_byte": 0.2,
            "tokens_per_kb": 200,
            "using_tiktoken": True,
            "model": "gpt-4o",
            "costs": {
                "gpt-4o": {"cost_usd": 0.001, "percentage_context": 0.15},
                "gpt-3.5-turbo": {"cost_usd": 0.0001, "percentage_context": 1.2}
            }
        }
        
        # Act
        print_token_analysis(stats)
        
        # Assert
        assert mock_print.call_count > 5  # Múltiplas chamadas para print
        # Verificar conteúdo das principais chamadas
        calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        joined_output = " ".join([str(call) for call in calls])
        
        assert "CONTAGEM DE TOKENS" in joined_output
        assert "test.py" in joined_output
        assert "200" in joined_output  # Número de tokens
        assert "gpt-4o" in joined_output  # Modelo
    
    @patch('builtins.print')
    def test_print_token_analysis_estimated(self, mock_print):
        # Arrange
        stats = {
            "file": "test.py",
            "size_bytes": 1024,
            "size_kb": 1,
            "size_mb": 0.001,
            "tokens": 200,
            "tokens_per_byte": 0.2,
            "tokens_per_kb": 200,
            "using_tiktoken": False,  # Sem tiktoken
            "model": "gpt-4o",
            "costs": {
                "gpt-4o": {"cost_usd": 0.001, "percentage_context": 0.15},
                "gpt-3.5-turbo": {"cost_usd": 0.0001, "percentage_context": 1.2}
            }
        }
        
        # Act
        print_token_analysis(stats)
        
        # Assert
        assert mock_print.call_count > 5  # Múltiplas chamadas para print
        # Verificar conteúdo das principais chamadas
        calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        joined_output = " ".join([str(call) for call in calls])
        
        assert "ESTIMATIVA DE TOKENS" in joined_output  # Diferente do caso com tiktoken
        assert "estimativa aproximada" in joined_output  # Aviso sobre estimativa
    
    @patch('builtins.print')
    def test_print_token_analysis_high_context_percentage(self, mock_print):
        # Arrange - Testar alertas para contexto quase cheio
        stats = {
            "file": "test.py",
            "size_bytes": 1024,
            "size_kb": 1,
            "size_mb": 0.001,
            "tokens": 200,
            "tokens_per_byte": 0.2,
            "tokens_per_kb": 200,
            "using_tiktoken": True,
            "model": "gpt-4o",
            "costs": {
                "gpt-4o": {"cost_usd": 0.001, "percentage_context": 95},  # Acima de 90%
                "gpt-3.5-turbo": {"cost_usd": 0.0001, "percentage_context": 75}  # Entre 70-90%
            }
        }
        
        # Act
        print_token_analysis(stats)
        
        # Assert
        # Verificar conteúdo das chamadas para ver alertas
        calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        joined_output = " ".join([str(call) for call in calls])
        
        assert "⚠️ 95" in joined_output  # Alerta para > 90%
        assert "⚠️ 75" in joined_output  # Alerta para > 70%
    
    @patch('builtins.print')
    def test_print_token_analysis_null_stats(self, mock_print):
        # Arrange
        stats = None
        
        # Act
        print_token_analysis(stats)
        
        # Assert
        mock_print.assert_not_called()  # Não deve imprimir nada com stats None
    
    @patch('builtins.print')
    def test_print_token_analysis_small_cost(self, mock_print):
        # Arrange - Testar formatação de custo pequeno em centavos
        stats = {
            "file": "test.py",
            "size_bytes": 100,
            "size_kb": 0.1,
            "size_mb": 0.0001,
            "tokens": 20,
            "tokens_per_byte": 0.2,
            "tokens_per_kb": 200,
            "using_tiktoken": True,
            "model": "gpt-4o",
            "costs": {
                "gpt-4o": {"cost_usd": 0.0001, "percentage_context": 0.015},  # Valor muito pequeno
            }
        }
        
        # Act
        print_token_analysis(stats)
        
        # Assert
        # Verificar formatação de custo em centavos
        calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        joined_output = " ".join([str(call) for call in calls])
        
        assert "centavos" in joined_output  # Deve mostrar o valor em centavos
    
    def test_tiktoken_import_error(self):
        """
        Este teste verifica se o módulo token_counter lida corretamente com a ausência do tiktoken.
        Em vez de tentar simular a importação, vamos apenas verificar se o código lida com ambos os casos.
        """
        # Verificar que o módulo funciona mesmo quando HAS_TIKTOKEN é False
        from fcship.commands.compact.token_counter import count_tokens, HAS_TIKTOKEN
        
        # Independentemente de tiktoken estar instalado ou não, o count_tokens deve funcionar
        text = "Este é um texto para testar a contagem de tokens."
        tokens = count_tokens(text)
        
        # O número de tokens deve ser um inteiro positivo
        assert isinstance(tokens, int)
        assert tokens > 0
        
        # Se tiktoken não estiver disponível, deve usar a estimativa aproximada
        if not HAS_TIKTOKEN:
            # Verificar que a estimativa aproximada é usada
            from fcship.commands.compact.token_counter import estimate_tokens_approx
            expected = estimate_tokens_approx(text)
            assert tokens == expected 