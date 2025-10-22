"""
Configurações de ambiente para o sistema de compras
"""
import os

# Configurações dos ambientes
ENVIRONMENTS = {
    'DEV': {
        'name': 'Desenvolvimento',
        'database_url': os.getenv('BD_COMPRAS_DEV', 'postgresql+pg8000://user:pass@prod-host:5432/purchase_db'),
        'description': 'Ambiente de desenvolvimento'
    },
    'HOM': {
        'name': 'Homologação',
        'database_url': os.getenv('BD_COMPRAS_HOM'),
        'description': 'Ambiente de homologação'
    },
    'PRD': {
        'name': 'Produção',
        'database_url': os.getenv('BD_COMPRAS_PRD'),
        'description': 'Ambiente de produção'
    }
}

# Ambiente padrão
DEFAULT_ENVIRONMENT = 'HOM'

def get_environment_config(env_code):
    """Retorna a configuração do ambiente especificado"""
    return ENVIRONMENTS.get(env_code, ENVIRONMENTS[DEFAULT_ENVIRONMENT])

def get_database_url(env_code):
    """Retorna a URL do banco de dados para o ambiente especificado"""
    config = get_environment_config(env_code)
    return config['database_url']

def get_available_environments():
    """Retorna lista de ambientes disponíveis"""
    return ENVIRONMENTS
