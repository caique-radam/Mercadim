"""
Rotas de Autenticação

DECISÃO: Centralizar todas as rotas de autenticação em um blueprint
Isso facilita organização e manutenção do código
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from .decorators import guest_only
from .service import (
    login as auth_login,
    sign_out as auth_sign_out,
    reset_password_email,
    update_password,
    refresh_session
)
from src.utils.funcs import is_valid_email, is_strong_password
from src.profile.service import get_logged_profile
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'], endpoint='login')
@guest_only
def login_view():
    """
    Página e processamento de login
    
    DECISÃO: Usar o serviço de autenticação para padronizar tratamento de erros
    DECISÃO: Configurar sessão permanente apenas se "lembrar-me" estiver marcado
    DECISÃO: Suportar redirecionamento após login (parâmetro 'next')
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        # Validações
        if not email or not password:
            flash('Email e senha são obrigatórios.', 'danger')
            return render_template('auth/login.html')

        if not is_valid_email(email):
            flash('Email inválido.', 'danger')
            return render_template('auth/login.html')

        # Tenta fazer login usando o serviço
        result = auth_login(email, password)

        if result['success']:
            # Login bem-sucedido
            auth_response = result['data']
            user = auth_response.user
            session_data = auth_response.session

            # DECISÃO: Buscar dados do profile após autenticação bem-sucedida
            # A trigger garante que sempre existe um profile para cada usuário
            profile_result = get_logged_profile(user.id)
            profile = profile_result.get('data') if profile_result['success'] else None

            # DECISÃO: Integrar dados do profile na sessão
            # Combina dados do auth.users com dados da tabela profiles
            # Facilita acesso nos templates sem precisar buscar novamente
            session['user'] = {
                # Dados do auth.users
                'id': user.id,
                'email': user.email,
                'user_metadata': user.user_metadata or {},
                
                # Dados do profile (tabela profiles)
                'profile': profile,  # Objeto completo do profile
                
                # Campos acessíveis diretamente (para facilitar uso nos templates)
                'name': profile.get('name') if profile else None,  # Nome completo calculado
                'first_name': profile.get('first_name') if profile else None,
                'last_name': profile.get('last_name') if profile else None,
                # Adicione outros campos do profile conforme necessário
                # 'avatar_url': profile.get('avatar_url') if profile else None,
                # 'role': profile.get('role') if profile else 'user',
            }
            session['access_token'] = session_data.access_token
            session['refresh_token'] = session_data.refresh_token

            # DECISÃO: Configurar sessão permanente apenas se "lembrar-me" estiver marcado
            # Isso respeita a preferência do usuário e configura PERMANENT_SESSION_LIFETIME
            session.permanent = bool(remember)

            flash('Login realizado com sucesso!', 'success')

            # DECISÃO: Redireciona para página solicitada ou dashboard
            # Isso melhora UX ao permitir acesso direto a páginas protegidas
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            # Erro no login - o serviço já retorna mensagens amigáveis
            error_message = result.get('error', 'Erro ao fazer login')
            flash(error_message, 'danger')
            return render_template('auth/login.html')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """
    Faz logout do usuário
    
    DECISÃO: Sempre limpar sessão local, mesmo se logout remoto falhar
    Isso garante que o usuário perca acesso imediatamente
    DECISÃO: Não usar @login_required porque usuários podem querer sair mesmo com sessão expirada
    """
    access_token = session.get('access_token')
    
    # Tenta fazer logout no Supabase (pode falhar se token estiver expirado)
    result = auth_sign_out(access_token)
    
    # Sempre limpa a sessão local, independente do resultado remoto
    session.clear()
    
    flash('Você saiu com sucesso.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@guest_only
def forgot_password():
    """
    Página e processamento de recuperação de senha
    
    DECISÃO: Usar @guest_only para evitar que usuários logados acessem
    DECISÃO: Sempre mostrar mensagem de sucesso por segurança (não revela se email existe)
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email:
            flash('Email é obrigatório.', 'danger')
            return render_template('auth/forgot_password.html')

        if not is_valid_email(email):
            flash('Email inválido.', 'danger')
            return render_template('auth/forgot_password.html')

        # DECISÃO: Construir URL de redirecionamento dinamicamente
        # Isso garante que funcione em diferentes ambientes
        redirect_url = f"{request.host_url.rstrip('/')}/auth/reset-password"
        result = reset_password_email(email, redirect_url)

        # DECISÃO: Sempre mostra mensagem de sucesso por segurança
        # Não revela se o email está cadastrado (evita enumeração de emails)
        flash('Se este email estiver cadastrado, você receberá instruções para redefinir sua senha.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
@guest_only
def reset_password():
    """
    Página para redefinir senha após clicar no link do email
    
    DECISÃO: Usar @guest_only porque reset deve ser feito sem estar logado
    DECISÃO: Validar força da senha antes de enviar para o Supabase
    DECISÃO: O token de reset vem na URL (Supabase adiciona automaticamente)
    """
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not password or not confirm_password:
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('auth/reset_password.html')

        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return render_template('auth/reset_password.html')

        # DECISÃO: Validar força da senha antes de enviar
        # Isso evita requisições desnecessárias e melhora UX
        if not is_strong_password(password):
            flash('A senha deve ter no mínimo 8 caracteres, incluindo maiúsculas, minúsculas e números.', 'danger')
            return render_template('auth/reset_password.html')

        # DECISÃO: O Supabase gerencia tokens de reset automaticamente
        # Quando o usuário clica no link do email, o Supabase adiciona tokens na URL
        # e cria uma sessão temporária. O método update_user usa essa sessão automaticamente.
        # Não precisamos extrair tokens manualmente.
        result = update_password(password)

        if result['success']:
            flash('Senha redefinida com sucesso!', 'success')
            # Limpa a sessão após reset bem-sucedido
            session.clear()
            return redirect(url_for('auth.login'))
        else:
            error_message = result.get('error', 'Erro ao redefinir senha. Tente novamente.')
            flash(error_message, 'danger')
            return render_template('auth/reset_password.html')

    return render_template('auth/reset_password.html')


@auth_bp.route('/api/refresh-token', methods=['POST'])
def refresh_token():
    """
    Renova o token de acesso usando refresh token
    
    DECISÃO: Endpoint API que retorna JSON (não HTML)
    DECISÃO: Usar serviço para padronizar tratamento de erros
    DECISÃO: Atualizar ambos os tokens na sessão
    """
    refresh_token_value = session.get('refresh_token')

    if not refresh_token_value:
        return jsonify({'success': False, 'error': 'No refresh token'}), 401

    result = refresh_session(refresh_token_value)

    if result['success']:
        # Atualiza tokens na sessão
        session_data = result['data']
        session['access_token'] = session_data['access_token']
        session['refresh_token'] = session_data['refresh_token']
        
        # DECISÃO: Atualizar dados do usuário e buscar profile atualizado
        # Isso garante que dados do profile estejam sempre atualizados após refresh
        if 'user' in session_data:
            user = session_data['user']
            
            # Busca profile atualizado
            profile_result = get_logged_profile(user.id)
            profile = profile_result.get('data') if profile_result['success'] else None
            
            # Atualiza sessão com dados completos (auth + profile)
            session['user'] = {
                'id': user.id,
                'email': user.email,
                'user_metadata': user.user_metadata or {},
                'profile': profile,
                'name': profile.get('name') if profile else None,
                'first_name': profile.get('first_name') if profile else None,
                'last_name': profile.get('last_name') if profile else None,
            }
        
        return jsonify({'success': True})

    error_message = result.get('error', 'Failed to refresh token')
    return jsonify({'success': False, 'error': error_message}), 401
