"""
Rotas de autenticação
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user
from .. import db
from ..models import User
from environment_config import get_available_environments

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        environment = request.form.get('environment')
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        # Validar ambiente selecionado
        available_envs = get_available_environments()
        if environment not in available_envs:
            flash('Ambiente inválido selecionado.', 'danger')
            return render_template('auth/login.html', environments=available_envs)
        
        # Configurar banco de dados para o ambiente selecionado
        try:
            from config import Config
            from environment_config import get_database_url
            
            # Obter URL do banco para o ambiente selecionado
            database_url = get_database_url(environment)
            
            # Atualizar configuração da aplicação
            current_app.config['SQLALCHEMY_DATABASE_URI'] = database_url
            
            # Fechar conexões existentes e reconectar
            db.engine.dispose()
            
            # Armazenar ambiente na sessão
            session['selected_environment'] = environment
            
        except Exception as e:
            flash(f'Erro ao conectar com o ambiente {environment}: {str(e)}', 'danger')
            return render_template('auth/login.html', environments=available_envs)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active():
                flash('Sua conta está inativa. Entre em contato com o administrador.', 'danger')
                return render_template('auth/login.html', environments=available_envs)
            
            login_user(user, remember=remember)
            user.update_last_login()
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            return redirect(url_for('main.dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    
    return render_template('auth/login.html', environments=get_available_environments())

@auth_bp.route('/switch-environment', methods=['POST'])
def switch_environment():
    """Troca o ambiente atual"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    environment = request.form.get('environment')
    available_envs = get_available_environments()
    
    if environment not in available_envs:
        flash('Ambiente inválido selecionado.', 'danger')
        return redirect(request.referrer or url_for('main.dashboard'))
    
    try:
        from environment_config import get_database_url
        
        # Obter URL do banco para o ambiente selecionado
        database_url = get_database_url(environment)
        
        # Atualizar configuração da aplicação
        current_app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        
        # Fechar conexões existentes e reconectar
        db.engine.dispose()
        
        # Atualizar ambiente na sessão
        session['selected_environment'] = environment
        
        env_config = available_envs[environment]
        flash(f'Ambiente alterado para {env_config["name"]} com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao conectar com o ambiente {environment}: {str(e)}', 'danger')
    
    return redirect(request.referrer or url_for('main.dashboard'))

@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    logout_user()
    session.pop('selected_environment', None)  # Limpar ambiente da sessão
    flash('Você saiu do sistema com sucesso.', 'success')
    return redirect(url_for('auth.login'))

