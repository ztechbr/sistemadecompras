"""
Modelo de nota fiscal
"""
from datetime import datetime
from decimal import Decimal
from app import db

class Invoice(db.Model):
    """Modelo de nota fiscal"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), nullable=False)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    vendor_cnpj = db.Column(db.String(18), nullable=False)
    total_value = db.Column(db.Numeric(15, 2), nullable=False)
    informed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    informed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    informer = db.relationship('User', foreign_keys=[informed_by], backref='created_invoices')
    payments = db.relationship('Payment', backref='invoice', lazy=True)
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
    
    @classmethod
    def get_pending_invoices(cls):
        """Retorna todas as notas fiscais pendentes"""
        return cls.query.filter_by(status='PENDING').order_by(cls.created_at).all()
    
    @classmethod
    def get_approved_invoices(cls):
        """Retorna todas as notas fiscais aprovadas"""
        return cls.query.filter_by(status='APPROVED').order_by(cls.created_at).all()
    
    @classmethod
    def get_rejected_invoices(cls):
        """Retorna todas as notas fiscais rejeitadas"""
        return cls.query.filter_by(status='REJECTED').order_by(cls.created_at).all()
    
    @classmethod
    def get_invoices_by_order(cls, order_id):
        """Retorna todas as notas fiscais de um pedido"""
        return cls.query.filter_by(purchase_order_id=order_id).order_by(cls.created_at).all()
