"""
Rotas de notas fiscais
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from .. import db
from ..models import Invoice, PurchaseOrder, QuotationItem
from ..utils.decorators import login_required_only

invoice_bp = Blueprint('invoice', __name__, url_prefix='/invoices')

@invoice_bp.route('/')
@login_required
@login_required_only
def index():
    """Lista de notas fiscais"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Invoice.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    invoices = query.order_by(Invoice.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('invoice/index.html', 
                         invoices=invoices, 
                         status_filter=status_filter)

@invoice_bp.route('/create/<int:order_id>')
@login_required
@login_required_only
def create_from_order(order_id):
    """Criar nota fiscal a partir de pedido"""
    order = PurchaseOrder.query.get_or_404(order_id)
    
    # Verificar se o pedido está concluído
    if order.status != 'CONCLUIDO':
        flash('Apenas pedidos concluídos podem gerar notas fiscais.', 'danger')
        return redirect(url_for('purchase_order.view', order_id=order_id))
    
    return render_template('invoice/create.html', order=order)

@invoice_bp.route('/create', methods=['POST'])
@login_required
@login_required_only
def create():
    """Criar nota fiscal"""
    try:
        purchase_order_id = request.form.get('purchase_order_id')
        supplier_id = request.form.get('supplier_id')
        invoice_number = request.form.get('invoice_number')
        issue_date = request.form.get('issue_date')
        receipt_date = request.form.get('receipt_date')
        total_value = request.form.get('total_value')
        notes = request.form.get('notes')
        
        # Buscar o pedido para comparar valores
        order = PurchaseOrder.query.get(purchase_order_id)
        
        # Converter datas
        issue_date = datetime.strptime(issue_date, '%Y-%m-%d').date()
        receipt_date = datetime.strptime(receipt_date, '%Y-%m-%d').date()
        
        invoice = Invoice(
            invoice_number=invoice_number,
            purchase_order_id=purchase_order_id,
            supplier_id=supplier_id,
            issue_date=issue_date,
            receipt_date=receipt_date,
            total_value=float(total_value),
            order_value=float(order.total_value),
            notes=notes,
            created_by=current_user.id
        )
        
        # Calcular diferenças
        invoice.calculate_difference()
        
        # Definir status baseado na diferença
        if invoice.has_significant_difference():
            invoice.status = 'DIVERGENCIA_DETECTADA'
        else:
            invoice.status = 'PENDENTE_CONFERENCIA'
        
        db.session.add(invoice)
        db.session.commit()
        
        flash(f'Nota fiscal {invoice_number} registrada com sucesso!', 'success')
        return redirect(url_for('invoice.view', invoice_id=invoice.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao registrar nota fiscal: {str(e)}', 'danger')
        return redirect(url_for('invoice.index'))

@invoice_bp.route('/<int:invoice_id>')
@login_required
@login_required_only
def view(invoice_id):
    """Visualizar nota fiscal"""
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('invoice/view.html', invoice=invoice)

@invoice_bp.route('/<int:invoice_id>/approve', methods=['POST'])
@login_required
@login_required_only
def approve(invoice_id):
    """Aprovar nota fiscal para pagamento"""
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        
        invoice.status = 'APROVADO_PAGAMENTO'
        db.session.commit()
        
        flash('Nota fiscal aprovada para pagamento!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao aprovar nota fiscal: {str(e)}', 'danger')
    
    return redirect(url_for('invoice.view', invoice_id=invoice_id))

@invoice_bp.route('/<int:invoice_id>/reject', methods=['POST'])
@login_required
@login_required_only
def reject(invoice_id):
    """Rejeitar nota fiscal"""
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        notes = request.form.get('notes', '')
        
        invoice.status = 'DIVERGENCIA_DETECTADA'
        if notes:
            invoice.notes = notes
        
        db.session.commit()
        
        flash('Nota fiscal rejeitada devido a divergências.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao rejeitar nota fiscal: {str(e)}', 'danger')
    
    return redirect(url_for('invoice.view', invoice_id=invoice_id))



