"""
Modelo de cotação
"""
from datetime import datetime
from decimal import Decimal
from app import db

class Quotation(db.Model):
    """Modelo de cotação"""
    __tablename__ = 'quotations'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_request_id = db.Column(db.Integer, db.ForeignKey('purchase_requests.id'), nullable=False)
    purchaser_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='DRAFT')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    released_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Quotation {self.id} - Request {self.purchase_request_id}>'
    
    def get_status_label(self):
        """Retorna o label do status"""
        labels = {
            'DRAFT': 'Rascunho',
            'RELEASED': 'Liberada',
            'APPROVED': 'Aprovada',
            'CANCELLED': 'Cancelada'
        }
        return labels.get(self.status, self.status)
    
    def get_status_color(self):
        """Retorna a cor do status"""
        colors = {
            'DRAFT': 'gray',
            'RELEASED': 'blue',
            'APPROVED': 'green',
            'CANCELLED': 'red'
        }
        return colors.get(self.status, 'gray')
    
    @classmethod
    def get_draft_quotations(cls):
        """Retorna todas as cotações em rascunho"""
        return cls.query.filter_by(status='DRAFT').order_by(cls.created_at).all()
    
    @classmethod
    def get_released_quotations(cls):
        """Retorna todas as cotações liberadas"""
        return cls.query.filter_by(status='RELEASED').order_by(cls.created_at).all()
    
    @classmethod
    def get_approved_quotations(cls):
        """Retorna todas as cotações aprovadas"""
        return cls.query.filter_by(status='APPROVED').order_by(cls.created_at).all()
    
    @classmethod
    def get_quotations_by_request(cls, request_id):
        """Retorna todas as cotações de uma requisição"""
        return cls.query.filter_by(purchase_request_id=request_id).order_by(cls.created_at).all()
    
    def approve(self, user, selected_item_id):
        """Aprova a cotação selecionando um fornecedor"""
        self.status = 'APPROVED'
        self.approved_by = user.id
        self.approved_at = datetime.utcnow()
        
        # Marcar o item selecionado
        from ..models import QuotationItem
        selected_item = QuotationItem.query.get(selected_item_id)
        if selected_item:
            selected_item.is_selected = True
        
        db.session.commit()
    
    def cancel(self):
        """Cancela a cotação"""
        self.status = 'CANCELLED'
        db.session.commit()
    
    def get_sorted_items(self):
        """Retorna os itens da cotação ordenados por valor"""
        from ..models import QuotationItem
        return QuotationItem.query.filter_by(quotation_id=self.id).order_by(QuotationItem.total_value.asc()).all()