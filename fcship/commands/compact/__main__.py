import argparse
import sys

from compact_code.cli import main
from compact_code.token_counter import analyze_file, print_token_analysis


def count_tokens_only():
    """Função para contar apenas tokens em um arquivo existente."""
    parser = argparse.ArgumentParser(description='Contagem de tokens em arquivo')
    parser.add_argument('--count-tokens', action='store_true', help='Contar tokens (necessário)')
    parser.add_argument('--file', default="../llm_repository_context.txt", help='Arquivo a analisar')
    parser.add_argument('--token-model', default='gpt-4o', help='Modelo de tokenização')
    
    args, _ = parser.parse_known_args()
    
    if args.count_tokens:
        token_stats = analyze_file(args.file, args.token_model)
        print_token_analysis(token_stats)
        return True
    
    return False


if __name__ == '__main__':
    # Se apenas a contagem de tokens foi solicitada, sem geração de arquivo
    if (len(sys.argv) > 1 and 
        '--count-tokens' in sys.argv and 
        not any(arg.startswith('-t') or arg.startswith('--target') for arg in sys.argv) and
        count_tokens_only()):
        sys.exit(0)
    
    # Caso contrário, execute o CLI principal
    main()
