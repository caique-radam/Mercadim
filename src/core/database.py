"""
Módulo de Database - Cliente Supabase

Gerencia a conexão e inicialização do cliente Supabase.
"""
from supabase import create_client, Client
from flask import current_app

_supabase_client: Client = None

def init_supabase(app):
    """
    Inicializa o cliente Supabase com as configurações da aplicação.
    
    Args:
        app: Instância da aplicação Flask
    """
    global _supabase_client
    url = app.config.get('SUPABASE_URL')
    key = app.config.get('SUPABASE_KEY')

    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar configurados")

    _supabase_client = create_client(url, key)

def supabase_client() -> Client:
    """
    Retorna o cliente Supabase inicializado.
    
    Returns:
        Cliente Supabase
        
    Raises:
        RuntimeError: Se o cliente não foi inicializado
    """
    if _supabase_client is None:
        raise RuntimeError("Supabase client não inicializado. Chame init_supabase(app) primeiro")
    return _supabase_client

