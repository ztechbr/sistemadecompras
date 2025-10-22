"""
Rotas de cotações
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import Quotation, PurchaseRequest, QuotationItem
from ..utils.decorators import login_required_only

quotation_bp = Blueprint('quotation', __name__, url_prefix='/quotations')

@quotation_bp.route('/')
@login_required
@login_required_only
def index():
    """Lista de cotações"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Quotation.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    quotations = query.order_by(Quotation.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('quotation/index.html', 
                         quotations=quotations, 
                         status_filter=status_filter)

@quotation_bp.route('/request/<int:request_id>')
@login_required
@login_required_only
def by_request(request_id):
    """Cotações de uma requisição específica"""
    request_obj = PurchaseRequest.query.get_or_404(request_id)
    quotations = Quotation.query.filter_by(purchase_request_id=request_id).all()
    
    return render_template('quotation/by_request.html', 
                         request=request_obj, 
                         quotations=quotations)

@quotation_bp.route('/create')
@login_required
@login_required_only
def create_form():
    """Formulário para criar nova cotação"""
    # Buscar requisições que precisam de cotação
    requests = PurchaseRequest.query.filter_by(status='AGUARDANDO_COTACAO').all()
    
    return render_template('quotation/create.html', requests=requests)

@quotation_bp.route('/create', methods=['POST'])
@login_required
@login_required_only
def create():
    """Criar nova cotação"""
    try:
        # Validar dados obrigatórios
        if not request.form.get('purchase_request_id'):
            flash('Selecione uma requisição!', 'danger')
            return redirect(url_for('quotation.create_form'))
        
        if not request.form.get('vendor_name'):
            flash('Nome do fornecedor é obrigatório!', 'danger')
            return redirect(url_for('quotation.create_form'))
        
        if not request.form.get('unit_value'):
            flash('Valor unitário é obrigatório!', 'danger')
            return redirect(url_for('quotation.create_form'))
        
        if not request.form.get('quantity'):
            flash('Quantidade é obrigatória!', 'danger')
            return redirect(url_for('quotation.create_form'))
        
        # Converter dados
        purchase_request_id = int(request.form.get('purchase_request_id'))
        vendor_name = request.form.get('vendor_name').strip()
        vendor_cnpj = request.form.get('vendor_cnpj', '').strip()
        description = request.form.get('description', '').strip()
        unit_value = float(request.form.get('unit_value'))
        quantity = int(request.form.get('quantity'))
        
        # Verificar se já existem 3 cotações para esta requisição
        existing_quotations = Quotation.query.filter_by(purchase_request_id=purchase_request_id).count()
        if existing_quotations >= 3:
            flash('Limite máximo de 3 cotações por requisição atingido!', 'danger')
            return redirect(url_for('quotation.create_form'))
        
        # Buscar a requisição
        request_obj = PurchaseRequest.query.get(purchase_request_id)
        if not request_obj:
            flash('Requisição não encontrada!', 'danger')
            return redirect(url_for('quotation.create_form'))
        
        # Calcular valores
        total_value = unit_value * quantity
        
        # Criar cotação
        quotation = Quotation(
            purchase_request_id=purchase_request_id,
            purchaser_id=current_user.id,
            status='DRAFT'
        )
        
        db.session.add(quotation)
        db.session.flush()  # Para obter o ID da cotação
        
        # Criar item da cotação
        quotation_item = QuotationItem(
            quotation_id=quotation.id,
            vendor_name=vendor_name,
            vendor_cnpj=vendor_cnpj,
            description=description,
            unit_value=unit_value,
            quantity=quantity,
            total_value=total_value
        )
        
        db.session.add(quotation_item)
        
        # Atualizar status da requisição
        if request_obj.status == 'AGUARDANDO_COTACAO':
            request_obj.status = 'EM_COTACAO'
        
        db.session.commit()
        
        flash('Cotação criada com sucesso!', 'success')
        return redirect(url_for('quotation.by_request', request_id=purchase_request_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar cotação: {str(e)}', 'danger')
        return redirect(url_for('quotation.create_form'))

@quotation_bp.route('/<int:quotation_id>/select', methods=['POST'])
@login_required
@login_required_only
def select(quotation_id):
    """Selecionar cotação (fornecedor escolhido)"""
    try:
        quotation = Quotation.query.get_or_404(quotation_id)
        
        # Desmarcar todas as outras cotações da mesma requisição
        Quotation.query.filter_by(
            purchase_request_id=quotation.purchase_request_id
        ).update({'is_selected': False, 'status': 'COTACAO_ENCERRADA'})
        
        # Marcar esta cotação como selecionada
        quotation.is_selected = True
        quotation.status = 'FORNECEDOR_SELECIONADO'
        
        # Atualizar status da requisição
        request_obj = PurchaseRequest.query.get(quotation.purchase_request_id)
        request_obj.status = 'AGUARDANDO_APROVACAO'
        
        db.session.commit()
        
        flash(f'Fornecedor {quotation.supplier.name} selecionado!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao selecionar cotação: {str(e)}', 'danger')
    
    return redirect(url_for('quotation.by_request', request_id=quotation.purchase_request_id))

@quotation_bp.route('/<int:quotation_id>/edit', methods=['POST'])
@login_required
@login_required_only
def edit(quotation_id):
    """Editar cotação"""
    try:
        quotation = Quotation.query.get_or_404(quotation_id)
        
        quotation.unit_price = request.form.get('unit_price')
        quotation.delivery_days = request.form.get('delivery_days')
        quotation.payment_terms = request.form.get('payment_terms')
        quotation.observations = request.form.get('observations')
        
        # Recalcular total
        request_obj = PurchaseRequest.query.get(quotation.purchase_request_id)
        quotation.total_value = float(quotation.unit_price) * request_obj.quantity
        
        db.session.commit()
        
        flash('Cotação atualizada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar cotação: {str(e)}', 'danger')
    
    return redirect(url_for('quotation.by_request', request_id=quotation.purchase_request_id))

@quotation_bp.route('/<int:quotation_id>/delete', methods=['POST'])
@login_required
@login_required_only
def delete(quotation_id):
    """Deletar cotação"""
    try:
        quotation = Quotation.query.get_or_404(quotation_id)
        request_id = quotation.purchase_request_id
        
        db.session.delete(quotation)
        db.session.commit()
        
        flash('Cotação deletada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar cotação: {str(e)}', 'danger')
    
    return redirect(url_for('quotation.by_request', request_id=request_id))

