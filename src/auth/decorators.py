from functools import wraps

from flask import session, flash, redirect, request, url_for


def login_required(f):
    """
        Decorador para proteger rotas que requerem autenticação
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or 'access_token' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        access_token = session.get('access_token')
        result =