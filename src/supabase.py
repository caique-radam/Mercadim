from supabase import create_client, Client
from flask import current_app

_supabase_client: Client = None

def init_supabase(app):
    global _supabase_client
    url = app.config.get('SUPABASE_URL')
    key = app.config.get('SUPABASE_KEY')

    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar configurados")

    _supabase_client = create_client(url, key)

def get_client() -> Client:
    """Retorna o cliente Supabase"""
    if _supabase_client is None:
        raise RuntimeError("Supabase client não inicializado. Chame init_supabase(app) primeiro")
    return _supabase_client