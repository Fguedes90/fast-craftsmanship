import pytest
import asyncio
import typer
from fcship.utils.error_handling import handle_command_errors, validate_operation
from expression import Ok, Error

# Funções de teste para funções síncronas

@handle_command_errors
def successful_sync(x: int) -> int:
    return x * 2

@handle_command_errors
def failing_sync() -> int:
    # Essa função gera uma exceção para forçar o fluxo de erro.
    raise ValueError("Erro na função síncrona")

def test_successful_sync():
    # Verifica se o valor retornado é o esperado.
    assert successful_sync(5) == 10

def test_failing_sync():
    # Espera que a exceção gerada pela função decorada provoque um typer.Exit.
    with pytest.raises(typer.Exit) as excinfo:
        failing_sync()
    assert excinfo.value.code == 1

@handle_command_errors
async def successful_async(x: int) -> int:
    return x + 3

@handle_command_errors
async def failing_async() -> int:
    raise ValueError("Erro na função assíncrona")

@pytest.mark.asyncio
async def test_successful_async():
    result = await successful_async(7)
    assert result == 10

@pytest.mark.asyncio
async def test_failing_async():
    with pytest.raises(typer.Exit) as excinfo:
        await failing_async()
    assert excinfo.value.code == 1

def test_validate_operation_valida_sem_nome():
    # Quando a operação é válida e não é necessário nome.
    result = validate_operation("start", ["start", "stop"])
    # Verifica se o resultado é do tipo Ok e contém a operação.
    assert isinstance(result, Ok)
    assert result.value == "start"

def test_validate_operation_op_invalida():
    result = validate_operation("foo", ["start", "stop"])
    # Espera um Erro do typer.BadParameter.
    assert isinstance(result, Error)
    error = result.err()
    assert isinstance(error, typer.BadParameter)
    assert "Invalid operation" in str(error)

def test_validate_operation_nome_necessario_falha():
    # Se a operação requer nome e nenhum é fornecido, deve ocorrer erro.
    result = validate_operation("update", ["update", "delete"], requires_name=["update"])
    assert isinstance(result, Error)
    error = result.err()
    assert isinstance(error, typer.BadParameter)
    assert "requires a name parameter" in str(error)

def test_validate_operation_nome_necessario_sucesso():
    # Se o nome é fornecido para operação que requer, o retorno deve ser Ok.
    result = validate_operation("update", ["update", "delete"], name="minha_op", requires_name=["update"])
    assert isinstance(result, Ok)
    assert result.value == "update"
