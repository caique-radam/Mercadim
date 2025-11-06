"""
Módulo Common - Utilitários e componentes compartilhados

Contém funções utilitárias e componentes reutilizáveis:
- Utils (validações, helpers)
- Interface (menus, contexto)
"""
from .utils import is_valid_email, is_strong_password

__all__ = [
    'is_valid_email',
    'is_strong_password',
]

