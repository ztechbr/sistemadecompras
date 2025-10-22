"""
Rotas de requisições de compra
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import PurchaseRequest, Product, Department, User
from ..utils.decorators import login_required_only

purchase_request_bp = Blueprint('purchase_request', __name__, url_prefix='/purchase-requests')

@purchase_request_bp.route('/')
@login_required
def index():
    """Lista de requisições de compra"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    department_filter = request.args.get('department', '')
    
    query = PurchaseRequest.query
    
    # Filtros baseados no role do usuário
    if current_user.role == 'USER':
        query = query.filter_by(user_id=current_user.id)
    elif current_user.role == 'MANAGER':
        query = query.join(User).filter(User.department_id == current_user.department_id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if department_filter:
        query = query.join(User).filter(User.department_id == department_filter)
    
    requests = query.order_by(PurchaseRequest.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    departments = Department.query.filter_by(status='ATIVO').all()
    
    return render_template('purchase_request/index.html', 
                         requests=requests, 
                         status_filter=status_filter,
                         department_filter=department_filter,
                         departments=departments)

@purchase_request_bp.route('/create', methods=['GET', 'POST'])
@login_required
@login_required_only
def create():
    """Criar nova requisição de compra"""
    if request.method == 'POST':
        try:
            product_id = request.form.get('product_id')
            quantity = request.form.get('quantity')
            justification = request.form.get('justification')
            notes = request.form.get('notes')
            
            # Gerar número da requisição
            request_number = PurchaseRequest.generate_request_number()
            
            # Calcular valor estimado (usando preço médio do produto)
            product = Product.query.get(product_id)
            estimated_total = float(product.average_unit_value) * int(quantity) if product else 0
            
            request_obj = PurchaseRequest(
                request_number=request_number,
                user_id=current_user.id,
                product_id=product_id,
                quantity=int(quantity),
                unit='UN',
                justification=justification,
                estimated_total=estimated_total,
                notes=notes,
                status='AGUARDANDO_COTACAO'
            )
            
            db.session.add(request_obj)
            db.session.commit()
            
            flash(f'Requisição {request_number} criada com sucesso!', 'success')
            return redirect(url_for('purchase_request.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar requisição: {str(e)}', 'danger')
    
    products = Product.query.filter_by(status='ATIVO').all()
    return render_template('purchase_request/create.html', products=products)

@purchase_request_bp.route('/<int:request_id>')
@login_required
def view(request_id):
    """Visualizar requisição de compra"""
    request_obj = PurchaseRequest.query.get_or_404(request_id)
    
    # Verificar permissões
    if current_user.role == 'USER' and request_obj.user_id != current_user.id:
        flash('Você não tem permissão para visualizar esta requisição.', 'danger')
        return redirect(url_for('purchase_request.index'))
    
    if current_user.role == 'MANAGER' and request_obj.department_id != current_user.department_id:
        flash('Você não tem permissão para visualizar esta requisição.', 'danger')
        return redirect(url_for('purchase_request.index'))
    
    return render_template('purchase_request/view.html', request=request_obj)

@purchase_request_bp.route('/<int:request_id>/approve', methods=['POST'])
@login_required
@login_required_only
def approve(request_id):
    """Aprovar requisição de compra"""
    try:
        request_obj = PurchaseRequest.query.get_or_404(request_id)
        
        # Verificar se o gerente pode aprovar (mesmo departamento)
        if request_obj.department_id != current_user.department_id:
            flash('Você só pode aprovar requisições do seu departamento.', 'danger')
            return redirect(url_for('purchase_request.view', request_id=request_id))
        
        request_obj.status = 'APROVADA'
        request_obj.approved_by = current_user.id
        request_obj.approved_at = db.func.now()
        
        db.session.commit()
        
        flash(f'Requisição {request_obj.request_number} aprovada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao aprovar requisição: {str(e)}', 'danger')
    
    return redirect(url_for('purchase_request.view', request_id=request_id))

@purchase_request_bp.route('/<int:request_id>/reject', methods=['POST'])
@login_required
@login_required_only
def reject(request_id):
    """Rejeitar requisição de compra"""
    try:
        request_obj = PurchaseRequest.query.get_or_404(request_id)
        rejected_reason = request.form.get('rejected_reason')
        
        # Verificar se o gerente pode rejeitar (mesmo departamento)
        if request_obj.department_id != current_user.department_id:
            flash('Você só pode rejeitar requisições do seu departamento.', 'danger')
            return redirect(url_for('purchase_request.view', request_id=request_id))
        
        request_obj.status = 'CANCELADA'
        request_obj.rejected_by = current_user.id
        request_obj.rejected_at = db.func.now()
        request_obj.rejected_reason = rejected_reason
        
        db.session.commit()
        
        flash(f'Requisição {request_obj.request_number} rejeitada.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao rejeitar requisição: {str(e)}', 'danger')
    
    return redirect(url_for('purchase_request.view', request_id=request_id))

