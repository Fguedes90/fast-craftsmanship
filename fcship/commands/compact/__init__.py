# Módulo compact_code
# Gerador de código compacto para Python

__version__ = '1.0.0'

from .compactors import (
    get_compact_class_signature,
    get_compact_enum_signature,
    get_compact_function_signature,
    get_compact_method_signature,
)
from .config import COMPACT_NOTATION_FILE, DEFAULT_OUTPUT_FILE, IGNORE_DIRS, IGNORE_FILES
from .file_utils import find_python_files, get_relative_path
from .generator import generate_compact_code_with_config

__all__ = [
    'generate_compact_code_with_config',
    'get_compact_class_signature',
    'get_compact_function_signature',
    'get_compact_method_signature',
    'get_compact_enum_signature',
    'DEFAULT_OUTPUT_FILE',
    'IGNORE_DIRS',
    'IGNORE_FILES',
    'COMPACT_NOTATION_FILE',
    'find_python_files',
    'get_relative_path',
]
