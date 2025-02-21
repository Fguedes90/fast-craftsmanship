# Python Functional Guide: Desenvolvendo Aplicações Altamente Funcionais

Este guia demonstra como construir aplicações em Python utilizando a abordagem funcional por meio da biblioteca Expression e de nossos helpers customizados. Aqui você verá exemplos de validação, transformação de dados, manipulação de arquivos, tratamento de erros e a composição das operações em uma pipeline funcional.

---

## 1. Conceitos Básicos

- **Result & Option:** Utilizados para trabalhar com operações “seguras” sem exceções dispersas.
- **Effects:** Capturam erros e permitem compor funções sem a necessidade de blocos try/except em cada função.
- **Composition & Pipelining:** Encadeie funções de forma legível e robusta.
- **Helpers Customizados:** Funções como `lift_option`, `ensure_type`, `map_type`, e decorators de erro, que auxiliam na escrita de código funcional.

---

## 2. Exemplos Práticos

### 2.1 Validação e Transformação de Dados

Utilize os helpers de validação e transformação para compor pipelines robustos:

```python
from fcship.fcship.utils.type_utils import ensure_type, map_type
from fcship.fcship.utils/validation import validate, compose_validations
from expression import Ok, Error, Result

def validate_and_transform_age(age_input: str) -> Result[int, Exception]:
    # Converte a entrada para inteiro, garantindo que o dado esteja correto
    age = ensure_type(age_input, int, "number", lambda x: str(x).isdigit())

    # Validação: deve ser positivo e realista
    validate_positive = validate(lambda x: x > 0, "Age must be positive")
    validate_reasonable = validate(lambda x: x < 150, "Age seems unrealistic")
    validate_age = compose_validations(validate_positive, validate_reasonable)

    return validate_age(age)

# Uso exemplo:
result = validate_and_transform_age("30")
if result.is_ok():
    print(f"Idade válida: {result.ok}")
else:
    print(f"Erro: {result.error}")
```

---

### 2.2 Manipulação de Options e Levantamento para Result

Utilize `lift_option` para converter funções que retornam Option em funções que retornam Result:

```python
from fcship.fcship.utils.functional import lift_option
from expression import Some, Nothing

def get_optional_value(x: int):
    return Some(x) if x > 0 else Nothing

# Levanta a função para retornar um Result
safe_get_value = lift_option(get_optional_value)

result = safe_get_value(10)
if result.is_ok():
    print("Valor obtido:", result.ok)
else:
    print("Erro:", result.error)
```

---

### 2.3 Exibindo Mensagens na Interface (UI)

Utilize os helpers de UI para exibir mensagens no terminal com Rich:

```python
from fcship.fcship.utils.ui import success_message, error_message, format_message

# Exemplo de mensagem de sucesso
msg_result = success_message("Operação realizada com sucesso!")
if msg_result.is_ok():
    print("Mensagem exibida com sucesso.")
else:
    print(f"Erro ao exibir mensagem: {msg_result.error}")

# Exemplo de formatação de mensagem composta
formatted = format_message(["Parte 1", "Parte 2", "Detalhes adicionais"])
if formatted.is_ok():
    print("Mensagem formatada:", formatted.ok)
```

---

### 2.4 Tratamento de Erros com Decoradores

Utilize o decorator `handle_command_errors` para centralizar o tratamento de exceções:

```python
from fcship.fcship.utils.error_handling import handle_command_errors

@handle_command_errors
def perform_operation(data: int) -> int:
    # Exemplo: Falha se o dado for negativo
    if data < 0:
        raise ValueError("Data must be non-negative")
    return data * 2

try:
    print("Resultado:", perform_operation(-5))
except SystemExit:
    print("Operação terminou com erro tratado.")
```

---

### 2.5 Manipulação de Arquivos com File Creation Tracker

Utilize os helpers de file handling para criar arquivos de forma funcional e monitorada:

```python
from pathlib import Path
from fcship.fcship.utils.file_utils import create_file, FileCreationTracker
from expression import Try

# Define o caminho e conteúdo para o arquivo
file_path = Path("output") / "sample.txt"
content = "Conteúdo do arquivo gerado funcionalmente."

tracker = FileCreationTracker()

# A função create_file usa um efeito (try_) que lança exceção em caso de falha
Try.apply(lambda: create_file(file_path, content, tracker))
print("Arquivos criados:", tracker.files)
```

---

## 3. Conclusão

Ao unir os conceitos de Result, Option, Effects e a composição funcional, você pode construir pipelines robustas, mantendo o código fácil de testar, modificar e manter. Utilize estas técnicas para garantir que cada operação seja validada e que os erros sejam tratados de forma centralizada – promovendo um design mais funcional e composto.

Explore e adapte os exemplos deste guia para as necessidades do seu projeto, integrando os helpers customizados e a biblioteca Expression para escrever código verdadeiramente funcional em Python.
