"""
Modelo de usuário
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

class User(UserMixin, db.Model):
    """Modelo de usuário"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='ATIVO')
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    department = db.relationship('Department', backref='users')
    purchase_requests = db.relationship('PurchaseRequest', foreign_keys='PurchaseRequest.user_id', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Define a senha do usuário"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def is_active(self):
        """Verifica se o usuário está ativo"""
        return self.status == 'ATIVO'
    
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.role == 'ADMIN'
    
    def is_manager(self):
        """Verifica se o usuário é gerente"""
        return self.role == 'MANAGER'
    
    def is_purchaser(self):
        """Verifica se o usuário é comprador"""
        return self.role == 'PURCHASER'
    
    def is_finance(self):
        """Verifica se o usuário é do financeiro"""
        return self.role == 'FINANCE'
    
    def update_last_login(self):
        """Atualiza o último login do usuário"""
        self.last_login = datetime.utcnow()
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def get_active_users(cls):
        """Retorna todos os usuários ativos"""
        return cls.query.filter_by(status='ATIVO').order_by(cls.username).all()
    
    @property
    def name(self):
        """Alias para username para compatibilidade"""
        return self.username