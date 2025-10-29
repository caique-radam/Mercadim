from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

Config = {
    "SECRET_KEY": os.environ.get('SECRET_KEY'),
    "SUPABASE_URL": os.environ.get('SUPABASE_URL'),
    "SUPABASE_KEY": os.environ.get('SUPABASE_KEY'),
    "SESSION_TYPE": 'filesystem',
    "SESSION_PERMANENT": True,
    "PERMANENT_SESSION_LIFETIME": timedelta(days=7),
    "SESSION_COOKIE_SECURE": True,
    "SESSION_COOKIE_HTTPONLY": True,
    "SESSION_COOKIE_SAMESITE": 'Lax',
    "MAX_LOGIN_ATTEMPTS": 5,
    "LOGIN_ATTEMPT_TIMEOUT": 300,
}
