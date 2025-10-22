"""
Rotas do administrador
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import User, Department, Product, SystemParameter, PurchaseRequest
from ..utils.decorators import login_required_only
from werkzeug.security import generate_password_hash
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required_only
def dashboard():
    """Dashboard do administrador"""
    # Estatísticas gerais
    total_users = User.query.count()
    active_users = User.query.filter_by(status='ATIVO').count()
    total_departments = Department.query.count()
    total_products = Product.query.filter_by(status='ATIVO').count()
    total_requests = PurchaseRequest.query.count()
    
    # Requisições por status
    requests_by_status = db.session.query(
        PurchaseRequest.status,
        func.count(PurchaseRequest.id)
    ).group_by(PurchaseRequest.status).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         active_users=active_users,
                         total_departments=total_departments,
                         total_products=total_products,
                         total_requests=total_requests,
                         requests_by_status=requests_by_status)

# ==================== USUÁRIOS ====================

@admin_bp.route('/users')
@login_required
@login_required_only
def users():
    """Lista de usuários"""
    users = User.query.order_by(User.created_at.desc()).all()
    departments = Department.get_active_departments()
    return render_template('admin/users.html', users=users, departments=departments)

@admin_bp.route('/users/create', methods=['POST'])
@login_required
@login_required_only
def create_user():
    """Criar novo usuário"""
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        department_id = request.form.get('department_id')
        status = request.form.get('status', 'ATIVO')
        
        # Validações
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.', 'danger')
            return redirect(url_for('admin.users'))
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'danger')
            return redirect(url_for('admin.users'))
        
        # Criar usuário
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            department_id=int(department_id) if department_id else None,
            status=status
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Usuário {username} criado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar usuário: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@login_required
@login_required_only
def edit_user(user_id):
    """Editar usuário"""
    try:
        user = User.query.get_or_404(user_id)
        
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        department_id = request.form.get('department_id')
        user.department_id = int(department_id) if department_id else None
        user.status = request.form.get('status')
        
        # Atualizar senha se fornecida
        password = request.form.get('password')
        if password:
            user.password_hash = generate_password_hash(password)
        
        db.session.commit()
        flash(f'Usuário {user.username} atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar usuário: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@login_required_only
def delete_user(user_id):
    """Deletar usuário"""
    try:
        user = User.query.get_or_404(user_id)
        
        if user.id == current_user.id:
            flash('Você não pode deletar seu próprio usuário.', 'danger')
            return redirect(url_for('admin.users'))
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        flash(f'Usuário {username} deletado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar usuário: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))

# ==================== DEPARTAMENTOS ====================

@admin_bp.route('/departments')
@login_required
@login_required_only
def departments():
    """Lista de departamentos"""
    departments = Department.query.order_by(Department.name).all()
    return render_template('admin/departments.html', departments=departments)

@admin_bp.route('/departments/create', methods=['POST'])
@login_required
@login_required_only
def create_department():
    """Criar novo departamento"""
    try:
        name = request.form.get('name')
        status = request.form.get('status', 'ATIVO')
        
        if Department.query.filter_by(name=name).first():
            flash('Departamento já existe.', 'danger')
            return redirect(url_for('admin.departments'))
        
        department = Department(name=name, status=status)
        db.session.add(department)
        db.session.commit()
        
        flash(f'Departamento {name} criado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar departamento: {str(e)}', 'danger')
    
    return redirect(url_for('admin.departments'))

@admin_bp.route('/departments/<int:dept_id>/edit', methods=['POST'])
@login_required
@login_required_only
def edit_department(dept_id):
    """Editar departamento"""
    try:
        department = Department.query.get_or_404(dept_id)
        department.name = request.form.get('name')
        department.status = request.form.get('status')
        
        db.session.commit()
        flash(f'Departamento atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar departamento: {str(e)}', 'danger')
    
    return redirect(url_for('admin.departments'))

# ==================== PRODUTOS ====================

@admin_bp.route('/products')
@login_required
@login_required_only
def products():
    """Lista de produtos"""
    products = Product.query.order_by(Product.product_name).all()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/products/create', methods=['POST'])
@login_required
@login_required_only
def create_product():
    """Criar novo produto"""
    try:
        sku = request.form.get('sku')
        product_name = request.form.get('product_name')
        description = request.form.get('description')
        average_unit_value = request.form.get('average_unit_value', 0)
        status = request.form.get('status', 'ATIVO')
        
        if Product.query.filter_by(sku=sku).first():
            flash('SKU já existe.', 'danger')
            return redirect(url_for('admin.products'))
        
        product = Product(
            sku=sku,
            product_name=product_name,
            description=description,
            average_unit_value=float(average_unit_value),
            status=status
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash(f'Produto {product_name} criado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar produto: {str(e)}', 'danger')
    
    return redirect(url_for('admin.products'))

@admin_bp.route('/products/<int:product_id>/edit', methods=['POST'])
@login_required
@login_required_only
def edit_product(product_id):
    """Editar produto"""
    try:
        product = Product.query.get_or_404(product_id)
        
        product.product_name = request.form.get('product_name')
        product.description = request.form.get('description')
        product.average_unit_value = float(request.form.get('average_unit_value', 0))
        product.status = request.form.get('status')
        
        db.session.commit()
        flash(f'Produto atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar produto: {str(e)}', 'danger')
    
    return redirect(url_for('admin.products'))

# ==================== PARÂMETROS ====================

@admin_bp.route('/parameters')
@login_required
@login_required_only
def parameters():
    """Lista de parâmetros do sistema"""
    parameters = SystemParameter.query.order_by(SystemParameter.param_key).all()
    return render_template('admin/parameters.html', parameters=parameters)

@admin_bp.route('/parameters/<int:param_id>/edit', methods=['POST'])
@login_required
@login_required_only
def edit_parameter(param_id):
    """Editar parâmetro"""
    try:
        parameter = SystemParameter.query.get_or_404(param_id)
        parameter.param_value = request.form.get('param_value')
        parameter.updated_by = current_user.id
        
        db.session.commit()
        flash('Parâmetro atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar parâmetro: {str(e)}', 'danger')
    
    return redirect(url_for('admin.parameters'))

