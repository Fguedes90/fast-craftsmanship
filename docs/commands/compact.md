# Comando Compact

O comando `compact` do Fast Craftsmanship gera uma representação compacta do código do seu projeto, otimizada para:

1. Análise por modelos de IA
2. Documentação de código
3. Entendimento rápido de projetos complexos
4. Redução do tamanho de tokens para contextos limitados

## Uso

```bash
fcship compact [OPÇÕES]
```

## Argumentos

| Argumento | Descrição |
|-----------|-----------|
| `-o, --output TEXT` | Caminho para arquivo de saída (padrão: compact_code.txt) |
| `-d, --directory TEXT` | Diretório raiz do projeto (padrão: diretório atual) |
| `-g, --guide TEXT` | Caminho para arquivo de guia de notação compacta |
| `-t, --target TEXT` | Arquivo ou diretório específico a ser processado |
| `--stdout` | Envia saída para terminal em vez de arquivo |
| `-v, --verbose` | Ativa saída detalhada |
| `--ignore-dirs TEXT` | Lista de diretórios a ignorar, separados por vírgula |
| `--ignore-files TEXT` | Lista de padrões de arquivos a ignorar, separados por vírgula |
| `--count-tokens` | Conta tokens no arquivo de saída |
| `--token-model [gpt-4o\|gpt-3.5-turbo\|claude-3-opus]` | Modelo para contagem de tokens (padrão: gpt-4o) |

## Exemplos de Uso

### Exemplo Básico

Gerar uma representação compacta do projeto atual:

```bash
fcship compact
```

Este comando:
- Analisa todos os arquivos Python no diretório atual
- Ignora diretórios padrão como `venv`, `.git`, `__pycache__`
- Gera um arquivo `compact_code.txt` no diretório atual
- Usa as configurações padrão de compactação

### Especificar Arquivo de Saída

Salvar a representação compacta em um caminho personalizado:

```bash
fcship compact -o docs/code_overview.txt
```

Este comando salva o resultado em `docs/code_overview.txt` em vez do local padrão.

### Processar Diretório Específico

Compactar apenas um subdiretório do projeto:

```bash
fcship compact -d src/core -o core_compact.txt
```

Este comando:
- Processa apenas os arquivos no diretório `src/core`
- Salva o resultado em `core_compact.txt`

### Processar Arquivo ou Módulo Específico

Compactar apenas um arquivo ou módulo específico:

```bash
fcship compact -t fcship/commands/compact/compact.py -o compact_implementation.txt
```

Este comando processa apenas o arquivo especificado, útil para análise focada.

### Personalizar Diretórios e Arquivos Ignorados

Excluir diretórios e arquivos específicos da compactação:

```bash
fcship compact --ignore-dirs="tests,examples,docs" --ignore-files="*.test.py,*_test.py" -v
```

Este comando:
- Ignora os diretórios `tests`, `examples` e `docs`
- Ignora arquivos que terminam com `.test.py` ou `_test.py`
- Usa o modo verbose para mostrar quais arquivos estão sendo processados

### Usar Guia de Notação Personalizado

Aplicar regras de compactação personalizadas:

```bash
fcship compact -g custom_notation.txt -o custom_compact.txt
```

Este comando usa as regras definidas em `custom_notation.txt` para determinar como o código será compactado.

### Contar Tokens no Resultado

Analisar o consumo de tokens do resultado:

```bash
fcship compact --count-tokens --token-model gpt-4o
```

Este comando:
- Gera a representação compacta
- Conta os tokens usando o modelo de tokenização do GPT-4o
- Exibe estatísticas sobre o consumo de tokens

### Enviar Resultado para Terminal

Visualizar o resultado diretamente no terminal:

```bash
fcship compact --stdout | less
```

Este comando envia o resultado para stdout, permitindo visualização direta ou redirecionamento para outras ferramentas.

### Combinando Múltiplas Opções

Exemplo de uso avançado combinando várias opções:

```bash
fcship compact -d src -t core/models -o docs/models_overview.txt --ignore-files="*.bak.py" --verbose --count-tokens
```

Este comando:
- Processa apenas os arquivos em `src/core/models`
- Ignora arquivos de backup (`.bak.py`)
- Salva o resultado em `docs/models_overview.txt`
- Mostra informações detalhadas durante o processamento
- Conta e exibe estatísticas de tokens ao finalizar

## Como Funciona

O comando `compact` analisa os arquivos Python do seu projeto e gera uma representação simplificada que:

1. Remove comentários e docstrings não essenciais
2. Simplifica estruturas de código complexas
3. Mantém apenas a informação essencial sobre classes, funções e suas assinaturas
4. Preserva a estrutura do projeto e relacionamentos entre módulos
5. Adiciona anotações para entendimento rápido

## Usos Comuns

### Documentação de Arquitetura

O resultado pode ser incluído em documentação para fornecer uma visão geral da estrutura do código.

### Consulta a IA

A representação compacta é ideal para enviar a modelos de IA para análise, permitindo incluir mais código dentro do limite de tokens.

### Onboarding de Desenvolvedores

Ajuda novos desenvolvedores a entender rapidamente a estrutura do projeto sem precisar analisar cada arquivo individualmente.

### Otimização para Contextos Limitados

Quando trabalhando com modelos de IA que têm limites de contexto, a versão compacta permite incluir mais funcionalidades do projeto na mesma consulta.

## Guia de Notação Personalizado

Você pode criar seu próprio guia de notação com o argumento `-g`:

```bash
fcship compact -g minha_notacao.txt
```

Um guia de notação típico define regras para compactação, como:
- Quais elementos de código manter
- Como representar herança e relacionamentos
- Quais detalhes de implementação omitir
- Estilos específicos de anotação

## Fluxo de Trabalho Recomendado

1. Gere uma versão compacta do projeto inteiro:
   ```bash
   fcship compact -o docs/project_overview.txt
   ```

2. Gere versões específicas para módulos principais:
   ```bash
   fcship compact -t src/core -o docs/core_modules.txt
   fcship compact -t src/api -o docs/api_modules.txt
   ```

3. Inclua as versões compactas na documentação do projeto para referência rápida.

4. Atualize as versões compactas antes de releases importantes para manter a documentação sincronizada.

## Dicas e Boas Práticas

1. Use `--verbose` para ver quais arquivos estão sendo processados e identificar problemas
2. Experimente com diferentes modelos de tokenização se estiver otimizando para um modelo específico
3. Combine com `--stdout` e ferramentas de filtragem para análise mais avançada
4. Mantenha um guia de notação consistente para todos os projetos da equipe
5. Inclua a versão compacta no processo de CI/CD para manter a documentação atualizada 