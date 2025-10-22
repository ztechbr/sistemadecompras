"""
Rotas de solicitações de pagamento
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from .. import db
from ..models import PaymentRequest, Invoice, PurchaseOrder
from ..utils.decorators import login_required_only

payment_request_bp = Blueprint('payment_request', __name__, url_prefix='/payment-requests')

@payment_request_bp.route('/')
@login_required
@login_required_only
def index():
    """Lista de solicitações de pagamento"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = PaymentRequest.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    requests = query.order_by(PaymentRequest.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('payment_request/index.html', 
                         requests=requests, 
                         status_filter=status_filter)

@payment_request_bp.route('/create/<int:invoice_id>')
@login_required
@login_required_only
def create_from_invoice(invoice_id):
    """Criar solicitação de pagamento a partir de nota fiscal"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Verificar se a nota fiscal está aprovada
    if invoice.status != 'APROVADO_PAGAMENTO':
        flash('Apenas notas fiscais aprovadas podem gerar solicitações de pagamento.', 'danger')
        return redirect(url_for('invoice.view', invoice_id=invoice_id))
    
    return render_template('payment_request/create.html', invoice=invoice)

@payment_request_bp.route('/create', methods=['POST'])
@login_required
@login_required_only
def create():
    """Criar solicitação de pagamento"""
    try:
        invoice_id = request.form.get('invoice_id')
        purchase_order_id = request.form.get('purchase_order_id')
        approved_value = request.form.get('approved_value')
        cost_center = request.form.get('cost_center')
        accounting_account = request.form.get('accounting_account')
        notes = request.form.get('notes')
        
        # Gerar número da solicitação
        request_number = PaymentRequest.generate_request_number()
        
        payment_request = PaymentRequest(
            request_number=request_number,
            invoice_id=invoice_id,
            purchase_order_id=purchase_order_id,
            approved_value=float(approved_value),
            cost_center=cost_center,
            accounting_account=accounting_account,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(payment_request)
        db.session.commit()
        
        flash(f'Solicitação de pagamento {request_number} criada com sucesso!', 'success')
        return redirect(url_for('payment_request.view', request_id=payment_request.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar solicitação de pagamento: {str(e)}', 'danger')
        return redirect(url_for('payment_request.index'))

@payment_request_bp.route('/<int:request_id>')
@login_required
@login_required_only
def view(request_id):
    """Visualizar solicitação de pagamento"""
    request_obj = PaymentRequest.query.get_or_404(request_id)
    return render_template('payment_request/view.html', request=request_obj)

@payment_request_bp.route('/<int:request_id>/pay', methods=['POST'])
@login_required
@login_required_only
def pay(request_id):
    """Registrar pagamento"""
    try:
        request_obj = PaymentRequest.query.get_or_404(request_id)
        payment_date = request.form.get('payment_date')
        payment_method = request.form.get('payment_method')
        notes = request.form.get('notes', '')
        
        # Converter data
        payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
        
        request_obj.status = 'PAGO'
        request_obj.payment_date = payment_date
        request_obj.payment_method = payment_method
        
        if notes:
            request_obj.notes = notes
        
        db.session.commit()
        
        flash('Pagamento registrado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao registrar pagamento: {str(e)}', 'danger')
    
    return redirect(url_for('payment_request.view', request_id=request_id))

@payment_request_bp.route('/<int:request_id>/cancel', methods=['POST'])
@login_required
@login_required_only
def cancel(request_id):
    """Cancelar solicitação de pagamento"""
    try:
        request_obj = PaymentRequest.query.get_or_404(request_id)
        notes = request.form.get('notes', '')
        
        request_obj.status = 'CANCELADO'
        if notes:
            request_obj.notes = notes
        
        db.session.commit()
        
        flash('Solicitação de pagamento cancelada.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cancelar solicitação: {str(e)}', 'danger')
    
    return redirect(url_for('payment_request.view', request_id=request_id))

@payment_request_bp.route('/export')
@login_required
@login_required_only
def export():
    """Exportar relatório de pagamentos"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = PaymentRequest.query
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(PaymentRequest.created_at >= start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(PaymentRequest.created_at <= end_date)
    
    requests = query.order_by(PaymentRequest.created_at.desc()).all()
    
    return render_template('payment_request/export.html', 
                         requests=requests,
                         start_date=start_date,
                         end_date=end_date)



