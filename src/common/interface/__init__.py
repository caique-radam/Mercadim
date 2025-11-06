"""
Módulo de Interface - Gerencia contexto da interface do usuário
"""
from .context import get_interface_context
from .menu import get_menu_items, get_menu_sections

__all__ = ['get_interface_context', 'get_menu_items', 'get_menu_sections']
