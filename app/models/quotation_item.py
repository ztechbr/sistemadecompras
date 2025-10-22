"""
Modelo de item de cotação
"""
from datetime import datetime
from decimal import Decimal
from app import db

class QuotationItem(db.Model):
    """Modelo de item de cotação"""
    __tablename__ = 'quotation_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotations.id'), nullable=False)
    vendor_name = db.Column(db.String(200), nullable=False)
    vendor_cnpj = db.Column(db.String(18))
    description = db.Column(db.Text)
    unit_value = db.Column(db.Numeric(15, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_value = db.Column(db.Numeric(15, 2), nullable=False)
    is_selected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    quotation = db.relationship('Quotation', backref='quotation_items')
    purchase_orders = db.relationship('PurchaseOrder', backref='quotation_item')
    
    def __repr__(self):
        return f'<QuotationItem {self.id} - {self.vendor_name}>'
    
    def calculate_total(self):
        """Calcula o valor total do item"""
        return Decimal(str(self.unit_value)) * self.quantity
    
    def is_vendor_selected(self):
        """Verifica se este fornecedor foi selecionado"""
        return self.is_selected
    
    @staticmethod
    def get_selected_items():
        """Retorna itens selecionados"""
        return QuotationItem.query.filter_by(is_selected=True).all()
    
    @staticmethod
    def get_by_vendor_cnpj(cnpj):
        """Retorna itens por CNPJ do fornecedor"""
        return QuotationItem.query.filter_by(vendor_cnpj=cnpj).all()
