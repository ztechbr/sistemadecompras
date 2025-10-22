"""
Script para inicializar o banco de dados com dados de exemplo
"""
from app import create_app, db
from app.models import User, Department, Product
from werkzeug.security import generate_password_hash

def init_sample_data():
    """Inicializa o banco com dados de exemplo"""
    app = create_app('development')
    
    with app.app_context():
        print("Criando tabelas...")
        db.create_all()
        
        print("Criando departamentos...")
        departments = [
            Department(name='Tecnologia da Informação', status='ATIVO'),
            Department(name='Recursos Humanos', status='ATIVO'),
            Department(name='Financeiro', status='ATIVO'),
            Department(name='Operações', status='ATIVO'),
            Department(name='Comercial', status='ATIVO'),
        ]
        
        for dept in departments:
            if not Department.query.filter_by(name=dept.name).first():
                db.session.add(dept)
        
        db.session.commit()
        
        print("Criando usuários...")
        ti_dept = Department.query.filter_by(name='Tecnologia da Informação').first()
        rh_dept = Department.query.filter_by(name='Recursos Humanos').first()
        fin_dept = Department.query.filter_by(name='Financeiro').first()
        
        users = [
            User(username='admin', email='admin@empresa.com', 
                 password_hash=generate_password_hash('admin123'),
                 role='ADMIN', department_id=ti_dept.id, status='ATIVO'),
            User(username='gerente_ti', email='gerente.ti@empresa.com',
                 password_hash=generate_password_hash('123456'),
                 role='MANAGER', department_id=ti_dept.id, status='ATIVO'),
            User(username='gerente_rh', email='gerente.rh@empresa.com',
                 password_hash=generate_password_hash('123456'),
                 role='MANAGER', department_id=rh_dept.id, status='ATIVO'),
            User(username='usuario_ti', email='usuario.ti@empresa.com',
                 password_hash=generate_password_hash('123456'),
                 role='USER', department_id=ti_dept.id, status='ATIVO'),
            User(username='usuario_rh', email='usuario.rh@empresa.com',
                 password_hash=generate_password_hash('123456'),
                 role='USER', department_id=rh_dept.id, status='ATIVO'),
            User(username='comprador', email='comprador@empresa.com',
                 password_hash=generate_password_hash('123456'),
                 role='PURCHASER', department_id=None, status='ATIVO'),
            User(username='financeiro', email='financeiro@empresa.com',
                 password_hash=generate_password_hash('123456'),
                 role='FINANCE', department_id=fin_dept.id, status='ATIVO'),
        ]
        
        for user in users:
            if not User.query.filter_by(username=user.username).first():
                db.session.add(user)
        
        db.session.commit()
        
        print("Criando produtos...")
        products = [
            Product(sku='SKU-001', product_name='Mouse USB', 
                   description='Mouse óptico USB com fio', 
                   average_unit_value=25.00, status='ATIVO'),
            Product(sku='SKU-002', product_name='Teclado USB',
                   description='Teclado padrão ABNT2 USB',
                   average_unit_value=45.00, status='ATIVO'),
            Product(sku='SKU-003', product_name='Monitor 24"',
                   description='Monitor LED 24 polegadas Full HD',
                   average_unit_value=650.00, status='ATIVO'),
            Product(sku='SKU-004', product_name='Cadeira Escritório',
                   description='Cadeira giratória com apoio lombar',
                   average_unit_value=450.00, status='ATIVO'),
            Product(sku='SKU-005', product_name='Notebook',
                   description='Notebook i5 8GB RAM 256GB SSD',
                   average_unit_value=3200.00, status='ATIVO'),
            Product(sku='SKU-006', product_name='Impressora Laser',
                   description='Impressora laser monocromática',
                   average_unit_value=850.00, status='ATIVO'),
            Product(sku='SKU-007', product_name='Papel A4',
                   description='Resma papel sulfite A4 com 500 folhas',
                   average_unit_value=22.00, status='ATIVO'),
            Product(sku='SKU-008', product_name='Caneta Esferográfica',
                   description='Caneta esferográfica azul',
                   average_unit_value=1.50, status='ATIVO'),
        ]
        
        for product in products:
            if not Product.query.filter_by(sku=product.sku).first():
                db.session.add(product)
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("Banco de dados inicializado com sucesso!")
        print("="*50)
        print("\nUsuários criados:")
        print("-" * 50)
        for user in users:
            print(f"Usuário: {user.username:20} | Role: {user.role:10} | Senha: 123456" if user.username != 'admin' else f"Usuário: {user.username:20} | Role: {user.role:10} | Senha: admin123")
        print("-" * 50)
        print(f"\nDepartamentos: {len(departments)}")
        print(f"Produtos: {len(products)}")
        print("\nAcesse: http://localhost:5000")
        print("="*50)

if __name__ == '__main__':
    init_sample_data()

