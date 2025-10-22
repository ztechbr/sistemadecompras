"""
Modelo de Log de Auditoria
"""
from datetime import datetime
from app import db

class AuditLog(db.Model):
    """Modelo de log de auditoria"""
    
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(50), nullable=True)
    record_id = db.Column(db.Integer, nullable=True)
    old_values = db.Column(db.JSON, nullable=True)
    new_values = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relacionamento
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.id} - {self.action}>'
    
    @staticmethod
    def log_action(user_id, action, table_name=None, record_id=None, 
                   old_values=None, new_values=None, ip_address=None, user_agent=None):
        """Registra uma ação no log de auditoria"""
        log = AuditLog(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log)
        db.session.commit()
        return log
    
    def to_dict(self):
        """Converte o log para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Sistema',
            'action': self.action,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat()
        }

