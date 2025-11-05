from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from src.supabase import supabase_client
from .decorators import guest_only
import is_valid_email

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'], endpoint='login')
@guest_only
def login_view():
    """Página e processamento de login"""

    if request.method == 'POST':
        print("request", request.form.get('email'))
    #     email = request.form.get('email', '').strip()
    #     password = request.form.get('password', '')
    #     remember = request.form.get('remember', False)

    #     # Validações
    #     if not email or not password:
    #         flash('Email e senha são obrigatórios.', 'danger')
    #         return render_template('auth/login.html')

    #     if not is_valid_email(email):
    #         flash('Email inválido.', 'danger')
    #         return render_template('auth/login.html')

    #     # Tenta fazer login no Supabase
    #     result = auth_service.login(email, password)

    #     if result['success']:
    #         # Login bem-sucedido
    #         auth_response = result['data']
    #         user = auth_response.user
    #         session_data = auth_response.session

    #         # Salva informações na sessão Flask
    #         session['user'] = {
    #             'id': user.id,
    #             'email': user.email,
    #             'user_metadata': user.user_metadata,
    #         }
    #         session['access_token'] = session_data.access_token
    #         session['refresh_token'] = session_data.refresh_token

    #         # Configura sessão permanente se "lembrar-me" estiver marcado
    #         session.permanent = bool(request.form.get('remember'))

    #         flash('Login realizado com sucesso!', 'success')

    #         # Redireciona para página solicitada ou dashboard
    #         next_page = request.args.get('next')
    #         if next_page:
    #             return redirect(next_page)
    #         return redirect(url_for('index'))
    #     else:
    #         # Erro no login
    #         error_message = result.get('error', 'Erro ao fazer login')
    #         if 'Invalid login credentials' in error_message:
    #             flash('Email ou senha incorretos.', 'danger')
    #         else:
    #             flash('Erro ao fazer login. Tente novamente.', 'danger')
    #         return render_template('auth/login.html')

    # return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """Faz logout do usuário"""
    access_token = session.get('access_token')

    if access_token:
        supabase_client().auth.sign_out()

    session.clear()
    flash('Você saiu com sucesso.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@guest_only
def forgot_password():
    """Página e processamento de recuperação de senha"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email:
            flash('Email é obrigatório.', 'danger')
            return render_template('auth/forgot_password.html')

        if not is_valid_email(email):
            flash('Email inválido.', 'danger')
            return render_template('auth/forgot_password.html')

        result = supabase_client().auth.reset_password_email(email)

        # Sempre mostra mensagem de sucesso por segurança (não revela se email existe)
        flash('Se este email estiver cadastrado, você receberá instruções para redefinir sua senha.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Página para redefinir senha após clicar no link do email"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not password or not confirm_password:
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('auth/reset_password.html')

        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('auth/reset_password.html')

        # if not is_strong_password(password):
        #     flash('A senha deve ter no mínimo 8 caracteres, incluindo maiúsculas, minúsculas e números.', 'danger')
        #     return render_template('auth/reset_password.html')

        access_token = session.get('access_token')
        result = supabase_client().auth.update_user({'password': password})

        if result['success']:
            flash('Senha redefinida com sucesso!', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Erro ao redefinir senha. Tente novamente.', 'danger')
            return render_template('auth/reset_password.html')

    return render_template('auth/reset_password.html')

@auth_bp.route('/api/refresh-token', methods=['POST'])
def refresh_token():
    """Renova o token de acesso"""
    refresh_token = session.get('refresh_token')

    if not refresh_token:
        return jsonify({'success': False, 'error': 'No refresh token'}), 401

    result = supabase_client().auth.refresh_session(refresh_token)

    if result['success']:
        session_data = result['data']
        session['access_token'] = session_data.access_token
        session['refresh_token'] = session_data.refresh_token
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Failed to refresh token'}), 401