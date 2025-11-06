"""
Módulo de Autenticação

DECISÃO: Exportar todos os componentes principais do módulo
Isso facilita imports e uso em outras partes da aplicação
"""
from .routes import auth_bp
from .decorators import login_required, admin_required, guest_only, role_required
from .service import (
    login,
    get_user,
    sign_out,
    reset_password_email,
    update_password,
    refresh_session
)

__all__ = [
    'auth_bp',
    'login_required',
    'admin_required',
    'guest_only',
    'role_required',
    # Serviços (exportados para uso avançado, mas normalmente não necessário)
    'login',
    'get_user',
    'sign_out',
    'reset_password_email',
    'update_password',
    'refresh_session',
]