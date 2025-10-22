"""
Modelo de produto
"""
from datetime import datetime
from decimal import Decimal
from app import db

class Product(db.Model):
    """Modelo de produto"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    average_unit_value = db.Column(db.Numeric(15, 2), default=Decimal('0.00'))
    status = db.Column(db.String(20), nullable=False, default='ATIVO')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    purchase_requests = db.relationship('PurchaseRequest', backref='product_ref', lazy='dynamic')
    
    def __repr__(self):
        return f'<Product {self.sku} - {self.product_name}>'
    
    def is_active(self):
        """Verifica se o produto está ativo"""
        return self.status == 'ATIVO'
    
    @classmethod
    def get_active_products(cls):
        """Retorna todos os produtos ativos"""
        return cls.query.filter_by(status='ATIVO').order_by(cls.product_name).all()
    
    @property
    def name(self):
        """Alias para product_name para compatibilidade"""
        return self.product_name