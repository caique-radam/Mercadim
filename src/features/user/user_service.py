from src.core.database import supabase_client

def list_users():
    try:
        response = (
            supabase_client()
            .table("user_full")
            .select("*")
            .execute()
        )
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}