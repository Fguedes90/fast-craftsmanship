from pathlib import Path

# Configurações padrão
DEFAULT_OUTPUT_FILE = 'compact_code.txt'
IGNORE_DIRS = ['venv', '.git', '__pycache__']
IGNORE_FILES = ['setup.py']
COMPACT_NOTATION_FILE = Path(__file__).parent / 'compact_notation.txt'
