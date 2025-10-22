"""
Decorators para controle de acesso e permissões
"""
from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def role_required(*roles):
    """
    Decorator para verificar se o usuário tem uma das roles especificadas
    
    Usage:
        @role_required('ADMIN', 'MANAGER')
        def my_view():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor, faça login para acessar esta página.', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.role not in roles:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                abort(403)
            
            if not current_user.is_active():
                flash('Sua conta está inativa. Entre em contato com o administrador.', 'danger')
                return redirect(url_for('auth.logout'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorator para verificar se o usuário é admin
    
    Usage:
        @admin_required
        def admin_view():
            pass
    """
    return role_required('ADMIN')(f)

def manager_required(f):
    """
    Decorator para verificar se o usuário é manager
    
    Usage:
        @manager_required
        def manager_view():
            pass
    """
    return role_required('MANAGER')(f)

def purchaser_required(f):
    """
    Decorator para verificar se o usuário é purchaser
    
    Usage:
        @purchaser_required
        def purchaser_view():
            pass
    """
    return role_required('PURCHASER')(f)

def finance_required(f):
    """
    Decorator para verificar se o usuário é finance
    
    Usage:
        @finance_required
        def finance_view():
            pass
    """
    return role_required('FINANCE')(f)

def user_required(f):
    """
    Decorator para verificar se o usuário é um usuário comum
    
    Usage:
        @user_required
        def user_view():
            pass
    """
    return role_required('USER')(f)

def active_user_required(f):
    """
    Decorator para verificar se o usuário está ativo
    
    Usage:
        @active_user_required
        def my_view():
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_active():
            flash('Sua conta está inativa. Entre em contato com o administrador.', 'danger')
            return redirect(url_for('auth.logout'))
        
        return f(*args, **kwargs)
    return decorated_function

def login_required_only(f):
    """
    Decorator que apenas verifica se o usuário está logado, sem restrições de role
    
    Usage:
        @login_required_only
        def my_view():
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

