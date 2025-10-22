"""
Rotas do usuário comum
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .. import db
from ..models import PurchaseRequest, Product, Department
from ..utils.decorators import login_required_only
from sqlalchemy import func
from datetime import datetime, timedelta

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard')
@login_required
@login_required_only
def dashboard():
    """Dashboard do usuário comum"""
    # Estatísticas do usuário
    total_requests = PurchaseRequest.query.filter_by(user_id=current_user.id).count()
    pending_requests = PurchaseRequest.query.filter_by(
        user_id=current_user.id, 
        status='PENDING'
    ).count()
    approved_requests = PurchaseRequest.query.filter_by(
        user_id=current_user.id, 
        status='APPROVED'
    ).count()
    
    # Solicitações recentes
    recent_requests = PurchaseRequest.query.filter_by(
        user_id=current_user.id
    ).order_by(PurchaseRequest.created_at.desc()).limit(5).all()
    
    return render_template('user/dashboard.html',
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         approved_requests=approved_requests,
                         recent_requests=recent_requests)

@user_bp.route('/requests')
@login_required
@login_required_only
def requests():
    """Lista de solicitações do usuário"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = PurchaseRequest.query.filter_by(user_id=current_user.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    requests = query.order_by(PurchaseRequest.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('user/requests.html', 
                         requests=requests, 
                         status_filter=status_filter)

@user_bp.route('/create-request')
@login_required
@login_required_only
def create_request():
    """Formulário para criar nova solicitação"""
    products = Product.query.filter_by(status='ATIVO').all()
    return render_template('user/create_request.html', products=products)

@user_bp.route('/create-request', methods=['POST'])
@login_required
@login_required_only
def create_request_post():
    """Processa criação de nova solicitação"""
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity')
    notes = request.form.get('notes', '')
    
    if not product_id or not quantity:
        flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
        return redirect(url_for('user.create_request'))
    
    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError()
    except ValueError:
        flash('Quantidade deve ser um número inteiro positivo.', 'error')
        return redirect(url_for('user.create_request'))
    
    # Gerar número da solicitação
    today = datetime.now().strftime('%Y%m%d')
    last_request = PurchaseRequest.query.filter(
        PurchaseRequest.request_number.like(f'REQ{today}%')
    ).order_by(PurchaseRequest.request_number.desc()).first()
    
    if last_request:
        last_number = int(last_request.request_number[-4:])
        new_number = f'REQ{today}{last_number + 1:04d}'
    else:
        new_number = f'REQ{today}0001'
    
    # Criar solicitação
    request_obj = PurchaseRequest(
        request_number=new_number,
        user_id=current_user.id,
        product_id=product_id,
        quantity=quantity,
        notes=notes,
        status='PENDING'
    )
    
    db.session.add(request_obj)
    db.session.commit()
    
    flash('Solicitação criada com sucesso!', 'success')
    return redirect(url_for('user.requests'))

@user_bp.route('/request/<int:request_id>')
@login_required
@login_required_only
def view_request(request_id):
    """Visualizar detalhes de uma solicitação"""
    request_obj = PurchaseRequest.query.filter_by(
        id=request_id, 
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('user/view_request.html', request=request_obj)

