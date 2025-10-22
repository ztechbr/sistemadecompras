"""
Rotas do financeiro (finance)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .. import db
from ..models import PaymentRequest, Invoice, PurchaseOrder, PurchaseRequest
from ..utils.decorators import login_required_only
from sqlalchemy import func
from datetime import datetime, timedelta

finance_bp = Blueprint('finance', __name__, url_prefix='/finance')

@finance_bp.route('/dashboard')
@login_required
@login_required_only
def dashboard():
    """Dashboard do financeiro"""
    # Pagamentos pendentes (aguardando liberação do manager)
    pending_payments = Payment.query.filter_by(status='PENDING').all()
    
    # Pagamentos liberados (aguardando pagamento)
    released_payments = Payment.query.filter_by(status='RELEASED').all()
    
    # Pagamentos realizados (últimos 30 dias)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    paid_payments = Payment.query.filter(
        Payment.status == 'PAID',
        Payment.paid_at >= thirty_days_ago
    ).all()
    
    # Calcular totais
    total_pending = sum([float(p.invoice.total_value) for p in pending_payments])
    total_released = sum([float(p.invoice.total_value) for p in released_payments])
    total_paid = sum([float(p.invoice.total_value) for p in paid_payments])
    
    return render_template('finance/dashboard.html',
                         pending_payments=pending_payments,
                         released_payments=released_payments,
                         paid_payments=paid_payments,
                         total_pending=total_pending,
                         total_released=total_released,
                         total_paid=total_paid)

@finance_bp.route('/payments')
@login_required
@login_required_only
def payments():
    """Lista de todos os pagamentos"""
    all_payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template('finance/payments.html', payments=all_payments)

@finance_bp.route('/payments/pending')
@login_required
@login_required_only
def pending_payments():
    """Pagamentos pendentes de liberação"""
    pending = Payment.query.filter_by(status='PENDING').order_by(Payment.created_at.asc()).all()
    return render_template('finance/pending_payments.html', payments=pending)

@finance_bp.route('/payments/released')
@login_required
@login_required_only
def released_payments():
    """Pagamentos liberados aguardando pagamento"""
    released = Payment.query.filter_by(status='RELEASED').order_by(Payment.released_at.asc()).all()
    return render_template('finance/released_payments.html', payments=released)

@finance_bp.route('/payments/<int:payment_id>')
@login_required
@login_required_only
def view_payment(payment_id):
    """Visualizar detalhes do pagamento"""
    payment = Payment.query.get_or_404(payment_id)
    return render_template('finance/view_payment.html', payment=payment)

@finance_bp.route('/payments/<int:payment_id>/pay', methods=['POST'])
@login_required
@login_required_only
def pay(payment_id):
    """Marcar pagamento como pago"""
    try:
        payment = Payment.query.get_or_404(payment_id)
        
        if payment.status != 'RELEASED':
            flash('Este pagamento ainda não foi liberado pelo gerente.', 'danger')
            return redirect(url_for('finance.view_payment', payment_id=payment_id))
        
        payment_notes = request.form.get('payment_notes')
        payment.payment_notes = payment_notes
        
        payment.mark_as_paid(current_user)
        
        flash(f'Pagamento realizado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao processar pagamento: {str(e)}', 'danger')
    
    return redirect(url_for('finance.payments'))

@finance_bp.route('/reports')
@login_required
@login_required_only
def reports():
    """Relatórios financeiros"""
    # Pagamentos por status
    payments_by_status = db.session.query(
        Payment.status,
        func.count(Payment.id).label('count'),
        func.sum(Invoice.total_value).label('total')
    ).join(Payment.invoice).group_by(Payment.status).all()
    
    # Pagamentos por mês (últimos 12 meses)
    twelve_months_ago = datetime.utcnow() - timedelta(days=365)
    payments_by_month = db.session.query(
        func.date_trunc('month', Payment.paid_at).label('month'),
        func.count(Payment.id).label('count'),
        func.sum(Invoice.total_value).label('total')
    ).join(Payment.invoice).filter(
        Payment.status == 'PAID',
        Payment.paid_at >= twelve_months_ago
    ).group_by('month').order_by('month').all()
    
    return render_template('finance/reports.html',
                         payments_by_status=payments_by_status,
                         payments_by_month=payments_by_month)

