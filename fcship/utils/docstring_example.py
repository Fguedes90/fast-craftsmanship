"""
Módulo de exemplo para demonstrar documentação de alta qualidade.

Este módulo contém exemplos de documentação de código seguindo
o estilo Google, que é recomendado para uso com mkdocstrings.
"""

from typing import Dict, List, Optional, Tuple, Union


class ExampleClass:
    """Classe de exemplo que demonstra documentação de alta qualidade.
    
    Esta classe serve como um exemplo de como documentar classes
    e seus métodos seguindo o estilo Google de docstrings. Isso facilita
    a geração automática de documentação com mkdocstrings.
    
    Attributes:
        name (str): O nome da instância da classe.
        value (int): Um valor numérico associado.
        options (Dict[str, str]): Opções configuráveis da classe.
    """
    
    def __init__(self, name: str, value: int = 0, options: Optional[Dict[str, str]] = None):
        """Inicializa uma nova instância da classe ExampleClass.
        
        Args:
            name: O nome a ser atribuído à instância.
            value: Um valor opcional (padrão é 0).
            options: Um dicionário opcional de opções.
        """
        self.name = name
        self.value = value
        self.options = options or {}
    
    def process_data(self, data: List[int], factor: float = 1.0) -> List[float]:
        """Processa uma lista de dados com um fator de multiplicação.
        
        Esta função demonstra como documentar um método que processa
        dados e retorna um resultado transformado.
        
        Args:
            data: Uma lista de valores inteiros para processar.
            factor: Um fator de multiplicação opcional (padrão é 1.0).
            
        Returns:
            Uma nova lista com os valores processados.
            
        Raises:
            ValueError: Se a lista de dados estiver vazia.
            
        Examples:
            >>> example = ExampleClass("test")
            >>> example.process_data([1, 2, 3], 2.0)
            [2.0, 4.0, 6.0]
        """
        if not data:
            raise ValueError("A lista de dados não pode estar vazia")
        
        return [item * factor for item in data]
    
    def get_status(self) -> Tuple[str, int]:
        """Retorna o status atual da instância.
        
        Returns:
            Uma tupla contendo o nome e o valor atual.
        """
        return (self.name, self.value)


def utility_function(input_value: Union[str, int], mode: str = "default") -> Dict[str, Union[str, int]]:
    """Função utilitária para processar um valor de entrada.
    
    Esta função demonstra como documentar uma função utilitária
    que aceita diferentes tipos de entrada e retorna um dicionário.
    
    Args:
        input_value: O valor de entrada a ser processado. Pode ser uma string ou inteiro.
        mode: O modo de processamento. Valores possíveis:
              - "default": processamento padrão
              - "uppercase": converte strings para maiúsculo
              - "double": dobra o valor de inteiros
              
    Returns:
        Um dicionário contendo o valor processado e informações adicionais.
        
    Raises:
        ValueError: Se o modo especificado não for suportado.
        TypeError: Se o tipo de entrada não for compatível com o modo.
        
    Examples:
        >>> utility_function("hello", "uppercase")
        {'result': 'HELLO', 'mode': 'uppercase', 'type': 'string'}
        >>> utility_function(5, "double")
        {'result': 10, 'mode': 'double', 'type': 'number'}
    """
    supported_modes = ["default", "uppercase", "double"]
    
    if mode not in supported_modes:
        raise ValueError(f"Modo não suportado. Use um destes: {', '.join(supported_modes)}")
    
    result = input_value
    input_type = "string" if isinstance(input_value, str) else "number"
    
    if mode == "uppercase":
        if not isinstance(input_value, str):
            raise TypeError("O modo 'uppercase' só pode ser usado com strings")
        result = input_value.upper()
    elif mode == "double":
        if not isinstance(input_value, int):
            raise TypeError("O modo 'double' só pode ser usado com números inteiros")
        result = input_value * 2
    
    return {
        "result": result,
        "mode": mode,
        "type": input_type
    } 