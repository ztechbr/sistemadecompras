"""
Ponto de entrada da aplicação Flask
"""
import os
from app import create_app, db
from app.models import User, Department, Product, PurchaseRequest, Quotation, QuotationItem, PurchaseOrder, Invoice, Payment

# Criar aplicação
app = create_app(os.getenv('FLASK_ENV') or 'development')

# Context para shell
@app.shell_context_processor
def make_shell_context():
    """Adiciona objetos ao contexto do shell Flask"""
    return {
        'db': db,
        'User': User,
        'Department': Department,
        'Product': Product,
        'PurchaseRequest': PurchaseRequest,
        'Quotation': Quotation,
        'QuotationItem': QuotationItem,
        'PurchaseOrder': PurchaseOrder,
        'Invoice': Invoice,
        'Payment': Payment
    }

# Comando CLI para criar usuário admin
@app.cli.command()
def create_admin():
    """Cria um usuário administrador"""
    from app.models import User, Department
    from werkzeug.security import generate_password_hash
    
    # Verificar se já existe admin
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print('Usuário admin já existe!')
        return
    
    # Buscar ou criar departamento
    dept = Department.query.filter_by(name='Administração').first()
    if not dept:
        dept = Department(name='Administração', status='ATIVO')
        db.session.add(dept)
        db.session.commit()
    
    # Criar admin
    admin = User(
        username='admin',
        email='admin@empresa.com',
        password_hash=generate_password_hash('admin123'),
        role='ADMIN',
        department_id=dept.id,
        status='ATIVO'
    )
    
    db.session.add(admin)
    db.session.commit()
    
    print('Usuário admin criado com sucesso!')
    print('Username: admin')
    print('Password: admin123')

# Comando CLI para inicializar banco
@app.cli.command()
def init_db():
    """Inicializa o banco de dados"""
    db.create_all()
    print('Banco de dados inicializado!')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

