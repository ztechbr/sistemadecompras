"""
Filtros personalizados para templates Jinja2
"""
from datetime import datetime
import locale

def register_filters(app):
    """Registra filtros personalizados na aplicação"""
    
    @app.template_filter('format_currency')
    def format_currency(value):
        """Formata valor como moeda brasileira"""
        if value is None:
            return 'R$ 0,00'
        try:
            return f'R$ {float(value):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        except (ValueError, TypeError):
            return 'R$ 0,00'
    
    @app.template_filter('format_date')
    def format_date(value, format='%d/%m/%Y'):
        """Formata data"""
        if value is None:
            return ''
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except:
                return value
        try:
            return value.strftime(format)
        except:
            return str(value)
    
    @app.template_filter('format_datetime')
    def format_datetime(value, format='%d/%m/%Y %H:%M'):
        """Formata data e hora"""
        if value is None:
            return ''
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except:
                return value
        try:
            return value.strftime(format)
        except:
            return str(value)
    
    @app.template_filter('format_cnpj')
    def format_cnpj(value):
        """Formata CNPJ"""
        if not value:
            return ''
        # Remove caracteres não numéricos
        cnpj = ''.join(filter(str.isdigit, str(value)))
        if len(cnpj) == 14:
            return f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}'
        return value
    
    @app.template_filter('days_ago')
    def days_ago(value):
        """Retorna quantos dias atrás"""
        if value is None:
            return ''
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except:
                return value
        try:
            delta = datetime.utcnow() - value
            days = delta.days
            if days == 0:
                return 'Hoje'
            elif days == 1:
                return '1 dia atrás'
            else:
                return f'{days} dias atrás'
        except:
            return str(value)
    
    @app.template_filter('status_badge_color')
    def status_badge_color(status):
        """Retorna a classe CSS para o badge de status"""
        colors = {
            'PENDING': 'bg-yellow-100 text-yellow-800',
            'APPROVED': 'bg-green-100 text-green-800',
            'REJECTED': 'bg-red-100 text-red-800',
            'IN_QUOTATION': 'bg-blue-100 text-blue-800',
            'QUOTED': 'bg-indigo-100 text-indigo-800',
            'VENDOR_APPROVED': 'bg-purple-100 text-purple-800',
            'PURCHASED': 'bg-green-100 text-green-800',
            'INVOICE_RECEIVED': 'bg-teal-100 text-teal-800',
            'PAYMENT_RELEASED': 'bg-cyan-100 text-cyan-800',
            'PAID': 'bg-green-100 text-green-800',
            'CANCELLED': 'bg-gray-100 text-gray-800',
            'ATIVO': 'bg-green-100 text-green-800',
            'INATIVO': 'bg-red-100 text-red-800'
        }
        return colors.get(status, 'bg-gray-100 text-gray-800')
    
    @app.template_filter('role_label')
    def role_label(role):
        """Retorna o label traduzido da role"""
        labels = {
            'ADMIN': 'Administrador',
            'MANAGER': 'Gerente',
            'USER': 'Usuário',
            'PURCHASER': 'Comprador',
            'FINANCE': 'Financeiro'
        }
        return labels.get(role, role)
    
    @app.template_filter('status_label')
    def status_label(status):
        """Retorna o label traduzido do status"""
        labels = {
            'PENDENTE': 'Pendente',
            'APROVADA': 'Aprovada',
            'REJEITADA': 'Rejeitada',
            'EM_COTACAO': 'Em Cotação',
            'COTADA': 'Cotada',
            'ORDENADA': 'Ordenada',
            'RECEBIDA': 'Recebida',
            'PAGA': 'Paga',
            'CANCELADA': 'Cancelada',
            'ATIVO': 'Ativo',
            'INATIVO': 'Inativo'
        }
        return labels.get(status, status)

