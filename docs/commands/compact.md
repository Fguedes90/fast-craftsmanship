# Compact Commands

Fast Craftsmanship provides commands for generating compact code representations of Python projects, useful for documentation and large language model context management.

## Overview

The `compact` command allows you to:

- Generate concise, structured representation of Python code
- Analyze token usage for large language models (LLMs)
- Create compact summaries of large codebases
- Prepare code documentation with minimal context usage

## Basic Usage

### Generate Compact Code

```bash
fcship compact
```

Generates a compact representation of all Python files in the current directory and saves it to `compact_code.txt` (default).

### Specify Output File

```bash
fcship compact --output OUTPUT_FILE
```

Generates a compact representation and saves it to the specified output file.

| Option | Description |
| ------ | ----------- |
| `-o, --output` | Output file path (default: compact_code.txt) |

### Process Specific Files or Directories

```bash
fcship compact --target PATH
```

Generates a compact representation of a specific file or directory.

| Option | Description |
| ------ | ----------- |
| `-t, --target` | Target file or directory to process |

## Advanced Options

### Customize Ignored Files and Directories

```bash
fcship compact --ignore-dirs "venv,node_modules" --ignore-files "setup.py,test_*.py"
```

Customizes which directories and files to exclude from processing.

| Option | Description |
| ------ | ----------- |
| `--ignore-dirs` | Comma-separated list of directories to ignore |
| `--ignore-files` | Comma-separated list of file patterns to ignore |

### Output to Console

```bash
fcship compact --stdout
```

Prints the compact representation to the console instead of a file.

| Option | Description |
| ------ | ----------- |
| `--stdout` | Print output to stdout instead of a file |

### Count Tokens

```bash
fcship compact --count-tokens [--token-model MODEL]
```

Counts tokens in the generated representation for LLM usage estimation.

| Option | Description |
| ------ | ----------- |
| `--count-tokens` | Count tokens in the output file |
| `--token-model` | Model to use for token counting (default: gpt-4o) |

## Command Reference

### Command Structure

```bash
fcship compact [options]
```

### Available Options

| Option | Description |
| ------ | ----------- |
| `-o, --output FILE` | Output file path (default: compact_code.txt) |
| `-d, --directory DIR` | Project root directory (default: current directory) |
| `-g, --guide FILE` | Path to compact notation guide file |
| `-t, --target PATH` | Target file or directory to process |
| `--stdout` | Print output to stdout instead of file |
| `-v, --verbose` | Enable verbose output |
| `--ignore-dirs LIST` | Comma-separated list of directories to ignore |
| `--ignore-files LIST` | Comma-separated list of file patterns to ignore |
| `--count-tokens` | Count tokens in the output file |
| `--token-model MODEL` | Model to use for token counting (gpt-4o, gpt-3.5-turbo, claude-3-opus) |

## Compact Notation Format

The generated compact code uses a specialized notation:

- **Classes**: `C:NomeClasse<Base1,Base2>`
- **Dataclasses**: `D:NomeDataclass;campo1:tipo;campo2:tipo`
- **Functions**: `F:nome_funcao(arg1:tipo,arg2)->tipo_retorno`
- **Methods**: `m:metodo(self,arg)->tipo`
- **Methods Dunder**: `d:__init__(self,arg)`
- **Constantes/Enums**: `E:CONSTANTE`

## Examples

### Basic Compact Code Generation

```bash
# Generate compact code for current project
fcship compact

# Generate compact code for a specific directory
fcship compact -t ./src

# Generate compact code for a specific file
fcship compact -t ./src/main.py
```

### Advanced Usage

```bash
# Generate compact code and count tokens for GPT-4o
fcship compact --count-tokens --token-model gpt-4o

# Generate compact code, excluding tests and venv directories
fcship compact --ignore-dirs "venv,tests" --output compact_no_tests.txt

# Print compact code to console for quick review
fcship compact --stdout -t ./src/core
```

### Token Analysis

```bash
# Generate compact code and analyze token usage
fcship compact --count-tokens
```

The token analysis will display:
- Total token count
- Cost estimates for different LLM models
- Context utilization percentages
- Token density metrics 