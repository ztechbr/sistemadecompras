"""
Modelo de parâmetro do sistema
"""
from datetime import datetime
from app import db

class SystemParameter(db.Model):
    """Modelo de parâmetro do sistema"""
    __tablename__ = 'system_parameters'
    
    id = db.Column(db.Integer, primary_key=True)
    param_key = db.Column(db.String(100), unique=True, nullable=False)
    param_value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemParameter {self.param_key}>'