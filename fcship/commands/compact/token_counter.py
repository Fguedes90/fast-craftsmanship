"""
Módulo para contagem de tokens em arquivos de texto.
Utiliza tiktoken (biblioteca oficial da OpenAI) quando disponível,
ou uma aproximação simples se a biblioteca não estiver instalada.
"""

import os
import re

# Tentar importar tiktoken, mas continuar mesmo se falhar
HAS_TIKTOKEN = False
try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    pass


def count_tokens(text, model="gpt-4o"):
    """
    Conta tokens em um texto usando tiktoken quando disponível.
    Caso contrário, usa uma aproximação simples.
    
    Args:
        text: O texto para contar tokens
        model: O modelo de tokenização (usado apenas com tiktoken)
        
    Returns:
        int: Número de tokens
    """
    if HAS_TIKTOKEN:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print(f"Modelo {model} não encontrado. Usando cl100k_base (GPT-4, GPT-3.5).")
            encoding = tiktoken.get_encoding("cl100k_base")
            
        tokens = encoding.encode(text)
        return len(tokens)
    return estimate_tokens_approx(text)


def estimate_tokens_approx(text):
    """
    Estimativa simples de tokens baseada em palavras e caracteres.
    Esta é uma aproximação grosseira para modelos como GPT.
    
    Em média, 1 token ≈ 4 caracteres em inglês ou ≈ 0.75 palavras.
    """
    # Remover caracteres de nova linha para não contar como espaços extras
    text = text.replace('\n', ' ')
    
    # Contar palavras (sequências de caracteres separadas por espaços)
    words = len(re.findall(r'\S+', text))
    
    # Contar caracteres (excluindo espaços)
    chars = len(re.sub(r'\s', '', text))
    
    # Estimativa baseada em palavras (aproximação para inglês)
    tokens_by_words = words / 0.75
    
    # Estimativa baseada em caracteres (aproximação para inglês)
    tokens_by_chars = chars / 4
    
    # Usar a média das duas estimativas
    estimated_tokens = int((tokens_by_words + tokens_by_chars) / 2)
    
    return estimated_tokens


def estimate_cost(num_tokens):
    """
    Estima o custo de uso dos tokens com diferentes modelos.
    Valores baseados em 2024, podem desatualizar.
    """
    costs = {
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5, "context": 16385},  # $0.5/1M tokens input
        "gpt-4o": {"input": 5, "output": 15, "context": 128000},  # $5/1M tokens input
        "gpt-4": {"input": 30, "output": 60, "context": 8192},  # $30/1M tokens input
        "claude-3-opus": {"input": 15, "output": 75, "context": 200000},  # $15/1M tokens input
        "claude-3-sonnet": {"input": 3, "output": 15, "context": 180000},  # $3/1M tokens input
    }
    
    results = {}
    
    for model_name, rates in costs.items():
        input_cost = (num_tokens / 1_000_000) * rates["input"]
        context_size = rates["context"]
        percentage = (num_tokens / context_size) * 100
        
        results[model_name] = {
            "cost_usd": input_cost,
            "percentage_context": percentage
        }
            
    return results


def analyze_file(file_path, model="gpt-4o"):
    """
    Analisa um arquivo quanto ao número de tokens e custo.
    
    Args:
        file_path: Caminho para o arquivo
        model: Modelo para usar na tokenização
        
    Returns:
        dict: Estatísticas de tokens
    """
    # Validar que o arquivo existe
    if not os.path.isfile(file_path):
        print(f"Erro: O arquivo {file_path} não existe.")
        return None
    
    # Obter o tamanho do arquivo
    file_size_bytes = os.path.getsize(file_path)
    file_size_kb = file_size_bytes / 1024
    file_size_mb = file_size_kb / 1024
    
    # Ler o arquivo
    with open(file_path, encoding='utf-8') as f:
        text = f.read()
    
    # Contar tokens
    num_tokens = count_tokens(text, model)
    
    # Estimar custos
    costs = estimate_cost(num_tokens)
    
    return {
        "file": os.path.basename(file_path),
        "size_bytes": file_size_bytes,
        "size_kb": file_size_kb,
        "size_mb": file_size_mb,
        "tokens": num_tokens,
        "tokens_per_byte": num_tokens / file_size_bytes,
        "tokens_per_kb": num_tokens / file_size_kb,
        "using_tiktoken": HAS_TIKTOKEN,
        "model": model,
        "costs": costs
    }


def print_token_analysis(stats):
    """
    Imprime a análise de tokens em um formato legível.
    
    Args:
        stats: Estatísticas de tokens retornadas por analyze_file
    """
    if not stats:
        return
    
    title = "CONTAGEM DE TOKENS" if stats["using_tiktoken"] else "ESTIMATIVA DE TOKENS"
    
    print("\n" + "=" * 60)
    print(f"{title}: {stats['file']}")
    print("=" * 60)
    print(f"Tamanho do arquivo: {stats['size_bytes']:,} bytes ({stats['size_kb']:.2f} KB, {stats['size_mb']:.2f} MB)")
    
    if stats["using_tiktoken"]:
        print(f"Número de tokens ({stats['model']}): {stats['tokens']:,}")
    else:
        print(f"Número estimado de tokens: {stats['tokens']:,}")
    
    print(f"Taxa de compressão: {stats['tokens_per_byte']:.2f} tokens por byte")
    print(f"Tokens por KB: {stats['tokens_per_kb']:.2f}")
    print("-" * 60)
    print("Estimativas por modelo:")
    print("-" * 60)
    
    for model, data in stats["costs"].items():
        cost = data["cost_usd"]
        percentage = data["percentage_context"]
        
        # Formatar o custo
        cost_str = f"${cost * 100:.2f} centavos" if cost < 0.01 else f"${cost:.2f}"
            
        # Alertar para contexto muito cheio
        if percentage > 90:
            context_str = f"⚠️ {percentage:.1f}% do contexto!"
        elif percentage > 70:
            context_str = f"⚠️ {percentage:.1f}% do contexto"
        else:
            context_str = f"{percentage:.1f}% do contexto"
            
        print(f"{model}: {cost_str} ({context_str})")
    
    print("=" * 60)
    if not stats["using_tiktoken"]:
        print("NOTA: Esta é uma estimativa aproximada. Para contagem precisa, instale tiktoken.")
    print("=" * 60) 