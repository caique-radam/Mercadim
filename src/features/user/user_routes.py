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

@user_bp.route('/')
@login_required
def user_view():
    logged_user = session.get('user', {})

    users_data = list_users()

    headers = ["Primeiro Nome", "Último Nome", "Email", "Role", "Telefone"]
    rows = users_data['data']
    
    return render_template(
        'user/list_user.html',
        title="Lista de Usuários",
        headers=headers,
        rows=rows,
        add_url=url_for('user.create_user'),
        user=logged_user
    )

@user_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """Rota para criar um novo usuário"""
    logged_user = session.get('user', {})
    
    if request.method == 'POST':
        # Coleta os dados do formulário
        user_data = {
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip() or None,
            'password': request.form.get('password', '').strip(),
            'confirm_password': request.form.get('confirm_password', '').strip(),
            'role': request.form.get('role', 'authenticated').strip()  # Valor padrão
        }
        
        # Validação básica
        if not user_data['first_name']:
            flash('Primeiro nome é obrigatório', 'error')
            return redirect(url_for('user.create_user'))
        if not user_data['last_name']:
            flash('Último nome é obrigatório', 'error')
            return redirect(url_for('user.create_user'))
        if not user_data['email']:
            flash('E-mail é obrigatório', 'error')
            return redirect(url_for('user.create_user'))
        if not user_data['password']:
            flash('Senha é obrigatória', 'error')
            return redirect(url_for('user.create_user'))
        if user_data['password'] != user_data['confirm_password']:
            flash('As senhas não correspondem', 'error')
            return redirect(url_for('user.create_user'))
        
        # Chama o serviço para criar o usuário
        result = create_user_service(user_data)
        
        if result['success']:
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('user.user_view'))
        else:
            flash(f'Erro ao criar usuário: {result.get("error", "Erro desconhecido")}', 'error')
            return redirect(url_for('user.create_user'))
    
    # Campos do formulário baseados nas colunas da listagem
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
            'cols': 6
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
            'required': True,
            'cols': 6
        },
        {
            'name': 'confirm_password',
            'id': 'confirm_password',
            'type': 'password',
            'label': 'Confirmar Senha',
            'placeholder': 'Confirme a senha',
            'required': True,
            'cols': 6
        }
        # {
        #     'name': 'role',
        #     'id': 'role',
        #     'type': 'select',
        #     'label': 'Perfil',
        #     'required': True,
        #     'cols': 12,
        #     'options': [
        #         {'value': 'authenticated', 'label': 'Autenticado'},
        #     ],
        #     'empty_option': 'Selecione o perfil'
        # }
    ]
    
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
        # Coleta os dados do formulário
        user_data = {
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'phone': request.form.get('phone', '').strip() or None
        }
        
        # Validação básica
        if not user_data['first_name']:
            flash('Primeiro nome é obrigatório', 'error')
            return redirect(url_for('user.edit_user', id=id))
        if not user_data['last_name']:
            flash('Último nome é obrigatório', 'error')
            return redirect(url_for('user.edit_user', id=id))
        
        # Chama o serviço para atualizar o usuário
        result = update_user(id, user_data)
        
        if result['success']:
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('user.user_view'))
        else:
            flash(f'Erro ao atualizar usuário: {result.get("error", "Erro desconhecido")}', 'error')
            return redirect(url_for('user.edit_user', id=id))
    
    # Busca os dados do usuário no banco de dados
    result = get_user_by_id(id)
    
    if not result['success']:
        flash(f'Usuário não encontrado: {result.get("error", "Erro desconhecido")}', 'error')
        return redirect(url_for('user.user_view'))
    
    user_data = result['data']
    
    # Campos do formulário baseados nas colunas da listagem (igual ao create_user)
    fields = [
        {
            'name': 'first_name',
            'id': 'first_name',
            'type': 'text',
            'label': 'Primeiro Nome',
            'placeholder': 'Digite o primeiro nome',
            'required': True,
            'cols': 6,
            'value': user_data.get('first_name', '')
        },
        {
            'name': 'last_name',
            'id': 'last_name',
            'type': 'text',
            'label': 'Último Nome',
            'placeholder': 'Digite o último nome',
            'required': True,
            'cols': 6,
            'value': user_data.get('last_name', '')
        },
        {
            'name': 'email',
            'id': 'email',
            'type': 'email',
            'label': 'E-mail',
            'placeholder': 'usuario@example.com',
            'required': True,
            'cols': 6,
            'value': user_data.get('email', ''),
            'readonly': True  # Email geralmente não é editável
        },
        {
            'name': 'phone',
            'id': 'phone',
            'type': 'tel',
            'label': 'Telefone',
            'placeholder': '(00) 00000-0000',
            'required': False,
            'cols': 6,
            'value': user_data.get('phone', '')
        },
        {
            'name': 'password',
            'id': 'password',
            'type': 'password',
            'label': 'Senha',
            'placeholder': 'Digite a senha',
            'required': False,
            'cols': 6
        },
        {
            'name': 'confirm_password',
            'id': 'confirm_password',
            'type': 'password',
            'label': 'Confirmar Senha',
            'placeholder': 'Confirme a senha',
            'required': False,
            'cols': 6
        },
    ]
    
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
    # Chama o serviço para deletar o usuário
    result = delete_user_service(id)
    
    if result['success']:
        flash('Usuário deletado com sucesso!', 'success')
    else:
        flash(f'Erro ao deletar usuário: {result.get("error", "Erro desconhecido")}', 'error')
    
    return redirect(url_for('user.user_view'))