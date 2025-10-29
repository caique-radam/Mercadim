from src.supabase import get_client

def list_users():
    try:
        response = get_client().select