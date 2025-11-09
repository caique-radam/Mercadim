"""
Gerencia itens e seções do menu lateral
"""
from typing import List, Dict, Optional
from flask import url_for


def get_menu_sections(user_role: Optional[str] = None) -> List[Dict]:
    """
    Retorna todas as seções do menu lateral com seus itens
    
    Args:
        user_role: Papel do usuário (admin, user, etc.) para filtrar itens
    
    Returns:
        Lista de dicionários contendo seções e seus itens
    """
    sections = [
        {
            'name': 'CADASTROS',
            'items': [
                {
                    'icon': 'bi-building',
                    'text': 'Fornecedores',
                    'url': url_for('fornecedores.fornecedores_view'),
                    'active': False
                },
                {
                    'icon': 'bi-cart4',
                    'text': 'Produtos',
                    'url': url_for('produtos.produtos_view'),
                    'active': False
                },
            ]
        },
        {
            'name': 'SISTEMA',
            'items': [
                {
                    'icon': 'bi-people',
                    'text': 'Usuários',
                    'url': url_for('user.user_view'),
                    'has_submenu': False,
                    'active': False
                }
            ]
        }
    ]
    
    # Filtrar itens baseado em permissões se necessário
    if user_role:
        sections = _filter_by_role(sections, user_role)
    
    return sections


def get_menu_items(current_url: Optional[str] = None) -> List[Dict]:
    """
    Retorna itens do menu principal (sem seções)
    
    Args:
        current_url: URL atual para marcar item como ativo
    
    Returns:
        Lista de itens do menu principal
    """
    items = [
        {
            'icon': 'bi-speedometer2',
            'text': 'Dashboard',
            'url': '/',
            'active': current_url == '/' or current_url == '/dashboard'
        },
        {
            'icon': 'bi-basket2',
            'text': 'Vendas',
            'url': url_for('venda.venda_view'),
            'active': False
        }
    ]
    
    return items


def _filter_by_role(sections: List[Dict], user_role: str) -> List[Dict]:
    """
    Filtra seções e itens baseado no papel do usuário
    
    Args:
        sections: Lista de seções do menu
        user_role: Papel do usuário
    
    Returns:
        Lista filtrada de seções
    """
    # Exemplo: apenas admin vê seção de administração
    if user_role != 'admin':
        sections = [s for s in sections if s.get('name') != 'ADMIN']
    
    return sections


def set_active_menu_item(sections: List[Dict], current_url: str) -> List[Dict]:
    """
    Marca o item do menu como ativo baseado na URL atual
    
    Args:
        sections: Lista de seções do menu
        current_url: URL atual
    
    Returns:
        Lista de seções com itens marcados como ativos
    """
    for section in sections:
        for item in section.get('items', []):
            if item.get('url') == current_url:
                item['active'] = True
    
    return sections

