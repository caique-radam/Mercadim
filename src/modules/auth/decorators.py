from functools import wraps
from flask import session, redirect, url_for, flash, request
from src.supabase import supabase_client


def login_required(f):
    """
    Decorador para proteger rotas que requerem autenticação
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se existe sessão ativa
        if 'user' not in session or 'access_token' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        # Verifica se o token ainda é válido
        access_token = session.get('access_token')
        result = supabase_client().auth.get_user(access_token)

        if not result['success']:
            # Token inválido ou expirado
            session.clear()
            flash('Sua sessão expirou. Por favor, faça login novamente.', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorador para proteger rotas que requerem privilégios de admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Primeiro verifica se está logado
        if 'user' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        # Verifica se é admin
        user = session.get('user', {})
        user_metadata = user.get('user_metadata', {})

        if not user_metadata.get('is_admin', False):
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)

    return decorated_function


def guest_only(f):
    """
    Decorador para rotas que só devem ser acessadas por usuários não autenticados
    Exemplo: login, registro
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' in session:
            # Usuário já está logado, redireciona para página inicial
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated_function


def role_required(*roles):
    """
    Decorador para verificar se o usuário tem uma role específica
    Uso: @role_required('admin', 'manager')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                flash('Por favor, faça login para acessar esta página.', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            user = session.get('user', {})
            user_metadata = user.get('user_metadata', {})
            user_role = user_metadata.get('role', 'user')

            if user_role not in roles:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('index'))

            return f(*args, **kwargs)

        return decorated_function

    return decorator