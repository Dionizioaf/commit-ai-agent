import re
import click
import os
import json
from pathlib import Path

CONFIG_PATH = Path.home() / '.seshat'

def validate_config():
    """Carrega e valida as configurações necessárias"""
    # Verifica provider primeiro
    provider = os.getenv('AI_PROVIDER')
    if not provider:
        raise ValueError(
            "Variável AI_PROVIDER não configurada!\n"
            "Defina no .env: AI_PROVIDER=deepseek ou AI_PROVIDER=claude"
        )

    # Verifica model primeiro
    model = os.getenv('AI_MODEL')
    if not model:
        raise ValueError(
            "Variável AI_MODEL não configurada!\n"
            "Defina no .env: AI_MODEL"
        )

    # Valida provider
    valid_providers = ['deepseek', 'claude', 'ollama']
    if provider not in valid_providers:
        raise ValueError(f"Provedor inválido: {provider}. Opções válidas: {', '.join(valid_providers)}")

    config = {
        'provider': os.getenv('AI_PROVIDER', 'deepseek'),
        'model': os.getenv('AI_MODEL')
    }
    
    # Validar chaves de API
    provider = config['provider']
    api_key = os.getenv('API_KEY')
    model = config['model']
    
    if not api_key:
        raise ValueError(
            f"API Key não encontrada para {provider}. Configure usando:\n"
            f"1. Variável de ambiente {'API_KEY'}\n"
            "2. Arquivo .env"
        )
    
    return config

def display_error(message):
    """Exibe erros formatados"""
    click.secho(f"🚨 Erro: {message}", fg='red')

def is_valid_conventional_commit(message):
    """
    Valida se a mensagem segue a especificação Conventional Commits 1.0.0.
    
    Estrutura:
    <type>[optional scope][!]: <description>
    [optional body]
    [optional footer(s)]
    
    Exemplos válidos:
    - feat: nova funcionalidade
    - fix(core): correção de bug
    - feat!: breaking change no título
    - feat(api)!: breaking change com escopo
    - chore: commit normal
      BREAKING CHANGE: breaking change no footer
    """
    # Define os tipos permitidos (não case sensitive)
    TYPES = ['feat', 'fix', 'docs', 'style', 'refactor', 
             'perf', 'test', 'chore', 'build', 'ci', 'revert']
    
    # Separa o header (primeira linha) do resto da mensagem
    parts = message.split('\n', 1)
    header = parts[0].strip()
    body_and_footer = parts[1].strip() if len(parts) > 1 else ''
    
    # Padrão para o header:
    # - tipo (obrigatório)
    # - escopo (opcional, entre parênteses)
    # - ! (opcional, para breaking changes)
    # - : e espaço (obrigatório)
    # - descrição (obrigatório)
    header_pattern = (
        r'^('  # início da string
        r'(?P<type>' + '|'.join(TYPES) + r')'  # tipo
        r'(?:\((?P<scope>[^)]+)\))?'  # escopo opcional
        r'(?P<breaking>!)?'  # breaking change opcional
        r': '  # : e espaço obrigatórios
        r'(?P<description>.+)'  # descrição
        r')$'
    )
    
    header_match = re.match(header_pattern, header, re.IGNORECASE)
    if not header_match:
        return False
        
    # Se tem corpo ou footer, verifica se há BREAKING CHANGE
    if body_and_footer:
        # Footers devem estar separados por linha em branco do corpo
        footer_pattern = r'BREAKING[ -]CHANGE: .*'
        
        # Se tem ! no header ou BREAKING CHANGE no footer, é válido
        has_breaking_change = bool(
            header_match.group('breaking') or 
            re.search(footer_pattern, body_and_footer, re.IGNORECASE)
        )
        
        # Se não tem breaking change mas tem conteúdo, é só um corpo normal
        return True
        
    return True