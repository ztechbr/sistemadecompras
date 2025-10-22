"""
Rotas de pedidos de compra
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import PurchaseOrder, PurchaseRequest, Quotation, QuotationItem
from ..utils.decorators import login_required_only

purchase_order_bp = Blueprint('purchase_order', __name__, url_prefix='/purchase-orders')

@purchase_order_bp.route('/')
@login_required
@login_required_only
def index():
    """Lista de pedidos de compra"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = PurchaseOrder.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    orders = query.order_by(PurchaseOrder.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('purchase_order/index.html', 
                         orders=orders, 
                         status_filter=status_filter)

@purchase_order_bp.route('/create/<int:request_id>')
@login_required
@login_required_only
def create_from_request(request_id):
    """Criar pedido de compra a partir de requisição aprovada"""
    request_obj = PurchaseRequest.query.get_or_404(request_id)
    
    # Verificar se a requisição está aprovada
    if request_obj.status != 'APROVADA':
        flash('Apenas requisições aprovadas podem gerar pedidos de compra.', 'danger')
        return redirect(url_for('purchase_request.view', request_id=request_id))
    
    # Buscar a cotação selecionada
    selected_quotation = Quotation.query.filter_by(
        purchase_request_id=request_id,
        is_selected=True
    ).first()
    
    if not selected_quotation:
        flash('Nenhuma cotação foi selecionada para esta requisição.', 'danger')
        return redirect(url_for('purchase_request.view', request_id=request_id))
    
    return render_template('purchase_order/create.html', 
                         request=request_obj, 
                         quotation=selected_quotation)

@purchase_order_bp.route('/create', methods=['POST'])
@login_required
@login_required_only
def create():
    """Criar pedido de compra"""
    try:
        purchase_request_id = request.form.get('purchase_request_id')
        supplier_id = request.form.get('supplier_id')
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        unit_price = request.form.get('unit_price')
        delivery_days = request.form.get('delivery_days')
        payment_terms = request.form.get('payment_terms')
        notes = request.form.get('notes')
        
        # Gerar número do pedido
        order_number = PurchaseOrder.generate_order_number()
        
        # Calcular valor total
        total_value = float(unit_price) * int(quantity)
        
        order = PurchaseOrder(
            order_number=order_number,
            purchase_request_id=purchase_request_id,
            supplier_id=supplier_id,
            product_id=product_id,
            quantity=int(quantity),
            unit_price=unit_price,
            total_value=total_value,
            delivery_days=int(delivery_days),
            payment_terms=payment_terms,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(order)
        
        # Atualizar status da requisição
        request_obj = PurchaseRequest.query.get(purchase_request_id)
        request_obj.status = 'ORDENADA'
        
        db.session.commit()
        
        flash(f'Pedido de compra {order_number} criado com sucesso!', 'success')
        return redirect(url_for('purchase_order.view', order_id=order.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar pedido de compra: {str(e)}', 'danger')
        return redirect(url_for('purchase_order.index'))

@purchase_order_bp.route('/<int:order_id>')
@login_required
@login_required_only
def view(order_id):
    """Visualizar pedido de compra"""
    order = PurchaseOrder.query.get_or_404(order_id)
    return render_template('purchase_order/view.html', order=order)

@purchase_order_bp.route('/<int:order_id>/update-status', methods=['POST'])
@login_required
@login_required_only
def update_status(order_id):
    """Atualizar status do pedido"""
    try:
        order = PurchaseOrder.query.get_or_404(order_id)
        new_status = request.form.get('status')
        notes = request.form.get('notes', '')
        
        order.status = new_status
        
        if new_status == 'CONCLUIDO':
            order.actual_delivery_date = db.func.now()
        
        if notes:
            order.notes = notes
        
        db.session.commit()
        
        flash(f'Status do pedido atualizado para {order.get_status_label()}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar status: {str(e)}', 'danger')
    
    return redirect(url_for('purchase_order.view', order_id=order_id))



