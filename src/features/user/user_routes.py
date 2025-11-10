from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from src.features.auth.auth_decorators import login_required
from src.features.user.user_service import (
    list_users, 
    create_user as create_user_service, 
    get_user_by_id, 
    update_user, 
    delete_user as delete_user_service
)

user_bp = Blueprint('user', __name__, url_prefix='/user')


def get_form_fields(user_data=None, is_edit=False):
    """
    Retorna os campos do formulário de usuário.
    Se user_data for fornecido, preenche os valores (modo edição).
    """
    fields = [
        {
            'name': 'first_name',
            'id': 'first_name',
            'type': 'text',
            'label': 'Primeiro Nome',
            'placeholder': 'Digite o primeiro nome',
            'required': True,
            'cols': 6
        },
        {
            'name': 'last_name',
            'id': 'last_name',
            'type': 'text',
            'label': 'Último Nome',
            'placeholder': 'Digite o último nome',
            'required': True,
            'cols': 6
        },
        {
            'name': 'email',
            'id': 'email',
            'type': 'email',
            'label': 'E-mail',
            'placeholder': 'usuario@example.com',
            'required': True,
            'cols': 6,
            'readonly': is_edit  # Email não é editável na edição
        },
        {
            'name': 'phone',
            'id': 'phone',
            'type': 'tel',
            'label': 'Telefone',
            'placeholder': '(00) 00000-0000',
            'required': False,
            'cols': 6
        },
        {
            'name': 'password',
            'id': 'password',
            'type': 'password',
            'label': 'Senha',
            'placeholder': 'Digite a senha',
            'required': not is_edit,  # Obrigatório apenas na criação
            'cols': 6
        },
        {
            'name': 'confirm_password',
            'id': 'confirm_password',
            'type': 'password',
            'label': 'Confirmar Senha',
            'placeholder': 'Confirme a senha',
            'required': not is_edit,  # Obrigatório apenas na criação
            'cols': 6
        }
    ]
    
    # Se estiver editando, preenche os valores
    if user_data:
        for field in fields:
            field_name = field['name']
            if field_name in ['password', 'confirm_password']:
                # Campos de senha não são preenchidos na edição
                continue
            else:
                # Campos de texto: trata None como string vazia
                value = user_data.get(field_name)
                field['value'] = str(value) if value is not None else ''
    
    return fields


def collect_form_data(is_edit=False):
    """Coleta e limpa os dados do formulário"""
    data = {
        'first_name': request.form.get('first_name', '').strip(),
        'last_name': request.form.get('last_name', '').strip(),
        'phone': request.form.get('phone', '').strip() or None
    }
    
    # Email apenas na criação
    if not is_edit:
        data['email'] = request.form.get('email', '').strip()
    
    # Senhas
    password = request.form.get('password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    # Só inclui senhas se foram fornecidas
    if password or confirm_password:
        data['password'] = password
        data['confirm_password'] = confirm_password
    
    return data


def validate_user_data(user_data, is_edit=False):
    """
    Valida os dados do usuário.
    Retorna (is_valid, error_message)
    """
    # Validações obrigatórias
    if not user_data.get('first_name'):
        return False, 'Primeiro nome é obrigatório'
    
    if not user_data.get('last_name'):
        return False, 'Último nome é obrigatório'
    
    # Email obrigatório apenas na criação
    if not is_edit and not user_data.get('email'):
        return False, 'E-mail é obrigatório'
    
    # Validação de senha
    password = user_data.get('password', '')
    confirm_password = user_data.get('confirm_password', '')
    
    if not is_edit:
        # Na criação, senha é obrigatória
        if not password:
            return False, 'Senha é obrigatória'
        if password != confirm_password:
            return False, 'As senhas não correspondem'
    else:
        # Na edição, senha é opcional, mas se fornecida, deve corresponder
        if password or confirm_password:
            if password != confirm_password:
                return False, 'As senhas não correspondem'
            # Remove senhas vazias
            if not password:
                user_data.pop('password', None)
                user_data.pop('confirm_password', None)
        else:
            # Remove senhas se não foram fornecidas
            user_data.pop('password', None)
            user_data.pop('confirm_password', None)
    
    return True, None


@user_bp.route('/')
@login_required
def user_view():
    """Rota para listar todos os usuários"""
    logged_user = session.get('user', {})

    users_data = list_users()

    if not users_data['success']:
        flash(f'Erro ao carregar usuários: {users_data.get("error", "Erro desconhecido")}', 'error')
        users_data['data'] = []

    headers = ["Primeiro Nome", "Último Nome", "Email", "Role", "Telefone"]
    # Garante que rows é sempre uma lista
    rows = users_data.get('data', []) if isinstance(users_data.get('data'), list) else []
    
    return render_template(
        'user/list_user.html',
        title="Lista de Usuários",
        headers=headers,
        rows=rows,
        add_url=url_for('user.create_user'),
        edit_url='user.edit_user',
        delete_url='user.delete_user',
        user=logged_user
    )


@user_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """Rota para criar um novo usuário"""
    logged_user = session.get('user', {})
    
    if request.method == 'POST':
        user_data = collect_form_data(is_edit=False)
        
        # Validação
        is_valid, error_message = validate_user_data(user_data, is_edit=False)
        if not is_valid:
            flash(error_message, 'error')
            return redirect(url_for('user.create_user'))
        
        # Chama o serviço para criar o usuário
        result = create_user_service(user_data)
        
        if result['success']:
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('user.user_view'))
        else:
            flash(f'Erro ao criar usuário: {result.get("error", "Erro desconhecido")}', 'error')
            return redirect(url_for('user.create_user'))
    
    # GET: mostra formulário vazio
    fields = get_form_fields(is_edit=False)
    
    return render_template(
        'user/form_user.html',
        title="Criar Novo Usuário",
        subtitle="Preencha os dados do novo usuário",
        fields=fields,
        action_url=url_for('user.create_user'),
        method='POST',
        cancel_url=url_for('user.user_view'),
        submit_label='Criar Usuário',
        user=logged_user
    )


@user_bp.route('/edit/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    """Rota para editar um usuário"""
    logged_user = session.get('user', {})
    
    if request.method == 'POST':
        user_data = collect_form_data(is_edit=True)
        
        # Validação
        is_valid, error_message = validate_user_data(user_data, is_edit=True)
        if not is_valid:
            flash(error_message, 'error')
            return redirect(url_for('user.edit_user', id=id))
        
        # Chama o serviço para atualizar o usuário
        result = update_user(id, user_data)
        
        if result['success']:
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('user.user_view'))
        else:
            flash(f'Erro ao atualizar usuário: {result.get("error", "Erro desconhecido")}', 'error')
            return redirect(url_for('user.edit_user', id=id))
    
    # GET: busca dados e mostra formulário preenchido
    result = get_user_by_id(id)
    
    if not result['success']:
        flash(f'Usuário não encontrado: {result.get("error", "Erro desconhecido")}', 'error')
        return redirect(url_for('user.user_view'))
    
    user_data = result['data']
    fields = get_form_fields(user_data=user_data, is_edit=True)
    
    return render_template(
        'user/form_user.html',
        title="Editar Usuário",
        subtitle=f"Editando usuário: {user_data.get('first_name', '')} {user_data.get('last_name', '')}",
        fields=fields,
        action_url=url_for('user.edit_user', id=id),
        method='POST',
        cancel_url=url_for('user.user_view'),
        submit_label='Salvar Alterações',
        data=user_data,
        user=logged_user
    )


@user_bp.route('/delete/<string:id>', methods=['POST'])
@login_required
def delete_user(id):
    """Rota para deletar um usuário"""
    result = delete_user_service(id)
    
    if result['success']:
        flash('Usuário deletado com sucesso!', 'success')
    else:
        flash(f'Erro ao deletar usuário: {result.get("error", "Erro desconhecido")}', 'error')
    
    return redirect(url_for('user.user_view'))
