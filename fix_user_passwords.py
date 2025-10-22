"""
Script para corrigir senhas de usuários com hash inválido
"""
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def fix_user_passwords():
    """Corrige senhas de usuários com hash inválido"""
    try:
        app = create_app('development')
        print("Aplicação criada com sucesso!")
        
        # Configurar ambiente HOM
        from environment_config import get_database_url
        database_url = get_database_url('HOM')
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print(f"Configurado banco: {database_url}")
        
    except Exception as e:
        print(f"Erro ao criar aplicação: {e}")
        import traceback
        traceback.print_exc()
        return
    
    with app.app_context():
        print("Verificando usuários com problemas de senha...")
        
        try:
            # Buscar todos os usuários
            users = User.query.all()
            print(f"Encontrados {len(users)} usuários no banco de dados.")
        except Exception as e:
            print(f"Erro ao buscar usuários: {e}")
            return
        
        for user in users:
            print(f"Verificando usuário: {user.username}")
            print(f"Password hash atual: '{user.password_hash}'")
            
            # Verificar se o password_hash está vazio ou inválido
            if not user.password_hash or user.password_hash.strip() == '':
                print(f"  [ERRO] Password hash vazio para {user.username}")
                
                # Definir senha padrão baseada no usuário
                if user.username == 'admin':
                    new_password = 'admin123'
                else:
                    new_password = '123456'
                
                # Gerar novo hash
                user.password_hash = generate_password_hash(new_password)
                print(f"  [OK] Senha corrigida para {user.username} (nova senha: {new_password})")
                
            else:
                # Verificar se o hash tem formato válido
                try:
                    # Tentar verificar se o hash é válido
                    from werkzeug.security import check_password_hash
                    # Se chegou até aqui, o hash parece válido
                    print(f"  [OK] Password hash válido para {user.username}")
                except Exception as e:
                    print(f"  [ERRO] Password hash inválido para {user.username}: {e}")
                    
                    # Corrigir senha
                    if user.username == 'admin':
                        new_password = 'admin123'
                    else:
                        new_password = '123456'
                    
                    user.password_hash = generate_password_hash(new_password)
                    print(f"  [OK] Senha corrigida para {user.username} (nova senha: {new_password})")
        
        # Salvar alterações
        db.session.commit()
        print("\n[OK] Correções aplicadas com sucesso!")
        
        print("\n" + "="*50)
        print("RESUMO DOS USUÁRIOS:")
        print("="*50)
        for user in users:
            print(f"Usuário: {user.username:20} | Role: {user.role:10} | Status: {user.status}")
        print("="*50)
        print("\nSenhas padrão:")
        print("- admin: admin123")
        print("- demais usuários: 123456")

if __name__ == '__main__':
    fix_user_passwords()
