"""
Gerencia contexto global da interface do usuário
"""
from flask import session, request, has_request_context
from typing import Dict, Optional
from .menu import get_menu_sections, get_menu_items, set_active_menu_item


def get_interface_context() -> Dict:
    """
    Retorna o contexto completo da interface para ser injetado nos templates
    
    Returns:
        Dicionário com todas as variáveis de contexto da interface
    """
    try:
        # Obter informações do usuário da sessão (pode não estar disponível)
        user = session.get('user', {}) if has_request_context() else {}
        user_role = user.get('role') if isinstance(user, dict) else None
        
        # Obter URL atual (apenas se houver contexto de requisição)
        current_url = request.path if has_request_context() else None
        
        # Obter seções do menu
        menu_sections = get_menu_sections(user_role)
        
        # Marcar item ativo baseado na URL
        if current_url:
            menu_sections = set_active_menu_item(menu_sections, current_url)
        
        # Obter itens do menu principal
        main_menu_items = get_menu_items(current_url)
        
        return {
            'sidebar_menu_sections': menu_sections,
            'sidebar_main_menu': main_menu_items,
            'user_role': user_role,
            'current_url': current_url
        }
    except Exception:
        # Em caso de erro, retornar valores padrão
        return {
            'sidebar_menu_sections': get_menu_sections(),
            'sidebar_main_menu': get_menu_items(),
            'user_role': None,
            'current_url': None
        }

