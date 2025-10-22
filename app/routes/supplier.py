"""
Rotas de fornecedores (baseado em QuotationItem)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import QuotationItem
from ..utils.decorators import login_required_only
from sqlalchemy import distinct, func

supplier_bp = Blueprint('supplier', __name__, url_prefix='/suppliers')

@supplier_bp.route('/')
@login_required
@login_required_only
def index():
    """Lista de fornecedores únicos baseado nos QuotationItems"""
    # Buscar fornecedores únicos pelos dados dos QuotationItems
    suppliers_data = db.session.query(
        QuotationItem.vendor_name,
        QuotationItem.vendor_cnpj,
        func.count(QuotationItem.id).label('total_quotations'),
        func.max(QuotationItem.created_at).label('last_quote_date')
    ).filter(
        QuotationItem.vendor_name.isnot(None),
        QuotationItem.vendor_name != ''
    ).group_by(
        QuotationItem.vendor_name,
        QuotationItem.vendor_cnpj
    ).order_by(QuotationItem.vendor_name).all()
    
    return render_template('supplier/index.html', suppliers=suppliers_data)

@supplier_bp.route('/create', methods=['GET', 'POST'])
@login_required
@login_required_only
def create():
    """Criar novo fornecedor (será usado quando criar QuotationItem)"""
    if request.method == 'POST':
        try:
            vendor_name = request.form.get('vendor_name')
            vendor_cnpj = request.form.get('vendor_cnpj')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            contact_person = request.form.get('contact_person')
            
            # Verificar se já existe fornecedor com mesmo nome ou CNPJ
            existing_by_name = db.session.query(QuotationItem).filter_by(vendor_name=vendor_name).first()
            if existing_by_name:
                flash('Fornecedor com este nome já existe.', 'warning')
                return redirect(url_for('supplier.index'))
            
            if vendor_cnpj:
                existing_by_cnpj = db.session.query(QuotationItem).filter_by(vendor_cnpj=vendor_cnpj).first()
                if existing_by_cnpj:
                    flash('CNPJ já cadastrado.', 'warning')
                    return redirect(url_for('supplier.index'))
            
            # Criar um QuotationItem temporário para "cadastrar" o fornecedor
            # Isso será usado como referência para futuras cotações
            temp_quotation_item = QuotationItem(
                quotation_id=None,  # Será definido quando criar cotação real
                vendor_name=vendor_name,
                vendor_cnpj=vendor_cnpj,
                description=f"Fornecedor cadastrado: {contact_person or 'N/A'}",
                unit_value=0,
                quantity=0,
                total_value=0,
                is_selected=False
            )
            
            db.session.add(temp_quotation_item)
            db.session.commit()
            
            flash(f'Fornecedor {vendor_name} cadastrado com sucesso!', 'success')
            return redirect(url_for('supplier.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar fornecedor: {str(e)}', 'danger')
    
    return render_template('supplier/create.html')

@supplier_bp.route('/<vendor_name>/edit', methods=['GET', 'POST'])
@login_required
@login_required_only
def edit(vendor_name):
    """Editar fornecedor"""
    if request.method == 'POST':
        try:
            new_name = request.form.get('vendor_name')
            new_cnpj = request.form.get('vendor_cnpj')
            
            # Buscar todos os QuotationItems deste fornecedor
            quotation_items = QuotationItem.query.filter_by(vendor_name=vendor_name).all()
            
            if not quotation_items:
                flash('Fornecedor não encontrado.', 'danger')
                return redirect(url_for('supplier.index'))
            
            # Verificar se novo nome ou CNPJ já existem
            if new_name != vendor_name:
                existing = QuotationItem.query.filter_by(vendor_name=new_name).first()
                if existing:
                    flash('Fornecedor com este nome já existe.', 'danger')
                    return redirect(url_for('supplier.edit', vendor_name=vendor_name))
            
            if new_cnpj:
                existing_cnpj = QuotationItem.query.filter_by(vendor_cnpj=new_cnpj).first()
                if existing_cnpj and existing_cnpj.vendor_name != vendor_name:
                    flash('CNPJ já cadastrado.', 'danger')
                    return redirect(url_for('supplier.edit', vendor_name=vendor_name))
            
            # Atualizar todos os QuotationItems deste fornecedor
            for item in quotation_items:
                item.vendor_name = new_name
                item.vendor_cnpj = new_cnpj
            
            db.session.commit()
            flash(f'Fornecedor atualizado com sucesso!', 'success')
            return redirect(url_for('supplier.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar fornecedor: {str(e)}', 'danger')
    
    # Buscar dados do fornecedor
    supplier_data = db.session.query(
        QuotationItem.vendor_name,
        QuotationItem.vendor_cnpj,
        func.count(QuotationItem.id).label('total_quotations')
    ).filter_by(vendor_name=vendor_name).group_by(
        QuotationItem.vendor_name,
        QuotationItem.vendor_cnpj
    ).first()
    
    if not supplier_data:
        flash('Fornecedor não encontrado.', 'danger')
        return redirect(url_for('supplier.index'))
    
    return render_template('supplier/edit.html', supplier=supplier_data)

@supplier_bp.route('/<vendor_name>/delete', methods=['POST'])
@login_required
@login_required_only
def delete(vendor_name):
    """Deletar fornecedor (remove todos os QuotationItems relacionados)"""
    try:
        quotation_items = QuotationItem.query.filter_by(vendor_name=vendor_name).all()
        
        if not quotation_items:
            flash('Fornecedor não encontrado.', 'danger')
            return redirect(url_for('supplier.index'))
        
        # Verificar se há itens selecionados (em pedidos)
        selected_items = [item for item in quotation_items if item.is_selected]
        if selected_items:
            flash('Não é possível deletar fornecedor com cotações selecionadas.', 'danger')
            return redirect(url_for('supplier.index'))
        
        # Deletar todos os QuotationItems deste fornecedor
        for item in quotation_items:
            db.session.delete(item)
        
        db.session.commit()
        flash(f'Fornecedor {vendor_name} deletado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar fornecedor: {str(e)}', 'danger')
    
    return redirect(url_for('supplier.index'))

@supplier_bp.route('/<vendor_name>/history')
@login_required
@login_required_only
def history(vendor_name):
    """Histórico de cotações do fornecedor"""
    quotation_items = QuotationItem.query.filter_by(vendor_name=vendor_name).order_by(
        QuotationItem.created_at.desc()
    ).all()
    
    return render_template('supplier/history.html', 
                         vendor_name=vendor_name, 
                         quotation_items=quotation_items)