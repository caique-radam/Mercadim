"""
Módulo Core - Infraestrutura base da aplicação

Contém configurações e serviços de infraestrutura como:
- Database (Supabase)
- Exceptions (futuro)
- Configurações base (futuro)
"""
from .database import init_supabase, supabase_client

__all__ = [
    'init_supabase',
    'supabase_client',
]

