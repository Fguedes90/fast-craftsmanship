
Este documento contém as diretrizes obrigatórias para que o agente LLM produza código conforme os padrões e regras da nossa documentação. Devido à limitação de contexto, as informações são concisas e objetivas. Sempre siga o método único estabelecido para cada situação, utilizando as funções e classes utilitárias especificadas.

## 1. Princípios Fundamentais

### 1.1. Imutabilidade
- **Coleções Imutáveis:**
  - Utilize **Block** para coleções pequenas ou médias, criando-as com `Block.of_seq(...)`.
  - Utilize **Seq** para processamento lazy de grandes conjuntos ou fluxos infinitos.
  - Utilize **Map** para dicionários, criados com `Map.of_seq(...)`.

  **Exemplo:**
  ```python
  from expression.collections import Block, Map, seq

  numbers = Block.of_seq(range(10))
  config = Map.of_seq([("host", "localhost"), ("port", 5432)])
  large_stream = seq(range(1_000_000))
  ```

### 1.2. Funções Puras e Composição
- **Funções Puras:**
  - Todas as funções devem ser puras, sem efeitos colaterais, e devem retornar novos valores sem modificar os dados originais.
- **Composição Funcional:**
  - Utilize **pipe** para encadear transformações puras.
  
  **Exemplo:**
  ```python
  from expression import pipe

  result = pipe(
      5,
      lambda x: x + 1,
      lambda x: x * 2,
      str
  )
  # result == "12"
  ```

## 2. Tratamento de Erros e Efeitos

### 2.1. Railway-Oriented Programming
- Utilize **Result** para operações que podem falhar.
- Encadeie operações com `.bind()`, transforme valores com `.map()` e trate erros com `.map_error()`.

  **Exemplo:**
  ```python
  from expression import Result

  def safe_divide(x: float, y: float) -> Result[float, str]:
      return Result.ok(x / y) if y != 0 else Result.error("Divisão por zero")

  resultado = Result.ok(10).bind(lambda x: safe_divide(x, 2))
  ```
  
### 2.2. Efeitos e Operações Assíncronas
- Utilize **Effect** para operações com efeitos colaterais (I/O, chamadas externas, etc.).
- Converta para async com `.to_awaitable()`.

  **Exemplo:**
  ```python
  from expression import Effect
  import asyncio

  async def async_operation():
      effect = Effect.success(42)
      result = await effect.to_awaitable()
      return result
  ```

## 3. Modelagem de Dados

### 3.1. Dataclasses Imutáveis
- Utilize `@dataclass(frozen=True)` para garantir a imutabilidade dos dados.

  **Exemplo:**
  ```python
  from dataclasses import dataclass

  @dataclass(frozen=True)
  class User:
      id: str
      name: str
      age: int
  ```

### 3.2. Tagged Unions (Sum Types)
- Utilize o decorator `@tagged_union` para criar unions.
- Forneça métodos estáticos para cada variante e utilize `match()` para tratar todos os casos de forma exaustiva.

  **Exemplo:**
  ```python
  from expression import tagged_union, tag, case

  @tagged_union
  class PaymentMethod:
      tag: str = tag()
      card: tuple[str, str] = case()  # (card_number, expiry)
      bank_transfer: str = case()     # account_number

      @staticmethod
      def Card(number: str, expiry: str) -> 'PaymentMethod':
          return PaymentMethod(card=(number, expiry))

      @staticmethod
      def BankTransfer(account: str) -> 'PaymentMethod':
          return PaymentMethod(bank_transfer=account)

  def process_payment(method: PaymentMethod) -> str:
      return method.match(
          lambda Card(number, _): f"Processando cartão: {number[-4:]}",
          lambda BankTransfer(account): f"Transferência para: {account}"
      )
  ```

## 4. Integração e Utilitários

### 4.1. Funções Utilitárias
- Utilize `option_to_result(opt, "mensagem de erro")` para converter um **Option** em **Result**.
- Utilize `sequence_results(results)` para transformar uma sequência de **Result** em um **Result** da coleção.
- Utilize os decorators `@catch_errors` ou `@catch_errors_async` para encapsular blocos de código que podem lançar exceções.
- Para exibir mensagens, use `display_message(message, style)`; para logs, utilize os métodos da classe `FunctionalLogger` (ex.: `.info()`, `.error()`, `.warning()`, `.debug()`).

### 4.2. Testabilidade
- Escreva funções pequenas e focadas para facilitar testes unitários e de propriedade.
- Utilize os padrões de teste apresentados nos exemplos de **Result**, **Option** e **Block**.

  **Exemplo de Teste para Result:**
  ```python
  def test_safe_divide():
      result = safe_divide(10, 2)
      assert result.is_ok() and result.value == 5.0
      result = safe_divide(10, 0)
      assert result.is_error() and "Divisão por zero" in str(result.error)
  ```

## 5. Diretrizes Gerais

- **Não Misture Paradigmas:**  
  Use exclusivamente abordagens funcionais definidas – não combine estilos imperativos com funcionais.
- **Segurança de Tipos:**  
  Utilize type hints e funções utilitárias como `ensure_type` e `validate_operation` para garantir a integridade dos dados.
- **Operações Assíncronas:**  
  As chamadas assíncronas devem sempre envolver **Effect** com conversão via `.to_awaitable()`.
- **Consistência:**  
  Siga rigorosamente as nomenclaturas e estruturas definidas na documentação. Arquivos READ ONLY não devem ser alterados.
- **Depuração e Monitoramento de Performance:**  
  Utilize funções utilitárias como `debug()`, `memoize` e `time_execution` para facilitar a depuração e o monitoramento da performance. Certifique-se de remover ou desabilitar chamadas de debug antes de colocar o código em produção.

---

## 6. Legibilidade e Clareza

Para assegurar que o código seja de fácil entendimento e manutenção, o agente deve observar as seguintes diretrizes adicionais:
- **Quebre funções grandes:** Divida a lógica complexa em funções pequenas, reutilizáveis e com responsabilidades bem definidas.
- **Use funções nomeadas:** Evite o uso de lambdas inline; defina funções com nomes descritivos para aumentar a clareza.
- **Garanta idempotência:** Certifique-se de que funções puras retornem sempre o mesmo resultado para os mesmos argumentos.
- **Prefira operações funcionais a loops imperativos:** Utilize métodos como `map()`, `filter()` e `reduce()` em vez de loops `for` ou `while` sempre que possível.
- **Consistência na nomenclatura:** Use nomes de funções e variáveis que sejam claros e consistentes ao longo do código.
- **Evite funções lambdas aninhadas:** Atribua lambdas a variáveis antes de usá-las, evitando o aninhamento excessivo.
- **Centralize transformações de dados:** Realize as transformações iniciais no começo do fluxo de dados para melhorar a legibilidade.
- **Documente transformações complexas:** Explique detalhadamente funções e cadeias de transformação quando estas forem complexas.
- **Utilize recursão quando apropriado:** Prefira recursão para iterações que não requeiram loops imperativos.

## Conclusão

Este documento estabelece o método único e correto para cada situação:
- **Imutabilidade:** Use Block, Map e Seq.
- **Funções Puras e Composição:** Utilize pipe para encadeamento.
- **Tratamento de Erros:** Utilize Result e Option com bind, map e map_error.
- **Efeitos Assíncronos:** Use Effect e .to_awaitable().
- **Modelagem de Dados:** Use dataclasses imutáveis e tagged unions com @tagged_union.
- **Utilitários:** Use as funções e decorators como option_to_result, sequence_results, catch_errors e FunctionalLogger.

Siga este documento rigorosamente para garantir a conformidade com os padrões do projeto sem ambiguidades ou opções alternativas.
