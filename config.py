"""
Configurações da aplicação Flask
"""
import os
from datetime import timedelta
from dotenv import load_dotenv
from environment_config import get_database_url, DEFAULT_ENVIRONMENT

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configuração base"""
    
    # Secret key para sessões e CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuração do banco de dados PostgreSQL
    # Será definida dinamicamente baseada no ambiente selecionado
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        get_database_url(DEFAULT_ENVIRONMENT)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Configuração de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = False  # True em produção com HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuração de upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    
    # Configuração de paginação
    ITEMS_PER_PAGE = 20
    
    # Configuração de timezone
    TIMEZONE = 'America/Sao_Paulo'
    
    # Configuração de logs
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # Configuração da aplicação
    APP_NAME = 'Sistema de Compras'
    COMPANY_NAME = 'Empresa XYZ Ltda'
    
    @classmethod
    def set_environment(cls, env_code):
        """Define a configuração do banco de dados baseada no ambiente selecionado"""
        cls.SQLALCHEMY_DATABASE_URI = get_database_url(env_code)


class DevelopmentConfig(Config):
    """Configuração de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configuração de produção"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    def __init__(self):
        super().__init__()
        # Em produção, SECRET_KEY deve vir de variável de ambiente
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY não definida em produção!")


class TestingConfig(Config):
    """Configuração de testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/purchase_system_test'
    WTF_CSRF_ENABLED = False


# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

