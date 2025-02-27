# Concorrência e Paralelismo com ROP e expression

## O Desafio da Concorrência

- Concorrência (múltiplas tarefas parecem executar ao mesmo tempo) e paralelismo (múltiplas tarefas realmente executam ao mesmo tempo) introduzem complexidade devido a potenciais condições de corrida, deadlocks e outros problemas.
- O estado mutável compartilhado é a principal fonte desses problemas.

## Princípios Funcionais para Concorrência

### Imutabilidade
Use dados imutáveis para evitar condições de corrida. Se os dados não podem ser modificados, não há risco de múltiplas threads/processos tentarem modificá-los simultaneamente.

### Isolamento de Efeitos Colaterais
Mantenha as operações que interagem com o mundo externo (I/O, estado mutável) o mais isoladas possível.

### Funções Puras
Use funções puras sempre que possível. Funções puras são thread-safe por natureza, pois não dependem de estado externo.

## Abordagens com expression e ROP

### MailboxProcessor (Concorrência)

MailboxProcessor é um ator (actor) assíncrono que permite enviar e receber mensagens entre diferentes partes do seu programa. Ele encapsula o estado e a lógica de processamento em um único lugar, evitando a necessidade de bloqueios (locks) e outras primitivas de sincronização.

#### Como usar com ROP
O MailboxProcessor pode receber mensagens que contêm dados e funções a serem executadas. Essas funções podem retornar Result, permitindo que você aplique os princípios do ROP dentro do ator.

#### Exemplo

```python
import asyncio
from expression import MailboxProcessor, Ok, Error

async def worker(inbox):
    while True:
        msg = await inbox.receive()
        if msg == "quit":
            break
        try:
            result = process_data(msg)  # process_data retorna Result
            print(f"Worker recebeu: {msg}, Resultado: {result}")
        except Exception as ex:
            print(f"Worker recebeu: {msg}, Erro: {ex}")

async def main():
    inbox = MailboxProcessor(worker)
    asyncio.create_task(inbox.start())

    await inbox.post("data1")
    await inbox.post("data2")
    await inbox.post("quit")

asyncio.run(main())
```

### asyncio e Funções Assíncronas (Concorrência)

asyncio permite escrever código concorrente usando async e await.

#### Como usar com ROP
Crie funções assíncronas que retornam Result. Use await para desempacotar os Results e propague os erros usando pipeline ou @effect.result.

#### Exemplo

```python
import asyncio
from expression import Result, Ok, Error, pipeline

async def fetch_data(url: str) -> Result[str, str]:
    # Simulação de chamada de rede
    await asyncio.sleep(1)
    if "example" in url:
        return Ok(f"Dados de {url}")
    else:
        return Error(f"Falha ao buscar dados de {url}")

async def process_data(data: str) -> Result[str, str]:
    # Simulação de processamento
    await asyncio.sleep(0.5)
    return Ok(data.upper())

async def main():
    fetch_and_process = pipeline(
        fetch_data,
        process_data
    )

    result1 = await fetch_and_process("http://example.com")
    result2 = await fetch_and_process("http://invalid.com")

    print(result1)
    print(result2)

asyncio.run(main())
```

### multiprocessing (Paralelismo)

multiprocessing permite executar código em múltiplos processos, aproveitando múltiplos núcleos de CPU.

#### Como usar com ROP
Divida o trabalho em tarefas independentes que podem ser executadas em paralelo. Cada tarefa deve receber dados imutáveis como entrada e retornar um Result. Use uma fila (queue) para coletar os resultados e tratar os erros.

#### Importante
A comunicação entre processos geralmente envolve serialização/desserialização, então certifique-se de que seus tipos Result e os dados que eles contêm sejam serializáveis.

#### Exemplo

```python
import multiprocessing
from expression import Result, Ok, Error
import time

def process_item(item: int) -> Result[int, str]:
    """Simula uma tarefa que pode ter sucesso ou falhar."""
    time.sleep(0.1)  # Simula trabalho
    if item % 2 == 0:
        return Ok(item * 2)
    else:
        return Error(f"Erro ao processar item: {item}")

def main():
    items = list(range(10))
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(process_item, items)

    successful_results = []
    errors = []
    for result in results:
        if isinstance(result, Ok):  # Usando isinstance para compatibilidade com multiprocessing
            successful_results.append(result.value)
        elif isinstance(result, Error):
            errors.append(result.error)

    print("Resultados de sucesso:", successful_results)
    print("Erros:", errors)

if __name__ == "__main__":
    main()
```

## Padrões Avançados

### Error Aggregation
Em cenários concorrentes, você pode querer coletar todos os erros, em vez de interromper no primeiro erro. Isso pode ser feito usando `asyncio.gather` ou `multiprocessing.Pool` e combinando os resultados em uma lista de Results.

### Circuit Breaker
Para evitar sobrecarregar serviços remotos, implemente um padrão de "circuit breaker". Se um serviço falhar repetidamente, interrompa as chamadas até que ele se recupere.

## Boas Práticas

1. **Comece Simples**: Evite concorrência/paralelismo a menos que seja realmente necessário.

2. **Priorize Imutabilidade**: Use dados imutáveis sempre que possível.

3. **Teste Exaustivamente**: Teste seu código concorrente/paralelo em diferentes condições para garantir que ele seja robusto.

4. **Monitore**: Monitore o desempenho do seu código concorrente/paralelo para identificar gargalos e problemas.

5. **Serialização**: Ao usar multiprocessing, certifique-se de que os dados que você está passando para os processos filhos são serializáveis. Tipos complexos podem precisar de tratamento especial.