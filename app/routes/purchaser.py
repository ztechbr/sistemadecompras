"""
Rotas do comprador (purchaser)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from .. import db
from ..models import PurchaseRequest, Quotation, QuotationItem, PurchaseOrder
from ..utils.decorators import login_required_only
from ..utils.pdf_generator import PDFGenerator
import os

purchaser_bp = Blueprint('purchaser', __name__, url_prefix='/purchaser')

@purchaser_bp.route('/dashboard')
@login_required
@login_required_only
def dashboard():
    """Dashboard do comprador"""
    # Requisições aprovadas aguardando cotação
    approved_requests = PurchaseRequest.query.filter_by(
        status='APPROVED'
    ).order_by(PurchaseRequest.approved_at.asc()).all()
    
    # Cotações em andamento (draft)
    draft_quotations = Quotation.query.filter_by(
        purchaser_id=current_user.id,
        status='DRAFT'
    ).order_by(Quotation.created_at.desc()).all()
    
    # Cotações aprovadas aguardando compra
    approved_quotations = Quotation.query.filter_by(
        status='APPROVED'
    ).join(Quotation.purchase_request).filter(
        PurchaseRequest.status == 'VENDOR_APPROVED'
    ).order_by(Quotation.approved_at.asc()).all()
    
    return render_template('purchaser/dashboard.html',
                         approved_requests=approved_requests,
                         draft_quotations=draft_quotations,
                         approved_quotations=approved_quotations)

@purchaser_bp.route('/requests')
@login_required
@login_required_only
def requests():
    """Lista de requisições aprovadas"""
    approved_requests = PurchaseRequest.query.filter_by(
        status='APPROVED'
    ).order_by(PurchaseRequest.approved_at.asc()).all()
    
    return render_template('purchaser/requests.html', requests=approved_requests)

@purchaser_bp.route('/requests/<int:request_id>/quotation', methods=['GET', 'POST'])
@login_required
@login_required_only
def create_quotation(request_id):
    """Criar mapa de cotações"""
    try:
        purchase_request = PurchaseRequest.query.get_or_404(request_id)
    except ValueError:
        flash('ID da requisição inválido.', 'danger')
        return redirect(url_for('purchaser.quotations'))
    
    if purchase_request.status not in ['PENDING', 'APPROVED', 'IN_QUOTATION', 'EM_COTACAO']:
        flash('Esta requisição não está disponível para cotação.', 'danger')
        return redirect(url_for('purchaser.requests'))
    
    if request.method == 'POST':
        try:
            # Verificar se já existe cotação em draft
            existing_quotation = Quotation.query.filter_by(
                purchase_request_id=request_id,
                status='DRAFT'
            ).first()
            
            if existing_quotation:
                quotation = existing_quotation
                # Limpar itens existentes para esta cotação
                QuotationItem.query.filter_by(quotation_id=quotation.id).delete()
            else:
                # Criar nova cotação
                quotation = Quotation(
                    purchase_request_id=request_id,
                    purchaser_id=current_user.id,
                    status='DRAFT'
                )
                db.session.add(quotation)
                db.session.flush()
            
            # Criar itens de cotação para cada fornecedor (3 fornecedores)
            for i in range(1, 4):
                vendor_name = request.form.get(f'vendor_name_{i}')
                vendor_cnpj = request.form.get(f'vendor_cnpj_{i}')
                description = request.form.get(f'description_{i}')
                unit_value = request.form.get(f'unit_value_{i}')
                
                if vendor_name and unit_value:
                    # Criar item de cotação para este fornecedor
                    quotation_item = QuotationItem(
                        quotation_id=quotation.id,
                        vendor_name=vendor_name,
                        vendor_cnpj=vendor_cnpj,
                        description=description,
                        unit_value=float(unit_value),
                        quantity=purchase_request.quantity,
                        total_value=float(unit_value) * purchase_request.quantity,
                        is_selected=False
                    )
                    db.session.add(quotation_item)
            
            # Atualizar status da requisição
            purchase_request.status = 'IN_QUOTATION'
            
            db.session.commit()
            flash('Mapa de cotações salvo com sucesso!', 'success')
            return redirect(url_for('purchaser.view_quotation', quotation_id=quotation.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar cotação: {str(e)}', 'danger')
    
    # Verificar se já existe cotação em draft
    existing_quotation = Quotation.query.filter_by(
        purchase_request_id=request_id,
        status='DRAFT'
    ).first()
    
    return render_template('purchaser/create_quotation.html',
                         request=purchase_request,
                         quotation=existing_quotation)

@purchaser_bp.route('/quotations')
@login_required
@login_required_only
def quotations():
    """Lista de requisições para mapeamento de cotações"""
    # Buscar requisições que precisam de cotação ou estão em cotação
    requests = PurchaseRequest.query.filter(
        PurchaseRequest.status.in_(['PENDING', 'IN_QUOTATION', 'APPROVED', 'EM_COTACAO'])
    ).order_by(PurchaseRequest.created_at.desc()).all()
    
    return render_template('purchaser/quotations.html', requests=requests)

@purchaser_bp.route('/map-quotations')
@login_required
@login_required_only
def map_quotations():
    """Mapa de cotações - mostra requisições com suas cotações em grid"""
    # Buscar requisições que têm cotações ou estão em processo de cotação
    requests_with_quotations = db.session.query(PurchaseRequest).filter(
        PurchaseRequest.status.in_(['IN_QUOTATION', 'QUOTED', 'VENDOR_APPROVED', 'PURCHASED', 'EM_COTACAO'])
    ).order_by(PurchaseRequest.created_at.desc()).all()
    
    # Buscar requisições disponíveis para cotação (para o modal)
    try:
        available_requests = db.session.query(PurchaseRequest).filter(
            PurchaseRequest.status.in_(['PENDING', 'APPROVED', 'EM_COTACAO'])
        ).order_by(PurchaseRequest.created_at.desc()).all()
    except Exception as e:
        available_requests = []
    
    # Para cada requisição, buscar suas cotações e itens
    request_data = []
    for request in requests_with_quotations:
        quotations = Quotation.query.filter_by(purchase_request_id=request.id).all()
        quotation_items = []
        
        for quotation in quotations:
            items = QuotationItem.query.filter_by(quotation_id=quotation.id).order_by(QuotationItem.total_value.asc()).all()
            quotation_items.extend(items)
        
        request_data.append({
            'request': request,
            'quotations': quotations,
            'quotation_items': quotation_items[:3]  # Máximo 3 cotações por requisição
        })
    
    return render_template('purchaser/map_quotations.html', 
                         request_data=request_data, 
                         available_requests=available_requests)

@purchaser_bp.route('/quotations/<int:quotation_id>')
@login_required
@login_required_only
def view_quotation(quotation_id):
    """Visualizar detalhes da cotação"""
    quotation = Quotation.query.get_or_404(quotation_id)
    items = quotation.get_sorted_items()
    
    return render_template('purchaser/view_quotation.html',
                         quotation=quotation,
                         items=items)

@purchaser_bp.route('/quotations/<int:quotation_id>/release', methods=['POST'])
@login_required
@login_required_only
def release_quotation(quotation_id):
    """Liberar cotação para aprovação do manager"""
    try:
        quotation = Quotation.query.get_or_404(quotation_id)
        
        if quotation.status != 'DRAFT':
            flash('Esta cotação não pode ser liberada.', 'danger')
            return redirect(url_for('purchaser.view_quotation', quotation_id=quotation_id))
        
        # Verificar se tem pelo menos 3 itens
        if quotation.items.count() < 3:
            flash('É necessário ter pelo menos 3 cotações de fornecedores.', 'danger')
            return redirect(url_for('purchaser.view_quotation', quotation_id=quotation_id))
        
        quotation.release_for_approval()
        flash('Cotação liberada para aprovação do gerente!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao liberar cotação: {str(e)}', 'danger')
    
    return redirect(url_for('purchaser.quotations'))

@purchaser_bp.route('/quotations/<int:quotation_id>/purchase', methods=['POST'])
@login_required
@login_required_only
def purchase(quotation_id):
    """Executar compra após aprovação do manager"""
    try:
        quotation = Quotation.query.get_or_404(quotation_id)
        
        if quotation.status != 'APPROVED':
            flash('Esta cotação não foi aprovada ainda.', 'danger')
            return redirect(url_for('purchaser.view_quotation', quotation_id=quotation_id))
        
        if quotation.purchase_request.status != 'VENDOR_APPROVED':
            flash('Fornecedor não foi aprovado.', 'danger')
            return redirect(url_for('purchaser.view_quotation', quotation_id=quotation_id))
        
        # Buscar item selecionado
        selected_item = quotation.get_selected_item()
        if not selected_item:
            flash('Nenhum fornecedor foi selecionado.', 'danger')
            return redirect(url_for('purchaser.view_quotation', quotation_id=quotation_id))
        
        # Criar ordem de compra
        purchase_order = PurchaseOrder(
            purchase_request_id=quotation.purchase_request_id,
            quotation_item_id=selected_item.id,
            purchaser_id=current_user.id,
            status='CREATED'
        )
        
        db.session.add(purchase_order)
        db.session.flush()
        
        # Gerar PDF
        from flask import current_app
        pdf_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'pdfs')
        pdf_generator = PDFGenerator(pdf_dir)
        pdf_path = pdf_generator.generate_purchase_order_pdf(purchase_order)
        
        # Salvar caminho relativo
        purchase_order.pdf_path = os.path.basename(pdf_path)
        
        # Atualizar status da requisição
        quotation.purchase_request.status = 'PURCHASED'
        
        db.session.commit()
        
        flash(f'Compra realizada com sucesso! Ordem: {purchase_order.order_number}', 'success')
        return redirect(url_for('purchaser.view_purchase_order', order_id=purchase_order.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao realizar compra: {str(e)}', 'danger')
    
    return redirect(url_for('purchaser.quotations'))

@purchaser_bp.route('/orders')
@login_required
@login_required_only
def orders():
    """Lista de ordens de compra"""
    purchase_orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).all()
    return render_template('purchaser/orders.html', orders=purchase_orders)

@purchaser_bp.route('/orders/<int:order_id>')
@login_required
@login_required_only
def view_purchase_order(order_id):
    """Visualizar ordem de compra"""
    purchase_order = PurchaseOrder.query.get_or_404(order_id)
    return render_template('purchaser/view_order.html', order=purchase_order)

@purchaser_bp.route('/orders/<int:order_id>/download')
@login_required
@login_required_only
def download_purchase_order(order_id):
    """Download do PDF da ordem de compra"""
    from flask import current_app
    purchase_order = PurchaseOrder.query.get_or_404(order_id)
    
    if not purchase_order.pdf_path:
        flash('PDF não encontrado.', 'danger')
        return redirect(url_for('purchaser.view_purchase_order', order_id=order_id))
    
    pdf_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'pdfs')
    pdf_path = os.path.join(pdf_dir, purchase_order.pdf_path)
    
    if not os.path.exists(pdf_path):
        flash('Arquivo PDF não encontrado.', 'danger')
        return redirect(url_for('purchaser.view_purchase_order', order_id=order_id))
    
    return send_file(pdf_path, as_attachment=True, download_name=purchase_order.pdf_path)

