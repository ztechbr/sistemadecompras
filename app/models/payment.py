"""
Modelo de pagamento
"""
from datetime import datetime
from decimal import Decimal
from app import db

class Payment(db.Model):
    """Modelo de pagamento"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='PENDING')
    released_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    released_at = db.Column(db.DateTime)
    paid_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    paid_at = db.Column(db.DateTime)
    payment_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.id} - Invoice {self.invoice_id}>'
    
    @classmethod
    def get_pending_payments(cls):
        """Retorna todos os pagamentos pendentes"""
        return cls.query.filter_by(status='PENDING').order_by(cls.created_at).all()
    
    @classmethod
    def get_released_payments(cls):
        """Retorna todos os pagamentos liberados"""
        return cls.query.filter_by(status='RELEASED').order_by(cls.created_at).all()
    
    @classmethod
    def get_paid_payments(cls):
        """Retorna todos os pagamentos pagos"""
        return cls.query.filter_by(status='PAID').order_by(cls.created_at).all()
    
    @classmethod
    def get_cancelled_payments(cls):
        """Retorna todos os pagamentos cancelados"""
        return cls.query.filter_by(status='CANCELLED').order_by(cls.created_at).all()
    
    @classmethod
    def get_payments_by_invoice(cls, invoice_id):
        """Retorna todos os pagamentos de uma nota fiscal"""
        return cls.query.filter_by(invoice_id=invoice_id).order_by(cls.created_at).all()
    
    def release(self, user):
        """Libera o pagamento"""
        self.status = 'RELEASED'
        self.released_by = user.id
        self.released_at = datetime.utcnow()
        db.session.commit()