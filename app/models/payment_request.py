"""
Modelo de solicitação de pagamento
"""
from datetime import datetime
from decimal import Decimal
from app import db

class PaymentRequest(db.Model):
    """Modelo de solicitação de pagamento"""
    __tablename__ = 'payment_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(20), unique=True, nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    approved_value = db.Column(db.Numeric(15, 2), nullable=False)
    cost_center = db.Column(db.String(100), nullable=True)
    accounting_account = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(30), nullable=False, default='AGUARDANDO_PAGAMENTO')
    payment_date = db.Column(db.Date, nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    creator = db.relationship('User', backref='created_payment_requests')
    invoice = db.relationship('Invoice', backref='payment_requests')
    purchase_order = db.relationship('PurchaseOrder', backref='payment_requests')
    
    def __repr__(self):
        return f'<PaymentRequest {self.request_number}>'
    
    def get_status_label(self):
        """Retorna o label do status"""
        labels = {
            'AGUARDANDO_PAGAMENTO': 'Aguardando Pagamento',
            'PAGO': 'Pago',
            'CANCELADO': 'Cancelado'
        }
        return labels.get(self.status, self.status)
    
    def get_status_color(self):
        """Retorna a cor do status"""
        colors = {
            'AGUARDANDO_PAGAMENTO': 'yellow',
            'PAGO': 'green',
            'CANCELADO': 'red'
        }
        return colors.get(self.status, 'gray')
    
    @staticmethod
    def generate_request_number():
        """Gera número único para solicitação de pagamento"""
        now = datetime.now()
        year_month = now.strftime('%Y%m')
        
        # Busca o último número do mês
        last_request = PaymentRequest.query.filter(
            PaymentRequest.request_number.like(f'SP-{year_month}-%')
        ).order_by(PaymentRequest.request_number.desc()).first()
        
        if last_request:
            last_number = int(last_request.request_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f'SP-{year_month}-{new_number:04d}'
    
    @classmethod
    def get_pending_requests(cls):
        """Retorna todas as solicitações pendentes"""
        return cls.query.filter_by(status='AGUARDANDO_PAGAMENTO').order_by(cls.created_at).all()
    
    @classmethod
    def get_paid_requests(cls):
        """Retorna todas as solicitações pagas"""
        return cls.query.filter_by(status='PAGO').order_by(cls.created_at).all()
    
    @classmethod
    def get_cancelled_requests(cls):
        """Retorna todas as solicitações canceladas"""
        return cls.query.filter_by(status='CANCELADO').order_by(cls.created_at).all()
    
    @classmethod
    def get_requests_by_invoice(cls, invoice_id):
        """Retorna todas as solicitações de uma nota fiscal"""
        return cls.query.filter_by(invoice_id=invoice_id).order_by(cls.created_at).all()
    
    @classmethod
    def get_requests_by_order(cls, order_id):
        """Retorna todas as solicitações de um pedido"""
        return cls.query.filter_by(purchase_order_id=order_id).order_by(cls.created_at).all()

