"""
Rotas do gerente (manager)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .. import db
from ..models import PurchaseRequest, Quotation, PaymentRequest, Payment
from ..utils.decorators import login_required_only
from sqlalchemy import func
from datetime import datetime

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')

@manager_bp.route('/dashboard')
@login_required
@login_required_only
def dashboard():
    """Dashboard do gerente"""
    # Requisições pendentes de aprovação do departamento
    pending_requests = PurchaseRequest.query.join(
        PurchaseRequest.requester
    ).filter(
        PurchaseRequest.status == 'PENDING',
        PurchaseRequest.requester.has(department_id=current_user.department_id)
    ).order_by(PurchaseRequest.created_at.asc()).all()
    
    # Cotações pendentes de aprovação
    pending_quotations = Quotation.query.join(
        Quotation.purchase_request
    ).join(
        PurchaseRequest.requester
    ).filter(
        Quotation.status == 'RELEASED',
        PurchaseRequest.requester.has(department_id=current_user.department_id)
    ).order_by(Quotation.released_at.asc()).all()
    
    # Pagamentos pendentes de liberação
    pending_payments = PaymentRequest.query.filter(
        PaymentRequest.status == 'AGUARDANDO_PAGAMENTO'
    ).all()
    
    # Filtrar por departamento
    dept_payments = []
    for payment in pending_payments:
        if (payment.purchase_order and 
            payment.purchase_order.purchase_request and 
            payment.purchase_order.purchase_request.requester and
            payment.purchase_order.purchase_request.requester.department_id == current_user.department_id):
            dept_payments.append(payment)
    
    pending_payments = dept_payments
    
    # Estatísticas do departamento
    dept_requests = PurchaseRequest.query.join(
        PurchaseRequest.requester
    ).filter(
        PurchaseRequest.requester.has(department_id=current_user.department_id)
    ).all()
    
    total_requests = len(dept_requests)
    approved_requests = len([r for r in dept_requests if r.status not in ['PENDING', 'REJECTED', 'CANCELLED']])
    
    return render_template('manager/dashboard.html',
                         pending_requests=pending_requests,
                         pending_quotations=pending_quotations,
                         pending_payments=pending_payments,
                         total_requests=total_requests,
                         approved_requests=approved_requests)

@manager_bp.route('/requests')
@login_required
@login_required_only
def requests():
    """Lista de requisições do departamento"""
    dept_requests = PurchaseRequest.query.join(
        PurchaseRequest.requester
    ).filter(
        PurchaseRequest.requester.has(department_id=current_user.department_id)
    ).order_by(PurchaseRequest.created_at.desc()).all()
    
    return render_template('manager/requests.html', requests=dept_requests)

@manager_bp.route('/requests/<int:request_id>/approve', methods=['POST'])
@login_required
@login_required_only
def approve_request(request_id):
    """Aprovar requisição de compra"""
    try:
        purchase_request = PurchaseRequest.query.get_or_404(request_id)
        
        # Verificar se pode aprovar
        if not purchase_request.can_be_approved_by(current_user):
            flash('Você não pode aprovar esta requisição.', 'danger')
            return redirect(url_for('manager.requests'))
        
        purchase_request.approve(current_user)
        flash(f'Requisição {purchase_request.request_number} aprovada com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao aprovar requisição: {str(e)}', 'danger')
    
    return redirect(url_for('manager.dashboard'))

@manager_bp.route('/requests/<int:request_id>/reject', methods=['POST'])
@login_required
@login_required_only
def reject_request(request_id):
    """Rejeitar requisição de compra"""
    try:
        purchase_request = PurchaseRequest.query.get_or_404(request_id)
        reason = request.form.get('reason', 'Não aprovado')
        
        # Verificar se pode rejeitar
        if not purchase_request.can_be_approved_by(current_user):
            flash('Você não pode rejeitar esta requisição.', 'danger')
            return redirect(url_for('manager.requests'))
        
        purchase_request.reject(current_user, reason)
        flash(f'Requisição {purchase_request.request_number} rejeitada.', 'warning')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao rejeitar requisição: {str(e)}', 'danger')
    
    return redirect(url_for('manager.dashboard'))

@manager_bp.route('/quotations')
@login_required
@login_required_only
def quotations():
    """Lista de cotações para aprovação"""
    dept_quotations = Quotation.query.join(
        Quotation.purchase_request
    ).join(
        PurchaseRequest.requester
    ).filter(
        Quotation.status == 'RELEASED',
        PurchaseRequest.requester.has(department_id=current_user.department_id)
    ).order_by(Quotation.released_at.asc()).all()
    
    return render_template('manager/quotations.html', quotations=dept_quotations)

@manager_bp.route('/quotations/<int:quotation_id>')
@login_required
@login_required_only
def view_quotation(quotation_id):
    """Visualizar detalhes da cotação"""
    quotation = Quotation.query.get_or_404(quotation_id)
    
    # Verificar se é do departamento
    if quotation.purchase_request.requester.department_id != current_user.department_id:
        flash('Você não tem permissão para ver esta cotação.', 'danger')
        return redirect(url_for('manager.quotations'))
    
    items = quotation.get_sorted_items()
    
    return render_template('manager/view_quotation.html', 
                         quotation=quotation,
                         items=items)

@manager_bp.route('/quotations/<int:quotation_id>/approve', methods=['POST'])
@login_required
@login_required_only
def approve_quotation(quotation_id):
    """Aprovar cotação selecionando fornecedor"""
    try:
        quotation = Quotation.query.get_or_404(quotation_id)
        selected_item_id = request.form.get('selected_item_id')
        
        # Verificar se é do departamento
        if quotation.purchase_request.requester.department_id != current_user.department_id:
            flash('Você não tem permissão para aprovar esta cotação.', 'danger')
            return redirect(url_for('manager.quotations'))
        
        if not selected_item_id:
            flash('Selecione um fornecedor.', 'danger')
            return redirect(url_for('manager.view_quotation', quotation_id=quotation_id))
        
        quotation.approve(current_user, int(selected_item_id))
        flash('Fornecedor aprovado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao aprovar cotação: {str(e)}', 'danger')
    
    return redirect(url_for('manager.quotations'))

@manager_bp.route('/quotations/<int:quotation_id>/cancel', methods=['POST'])
@login_required
@login_required_only
def cancel_quotation(quotation_id):
    """Cancelar cotação"""
    try:
        quotation = Quotation.query.get_or_404(quotation_id)
        
        # Verificar se é do departamento
        if quotation.purchase_request.requester.department_id != current_user.department_id:
            flash('Você não tem permissão para cancelar esta cotação.', 'danger')
            return redirect(url_for('manager.quotations'))
        
        quotation.cancel()
        flash('Cotação cancelada.', 'warning')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cancelar cotação: {str(e)}', 'danger')
    
    return redirect(url_for('manager.quotations'))

@manager_bp.route('/payments')
@login_required
@login_required_only
def payments():
    """Lista de pagamentos para liberação"""
    all_payments = PaymentRequest.query.filter(
        PaymentRequest.status == 'AGUARDANDO_PAGAMENTO'
    ).all()
    
    # Filtrar por departamento
    dept_payments = []
    for payment in all_payments:
        if (payment.purchase_order and 
            payment.purchase_order.purchase_request and 
            payment.purchase_order.purchase_request.requester and
            payment.purchase_order.purchase_request.requester.department_id == current_user.department_id):
            dept_payments.append(payment)
    
    return render_template('manager/payments.html', payment_requests=dept_payments)

@manager_bp.route('/payments/<int:payment_id>/release', methods=['POST'])
@login_required
@login_required_only
def release_payment(payment_id):
    """Liberar pagamento"""
    try:
        payment_request = PaymentRequest.query.get_or_404(payment_id)
        
        # Verificar se é do departamento
        if (payment_request.purchase_order and 
            payment_request.purchase_order.purchase_request and 
            payment_request.purchase_order.purchase_request.requester and
            payment_request.purchase_order.purchase_request.requester.department_id != current_user.department_id):
            flash('Você não tem permissão para liberar este pagamento.', 'danger')
            return redirect(url_for('manager.payments'))
        
        payment_request.status = 'PAGO'
        payment_request.payment_date = datetime.utcnow().date()
        db.session.commit()
        flash('Pagamento liberado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao liberar pagamento: {str(e)}', 'danger')
    
    return redirect(url_for('manager.payments'))

