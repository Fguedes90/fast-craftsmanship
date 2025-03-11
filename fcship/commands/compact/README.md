# Compact Code Generator

Um gerador de representação compacta para código Python, útil para documentação e referência rápida.

## Instalação

```bash
# Instalação direta do repositório
pip install -e .

# Ou após publicação
pip install compact-code
```

## Uso

```bash
# Gerar representação compacta do código no diretório atual
compact-code

# Especificar diretório de entrada e arquivo de saída
compact-code -d /caminho/para/projeto -o saida.txt

# Gerar para um arquivo ou diretório específico
compact-code -t /caminho/para/arquivo.py

# Enviar saída para o console
compact-code --stdout

# Exibir opções
compact-code --help
```

## Formato de Notação Compacta

A notação compacta segue um formato específico para representar:

- **Classes**: `C:NomeClasse<Base1,Base2>`
- **Dataclasses**: `D:NomeDataclass;campo1:tipo;campo2:tipo`
- **Funções**: `F:nome_funcao(arg1:tipo,arg2)->tipo_retorno`
- **Métodos**: `m:metodo(self,arg)->tipo`
- **Métodos Dunder**: `d:__init__(self,arg)`
- **Constantes/Enums**: `E:CONSTANTE`

Consulte o arquivo `compact_notation.txt` para a documentação completa.

## Configuração

É possível personalizar:

- Diretórios e arquivos ignorados
- Formato de saída
- Arquivos específicos para processamento

## Desenvolvimento

Para contribuir:

1. Clone o repositório
2. Instale em modo desenvolvimento: `pip install -e .`
3. Execute testes: `pytest`
4. Envie um pull request

## Licença

MIT 