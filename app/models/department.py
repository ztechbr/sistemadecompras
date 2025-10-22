"""
Modelo de departamento
"""
from datetime import datetime
from app import db

class Department(db.Model):
    """Modelo de departamento"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='ATIVO')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Department {self.name}>'
    
    def is_active(self):
        """Verifica se o departamento está ativo"""
        return self.status == 'ATIVO'
    
    @classmethod
    def get_active_departments(cls):
        """Retorna todos os departamentos ativos"""
        return cls.query.filter_by(status='ATIVO').order_by(cls.name).all()