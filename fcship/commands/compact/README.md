# Compact Code Generator

Um gerador de representação compacta para código Python, útil para documentação e referência rápida.

## Funcionalidades

- Geração de representações compactas de código Python
- Análise de tokens para modelos de linguagem grandes (LLMs)
- Criação de sumários concisos de codebases grandes
- Preparação de documentação de código com uso mínimo de contexto

## Instalação

```bash
# Instalação direta do repositório
pip install -e .

# Ou via fcship
pip install fast-craftsmanship
```

## Uso

```bash
# Gerar representação compacta do código no diretório atual
fcship compact

# Especificar diretório de entrada e arquivo de saída
fcship compact -d /caminho/para/projeto -o saida.txt

# Gerar para um arquivo ou diretório específico
fcship compact -t /caminho/para/arquivo.py

# Enviar saída para o console
fcship compact --stdout

# Contar tokens no arquivo gerado
fcship compact --count-tokens

# Exibir opções
fcship compact --help
```

## Opcões Disponíveis

| Opção | Descrição |
| ----- | --------- |
| `-o, --output FILE` | Caminho do arquivo de saída (padrão: compact_code.txt) |
| `-d, --directory DIR` | Diretório raiz do projeto (padrão: diretório atual) |
| `-g, --guide FILE` | Caminho para o arquivo de guia de notação compacta |
| `-t, --target PATH` | Arquivo ou diretório específico para processar |
| `--stdout` | Imprimir saída no console em vez de arquivo |
| `-v, --verbose` | Habilitar saída detalhada |
| `--ignore-dirs LIST` | Lista separada por vírgulas de diretórios a ignorar |
| `--ignore-files LIST` | Lista separada por vírgulas de padrões de arquivos a ignorar |
| `--count-tokens` | Contar tokens no arquivo de saída |
| `--token-model MODEL` | Modelo a usar para contagem de tokens (gpt-4o, gpt-3.5-turbo, claude-3-opus) |

## Formato de Notação Compacta

A notação compacta segue um formato específico para representar:

- **Classes**: `C:NomeClasse<Base1,Base2>`
- **Dataclasses**: `D:NomeDataclass;campo1:tipo;campo2:tipo`
- **Funções**: `F:nome_funcao(arg1:tipo,arg2)->tipo_retorno`
- **Métodos**: `m:metodo(self,arg)->tipo`
- **Métodos Dunder**: `d:__init__(self,arg)`
- **Constantes/Enums**: `E:CONSTANTE`

Consulte o arquivo `compact_notation.txt` para a documentação completa.

## Exemplos

### Geração Básica

```bash
# Gerar código compacto para o projeto atual
fcship compact

# Gerar código compacto para um diretório específico
fcship compact -t ./src

# Gerar código compacto para um arquivo específico
fcship compact -t ./src/main.py
```

### Uso Avançado

```bash
# Gerar código compacto e contar tokens para GPT-4o
fcship compact --count-tokens --token-model gpt-4o

# Gerar código compacto, excluindo diretórios de testes e venv
fcship compact --ignore-dirs "venv,tests" --output compact_no_tests.txt

# Imprimir código compacto no console para revisão rápida
fcship compact --stdout -t ./src/core
```

## Licença

MIT 