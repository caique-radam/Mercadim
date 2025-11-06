"""
Configurações da Aplicação

DECISÃO: Centralizar todas as configurações em um único arquivo
DECISÃO: Usar variáveis de ambiente para configurações sensíveis
DECISÃO: Ajustar configurações de segurança baseado no ambiente
"""
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# DECISÃO: Detectar ambiente (development/production)
# Em produção, FLASK_ENV deve ser 'production' ou não estar definido
# Em desenvolvimento, pode ser 'development' ou 'dev'
FLASK_ENV = os.environ.get('FLASK_ENV', 'development').lower()
IS_PRODUCTION = FLASK_ENV == 'production'

Config = {
    "SECRET_KEY": os.environ.get('SECRET_KEY'),
    "SUPABASE_URL": os.environ.get('SUPABASE_URL'),
    "SUPABASE_KEY": os.environ.get('SUPABASE_KEY'),
    "SESSION_TYPE": 'filesystem',
    "SESSION_PERMANENT": True,
    "PERMANENT_SESSION_LIFETIME": timedelta(days=7),
    # DECISÃO: SESSION_COOKIE_SECURE apenas em produção
    # Em desenvolvimento (HTTP local), cookies secure quebram a aplicação
    # Em produção (HTTPS), cookies secure são obrigatórios para segurança
    "SESSION_COOKIE_SECURE": IS_PRODUCTION,
    "SESSION_COOKIE_HTTPONLY": True,
    "SESSION_COOKIE_SAMESITE": 'Lax',
    "MAX_LOGIN_ATTEMPTS": 5,
    "LOGIN_ATTEMPT_TIMEOUT": 300,
}
