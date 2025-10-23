"""
Modelo de solicitação de compra
"""
from datetime import datetime
from decimal import Decimal
from app import db

class PurchaseRequest(db.Model):
    """Modelo de solicitação de compra"""
    __tablename__ = 'purchase_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(20), nullable=False, default='UN')
    justification = db.Column(db.Text, nullable=False)
    estimated_total = db.Column(db.Numeric(15, 2))
    status = db.Column(db.String(30), nullable=False, default='PENDING')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime)
    rejected_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    rejected_at = db.Column(db.DateTime)
    rejected_reason = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    requester = db.relationship('User', foreign_keys=[user_id])
    product = db.relationship('Product')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_requests')
    rejector = db.relationship('User', foreign_keys=[rejected_by], backref='rejected_requests')
    quotations = db.relationship('Quotation', backref='purchase_request', lazy='dynamic')
    purchase_orders = db.relationship('PurchaseOrder', backref='purchase_request', lazy=True)
    
    @property
    def department(self):
        """Retorna o departamento do usuário que fez a requisição"""
        return self.requester.department if self.requester else None
    
    def __repr__(self):
        return f'<PurchaseRequest {self.request_number}>'
    
    def is_pending(self):
        """Verifica se a solicitação está pendente"""
        return self.status == 'PENDING'
    
    def is_approved(self):
        """Verifica se a solicitação foi aprovada"""
        return self.status == 'APPROVED'
    
    def is_rejected(self):
        """Verifica se a solicitação foi rejeitada"""
        return self.status == 'REJECTED'
    
    def is_in_quotation(self):
        """Verifica se está em cotação"""
        return self.status == 'IN_QUOTATION'
    
    def get_status_label(self):
        """Retorna o label do status"""
        labels = {
            'PENDING': 'Aguardando Aprovação',
            'APPROVED': 'Aprovada',
            'REJECTED': 'Rejeitada',
            'IN_QUOTATION': 'Em Cotação',
            'EM_COTACAO': 'Em Cotação',  # Status antigo
            'QUOTED': 'Cotada',
            'VENDOR_APPROVED': 'Fornecedor Aprovado',
            'PURCHASED': 'Comprada',
            'INVOICE_RECEIVED': 'Nota Fiscal Recebida',
            'PAYMENT_RELEASED': 'Pagamento Liberado',
            'PAID': 'Paga',
            'CANCELLED': 'Cancelada'
        }
        return labels.get(self.status, self.status)
    
    def get_status_color(self):
        """Retorna a cor do status"""
        colors = {
            'PENDING': 'yellow',
            'APPROVED': 'green',
            'REJECTED': 'red',
            'IN_QUOTATION': 'blue',
            'EM_COTACAO': 'blue',  # Status antigo
            'QUOTED': 'purple',
            'VENDOR_APPROVED': 'green',
            'PURCHASED': 'green',
            'INVOICE_RECEIVED': 'blue',
            'PAYMENT_RELEASED': 'orange',
            'PAID': 'green',
            'CANCELLED': 'red'
        }
        return colors.get(self.status, 'gray')
    
    @staticmethod
    def generate_request_number():
        """Gera número único para requisição"""
        now = datetime.now()
        year_month = now.strftime('%Y%m')
        
        # Busca o último número do mês
        last_request = PurchaseRequest.query.filter(
            PurchaseRequest.request_number.like(f'RC-{year_month}-%')
        ).order_by(PurchaseRequest.request_number.desc()).first()
        
        if last_request:
            last_number = int(last_request.request_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f'RC-{year_month}-{new_number:04d}'
    
    @classmethod
    def get_pending_requests(cls):
        """Retorna todas as requisições pendentes"""
        return cls.query.filter_by(status='PENDING').order_by(cls.created_at).all()
    
    @classmethod
    def get_approved_requests(cls):
        """Retorna todas as requisições aprovadas"""
        return cls.query.filter_by(status='APPROVED').order_by(cls.created_at).all()
    
    @classmethod
    def get_rejected_requests(cls):
        """Retorna todas as requisições rejeitadas"""
        return cls.query.filter_by(status='REJECTED').order_by(cls.created_at).all()
    
    def can_be_approved_by(self, user):
        """Verifica se o usuário pode aprovar esta requisição"""
        return (self.status == 'PENDING' and 
                user.role in ['MANAGER', 'ADMIN'] and
                self.requester.department_id == user.department_id)
    
    def approve(self, user):
        """Aprova a requisição"""
        self.status = 'APPROVED'
        self.approved_by = user.id
        self.approved_at = datetime.utcnow()
        db.session.commit()
    
    def reject(self, user, reason):
        """Rejeita a requisição"""
        self.status = 'REJECTED'
        self.rejected_by = user.id
        self.rejected_at = datetime.utcnow()
        self.rejected_reason = reason
        db.session.commit()