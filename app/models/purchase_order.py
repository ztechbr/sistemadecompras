"""
Modelo de pedido de compra
"""
from datetime import datetime
from decimal import Decimal
from app import db

class PurchaseOrder(db.Model):
    """Modelo de pedido de compra"""
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    purchase_request_id = db.Column(db.Integer, db.ForeignKey('purchase_requests.id'), nullable=False)
    quotation_item_id = db.Column(db.Integer, db.ForeignKey('quotation_items.id'), nullable=False)
    purchaser_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pdf_path = db.Column(db.String(500))
    status = db.Column(db.String(20), nullable=False, default='CREATED')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    purchaser = db.relationship('User', foreign_keys=[purchaser_id], backref='created_purchase_orders')
    invoices = db.relationship('Invoice', backref='purchase_order', lazy=True)
    
    def __repr__(self):
        return f'<PurchaseOrder {self.order_number}>'
    
    def get_status_label(self):
        """Retorna o label do status"""
        labels = {
            'CREATED': 'Criado',
            'SENT': 'Enviado',
            'CONFIRMED': 'Confirmado',
            'CANCELLED': 'Cancelado'
        }
        return labels.get(self.status, self.status)
    
    def get_status_color(self):
        """Retorna a cor do status"""
        colors = {
            'CREATED': 'blue',
            'SENT': 'orange',
            'CONFIRMED': 'green',
            'CANCELLED': 'red'
        }
        return colors.get(self.status, 'gray')
    
    @classmethod
    def get_created_orders(cls):
        """Retorna todos os pedidos criados"""
        return cls.query.filter_by(status='CREATED').order_by(cls.created_at).all()
    
    @classmethod
    def get_sent_orders(cls):
        """Retorna todos os pedidos enviados"""
        return cls.query.filter_by(status='SENT').order_by(cls.created_at).all()
    
    @classmethod
    def get_confirmed_orders(cls):
        """Retorna todos os pedidos confirmados"""
        return cls.query.filter_by(status='CONFIRMED').order_by(cls.created_at).all()
    
    @classmethod
    def get_cancelled_orders(cls):
        """Retorna todos os pedidos cancelados"""
        return cls.query.filter_by(status='CANCELLED').order_by(cls.created_at).all()
    