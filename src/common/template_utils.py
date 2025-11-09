"""
Utilitários para uso nos templates Jinja2
Inclui filtros customizados e funções auxiliares
"""
from datetime import datetime
from typing import Any, Optional


# ============================================
# FILTROS CUSTOMIZADOS
# ============================================

def format_currency(value: Any, symbol: str = 'R$') -> str:
    """
    Formata um valor numérico como moeda brasileira
    
    Args:
        value: Valor numérico a ser formatado
        symbol: Símbolo da moeda (padrão: R$)
    
    Returns:
        String formatada como moeda (ex: R$ 1.234,56)
    """
    try:
        if value is None:
            return f"{symbol} 0,00"
        
        # Converte para float
        valor = float(value)
        
        # Formata com 2 casas decimais
        valor_str = f"{valor:.2f}"
        
        # Substitui ponto por vírgula
        valor_str = valor_str.replace('.', ',')
        
        # Adiciona separador de milhar
        partes = valor_str.split(',')
        parte_inteira = partes[0]
        
        # Adiciona pontos a cada 3 dígitos
        parte_inteira_formatada = ''
        for i, digito in enumerate(reversed(parte_inteira)):
            if i > 0 and i % 3 == 0:
                parte_inteira_formatada = '.' + parte_inteira_formatada
            parte_inteira_formatada = digito + parte_inteira_formatada
        
        return f"{symbol} {parte_inteira_formatada},{partes[1]}"
    except (ValueError, TypeError, IndexError):
        return f"{symbol} 0,00"


def format_number(value: Any, decimals: int = 2) -> str:
    """
    Formata um número com separador de milhar e casas decimais
    
    Args:
        value: Valor numérico
        decimals: Número de casas decimais (padrão: 2)
    
    Returns:
        String formatada (ex: 1.234,56)
    """
    try:
        if value is None:
            return "0,00"
        
        valor = float(value)
        valor_str = f"{valor:.{decimals}f}"
        return valor_str.replace('.', ',')
    except (ValueError, TypeError):
        return "0,00"


def format_date(value: Any, format_str: str = '%d/%m/%Y') -> str:
    """
    Formata uma data
    
    Args:
        value: Data (string, datetime, ou None)
        format_str: Formato desejado (padrão: %d/%m/%Y)
    
    Returns:
        String formatada ou string vazia se inválido
    """
    try:
        if value is None:
            return ''
        
        # Se já for string, tenta converter
        if isinstance(value, str):
            # Tenta vários formatos comuns
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%d-%m-%Y']:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime(format_str)
                except ValueError:
                    continue
            return value
        
        # Se for datetime
        if isinstance(value, datetime):
            return value.strftime(format_str)
        
        return str(value)
    except Exception:
        return ''


def format_quantity(value: Any, unit: str = '') -> str:
    """
    Formata quantidade com unidade de medida
    
    Args:
        value: Valor numérico
        unit: Unidade de medida (ex: 'kg', 'un')
    
    Returns:
        String formatada (ex: 10,5 kg)
    """
    try:
        if value is None:
            return f"0 {unit}".strip()
        
        valor = float(value)
        valor_str = f"{valor:.2f}".replace('.', ',')
        return f"{valor_str} {unit}".strip()
    except (ValueError, TypeError):
        return f"0 {unit}".strip()


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def calcular_total_itens(carrinho: list) -> float:
    """
    Calcula o total de itens no carrinho
    
    Args:
        carrinho: Lista de itens do carrinho
    
    Returns:
        Total calculado
    """
    try:
        total = 0.0
        for item in carrinho:
            preco = float(item.get('produto', {}).get('preco', 0) or 0)
            quantidade = float(item.get('quantidade', 0) or 0)
            total += preco * quantidade
        return total
    except Exception:
        return 0.0


def get_produto_by_id(produtos: list, produto_id: Any) -> Optional[dict]:
    """
    Busca um produto na lista pelo ID
    
    Args:
        produtos: Lista de produtos
        produto_id: ID do produto a buscar
    
    Returns:
        Dicionário do produto ou None se não encontrado
    """
    try:
        produto_id = int(produto_id)
        for produto in produtos:
            if produto.get('id') == produto_id:
                return produto
        return None
    except (ValueError, TypeError):
        return None

