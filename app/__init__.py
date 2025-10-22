"""
Inicialização da aplicação Flask
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config

# Inicializar extensões
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name='development'):
    """
    Factory para criar a aplicação Flask
    
    Args:
        config_name: Nome da configuração a ser usada
        
    Returns:
        Instância configurada da aplicação Flask
    """
    app = Flask(__name__)
    
    # Carregar configuração
    app.config.from_object(config[config_name])
    
    # Inicializar extensões com a app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configurar login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Carrega o usuário pelo ID"""
        from .models import User
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.user import user_bp
    from .routes.manager import manager_bp
    from .routes.purchaser import purchaser_bp
    from .routes.finance import finance_bp
    from .routes.main import main_bp
    from .routes.supplier import supplier_bp
    from .routes.purchase_request import purchase_request_bp
    from .routes.quotation import quotation_bp
    from .routes.purchase_order import purchase_order_bp
    from .routes.invoice import invoice_bp
    from .routes.payment_request import payment_request_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(purchaser_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(supplier_bp)
    app.register_blueprint(purchase_request_bp)
    app.register_blueprint(quotation_bp)
    app.register_blueprint(purchase_order_bp)
    app.register_blueprint(invoice_bp)
    app.register_blueprint(payment_request_bp)
    
    # Registrar filtros de template
    from .utils.filters import register_filters
    register_filters(app)
    
    # Registrar contexto de template
    @app.context_processor
    def inject_environment():
        """Injeta informações do ambiente atual no contexto dos templates"""
        from flask import session
        from environment_config import get_available_environments
        
        current_env = session.get('selected_environment', 'HOM')
        environments = get_available_environments()
        current_env_config = environments.get(current_env, environments['HOM'])
        
        return {
            'current_environment': current_env,
            'current_environment_name': current_env_config['name'],
            'available_environments': environments
        }
    
    # Registrar error handlers
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """Registra handlers de erro personalizados"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500

