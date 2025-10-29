from src.supabase import get_client

def login(email: str, password: str):
    try:
        response = get_client().auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}

def logout():
    try:
        get_client().sign_out()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_user(access_token: str):
    try:
        response = get_client().auth.get_user(access_token)
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}