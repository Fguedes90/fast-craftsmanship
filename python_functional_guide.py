# Python Functional Guide
#
# Este guia apresenta exemplos de como desenvolver com uma abordagem funcional
# que é facilmente testável e legível. Para cada conceito, são apresentados exemplos do
# "como NÃO fazer" e "como fazer". Utilize os conceitos da biblioteca Expression e as
# práticas funcionais recomendadas.
#
# ------------------------------------------------------------------------------
# Seção 1: Funções Puras vs. Funções Impuras
# ------------------------------------------------------------------------------
#
# NÃO FAZER: Função com efeitos colaterais (ex.: impressão) misturados com lógica.
def add_and_print(a, b):
    result = a + b
    print("Resultado (impuro):", result)
    return result

# FAZER: Função pura, sem efeitos colaterais, que apenas retorna o resultado.
def add(a, b):
    return a + b

# ------------------------------------------------------------------------------
# Seção 2: Composição Funcional com `pipe` e `compose`
# ------------------------------------------------------------------------------
from expression import pipe, compose, Ok, Error, Try

# NÃO FAZER: Chamadas de funções aninhadas difíceis de ler.
def calculate_bad(x):
    return (lambda a: (lambda b: a + b)(x * 2))(x + 3)

# FAZER: Usando `pipe` para compor funções de forma legível.
def calculate_good(x):
    def add3(val):
        return val + 3
    def multiply2(val):
        return val * 2
    return pipe(x, add3, multiply2)

# Alternativamente, usando `compose` (composição da esquerda para a direita):
def calculate_compose(x):
    add_then_multiply = compose(lambda x: x + 3, lambda x: x * 2)
    return add_then_multiply(x)

# ------------------------------------------------------------------------------
# Seção 3: Tratamento de Erros com Try e Option
# ------------------------------------------------------------------------------
from expression import effect, option, Nothing, Some

# NÃO FAZER: Função de divisão sem tratamento de erro, que pode levantar exceção.
def divide_bad(a, b):
    return a / b  # Pode levantar ZeroDivisionError

# FAZER: Usando o decorator effect.try_ para encapsular a lógica e tratar erros.
@effect.try_[float]()
def divide(a, b):
    if b == 0:
        raise ValueError("Divisão por zero não é permitida")
    return a / b

# Exemplo com Option: Evitar o uso de None e expressar a ausência de valor.
def get_item_option(lst, index):
    try:
        return Some(lst[index])
    except IndexError:
        return Nothing

# ------------------------------------------------------------------------------
# Seção 4: Utilitários de Ordem Superior: tap e map_type
# ------------------------------------------------------------------------------
def log_side_effect(value):
    # Exemplo de efeito colateral: log (pode ser substituído por um logger real)
    print("Log:", value)

# NÃO FAZER: Misturar cálculos com efeitos colaterais.
def compute_bad(x):
    y = x * 10
    print("Computed (impuro):", y)
    return y

# FAZER: Usando a função tap para realizar efeitos colaterais sem interferir no fluxo de dados.
from fcship.fcship.utils.functional import tap
def compute_good(x):
    y = x * 10
    return tap(log_side_effect)(y)

# Exemplo para map_type:
from fcship.fcship.utils.type_utils import map_type
def transform_str(s):
    # Função de transformação que retorna um Result.
    if s:
        return Ok(s.strip().upper())
    return Error(ValueError("String vazia"))

def transform_id(value):
    # Converte o valor para string, transforma e reconverte para o tipo original.
    return map_type(transform_str, int)(value)

# ------------------------------------------------------------------------------
# Seção 5: Operações Assíncronas Funcionais
# ------------------------------------------------------------------------------
import asyncio
from fcship.fcship.utils.error_handling import handle_command_errors

# NÃO FAZER: Função assíncrona sem tratamento de erros.
async def fetch_data_bad(url):
    response = await asyncio.sleep(0.1, result=f"Dados de {url}")
    return response

# FAZER: Usando o decorator handle_command_errors para tratamento elegante de erros.
@handle_command_errors
async def fetch_data(url):
    response = await asyncio.sleep(0.1, result=f"Dados de {url}")
    return response

# ------------------------------------------------------------------------------
# Seção 6: Abordagem de Testes Funcionais
# ------------------------------------------------------------------------------
# FAZER: Escrever funções puras que são facilmente testáveis.
def pure_transform(x):
    return x * x

# Exemplo de teste básico para funções puras.
def test_pure_transform():
    assert pure_transform(3) == 9
    assert pure_transform(0) == 0

# ------------------------------------------------------------------------------
# Execução dos Exemplos
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    print("Exemplo de função pura (add):", add(3, 4))
    print("Exemplo de cálculo com pipe:", calculate_good(5))
    try:
        print("Resultado da divisão:", divide(10, 2))
    except Exception as e:
        print("Erro na divisão:", e)
    print("Exemplo de Option:", get_item_option([1, 2, 3], 1))
    print("Exemplo de composição com compose:", calculate_compose(5))
    # Executando função assíncrona com tratamento de erro:
    print("Resultado assíncrono:", asyncio.run(fetch_data("http://exemplo.com")))
    test_pure_transform()
    print("Todos os testes passaram!")
