"""
Rotas principais da aplicação
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from .. import db
from ..models import PurchaseRequest, Department
from sqlalchemy import func, extract
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página inicial - redireciona para login ou dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal - redireciona para o dashboard específico da role"""
    role_dashboards = {
        'ADMIN': 'admin.dashboard',
        'MANAGER': 'manager.dashboard',
        'USER': 'user.dashboard',
        'PURCHASER': 'purchaser.dashboard',
        'FINANCE': 'finance.dashboard'
    }
    
    dashboard_route = role_dashboards.get(current_user.role, 'main.index')
    return redirect(url_for(dashboard_route))

