"""
Gerador de PDF para ordens de compra
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas

class PDFGenerator:
    """Classe para gerar PDFs de ordens de compra"""
    
    def __init__(self, output_dir):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_purchase_order_pdf(self, purchase_order):
        """
        Gera PDF da ordem de compra
        
        Args:
            purchase_order: Objeto PurchaseOrder
            
        Returns:
            Caminho do arquivo PDF gerado
        """
        filename = f"PO_{purchase_order.order_number}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Criar documento
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4b5563')
        )
        
        # Título
        title = Paragraph(f"ORDEM DE COMPRA<br/>{purchase_order.order_number}", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Informações da empresa
        company_heading = Paragraph("DADOS DA EMPRESA", heading_style)
        story.append(company_heading)
        
        company_data = [
            ['Empresa:', 'Empresa XYZ Ltda'],
            ['CNPJ:', '00.000.000/0001-00'],
            ['Data de Emissão:', datetime.now().strftime('%d/%m/%Y %H:%M')],
        ]
        
        company_table = Table(company_data, colWidths=[100, 350])
        company_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(company_table)
        story.append(Spacer(1, 20))
        
        # Informações do fornecedor
        vendor_heading = Paragraph("DADOS DO FORNECEDOR", heading_style)
        story.append(vendor_heading)
        
        quotation_item = purchase_order.quotation_item
        vendor_data = [
            ['Fornecedor:', quotation_item.vendor_name],
            ['CNPJ:', quotation_item.vendor_cnpj or 'Não informado'],
        ]
        
        vendor_table = Table(vendor_data, colWidths=[100, 350])
        vendor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(vendor_table)
        story.append(Spacer(1, 20))
        
        # Informações da requisição
        request_heading = Paragraph("DADOS DA REQUISIÇÃO", heading_style)
        story.append(request_heading)
        
        purchase_request = purchase_order.purchase_request
        product = purchase_request.product
        
        request_data = [
            ['Nº Requisição:', purchase_request.request_number],
            ['Solicitante:', purchase_request.requester.username],
            ['Departamento:', purchase_request.requester.department.name if purchase_request.requester.department else 'N/A'],
            ['Data da Requisição:', purchase_request.created_at.strftime('%d/%m/%Y')],
        ]
        
        request_table = Table(request_data, colWidths=[100, 350])
        request_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(request_table)
        story.append(Spacer(1, 20))
        
        # Itens da compra
        items_heading = Paragraph("ITENS DA COMPRA", heading_style)
        story.append(items_heading)
        
        items_data = [
            ['SKU', 'Produto', 'Descrição', 'Qtd', 'Valor Unit.', 'Valor Total']
        ]
        
        items_data.append([
            product.sku,
            product.product_name,
            quotation_item.description or product.description or '',
            str(quotation_item.quantity),
            f"R$ {float(quotation_item.unit_value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            f"R$ {float(quotation_item.total_value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        ])
        
        items_table = Table(items_data, colWidths=[60, 120, 150, 40, 70, 80])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 20))
        
        # Total
        total_data = [
            ['VALOR TOTAL:', f"R$ {float(quotation_item.total_value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')]
        ]
        
        total_table = Table(total_data, colWidths=[370, 150])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(total_table)
        story.append(Spacer(1, 30))
        
        # Assinaturas
        signature_text = Paragraph(
            "<br/><br/>_________________________________<br/>Comprador: " + purchase_order.purchaser.username +
            "<br/><br/><br/>_________________________________<br/>Fornecedor",
            normal_style
        )
        story.append(signature_text)
        
        # Gerar PDF
        doc.build(story)
        
        return filepath

