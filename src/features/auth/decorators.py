"""
Decoradores de Autenticação

DECISÃO: Centralizar lógica de autenticação em decoradores reutilizáveis
Isso evita duplicação de código e garante consistência
"""
from functools import wraps
from flask import session, redirect, url_for, flash, request
from .service import get_user


def login_required(f):
    """
    Decorador para proteger rotas que requerem autenticação
    
    DECISÃO: Validar token no Supabase antes de permitir acesso
    Isso garante que tokens expirados sejam rejeitados
    DECISÃO: Salvar URL atual no parâmetro 'next' para redirecionamento após login
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se existe sessão ativa
        if 'user' not in session or 'access_token' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        # DECISÃO: Validar token no Supabase para garantir que ainda é válido
        # Isso evita que tokens expirados sejam aceitos
        access_token = session.get('access_token')
        result = get_user(access_token)

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
    
    DECISÃO: Primeiro verificar login, depois verificar permissões
    Isso evita vazamento de informações sobre rotas admin
    DECISÃO: Usar login_required internamente para reutilizar validação
    DECISÃO: Redirecionar para 'index' (não 'main.index' que não existe)
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Verifica se é admin
        user = session.get('user', {})
        user_metadata = user.get('user_metadata', {})

        if not user_metadata.get('is_admin', False):
            flash('Você não tem permissão para acessar esta página.', 'danger')
            # DECISÃO: Redirecionar para 'index' (rota principal do app.py)
            # Não existe blueprint 'main', então usamos 'index'
            return redirect(url_for('index'))

        return f(*args, **kwargs)

    return decorated_function


def guest_only(f):
    """
    Decorador para rotas que só devem ser acessadas por usuários não autenticados
    Exemplo: login, registro, forgot-password
    
    DECISÃO: Redirecionar para 'index' se já estiver logado
    Isso evita que usuários logados vejam páginas de autenticação
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
    
    DECISÃO: Aceitar múltiplas roles para flexibilidade
    DECISÃO: Usar login_required internamente para reutilizar validação
    DECISÃO: Redirecionar para 'index' se não tiver permissão
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = session.get('user', {})
            user_metadata = user.get('user_metadata', {})
            user_role = user_metadata.get('role', 'user')

            if user_role not in roles:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('index'))

            return f(*args, **kwargs)

        return decorated_function

    return decorator
