from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from src.features.auth.auth_decorators import login_required
from src.features.user.user_service import list_users

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/')
@login_required
def user_view():
    logged_user = session.get('user', {})

    users_data = list_users()
    if not users_data['success']:
        flash(users_data['error'], 'danger')
        return redirect(url_for('user.user_view'))

    # Processa os dados do Supabase
    users_list = users_data['data'].data if users_data['data'] else []
    
    headers = ["Primeiro Nome", "Último Nome", "Email", "Role"]
    rows = []
    for user in users_list:
        # O primeiro elemento é o ID (UUID) - será usado nas ações mas não exibido na tabela
        # O template usa row[1:] para pular o ID ao exibir as células
        rows.append([
            user.get('id', ''),  # ID (UUID) - não será exibido
            user.get('first_name', ''),
            user.get('last_name', ''),
            user.get('email', ''),
            user.get('role', '')
        ])
    
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
        # TODO: Implementar lógica de criação
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('user.user_view'))
    
    # Exemplo de campos para o formulário
    fields = [
        {
            'name': 'name',
            'id': 'name',
            'type': 'text',
            'label': 'Nome',
            'placeholder': 'Digite o nome completo',
            'required': True,
            'cols': 12
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
            'name': 'status',
            'id': 'status',
            'type': 'select',
            'label': 'Status',
            'required': True,
            'cols': 6,
            'options': [
                {'value': 'active', 'label': 'Ativo'},
                {'value': 'inactive', 'label': 'Inativo'}
            ],
            'empty_option': 'Selecione o status'
        },
        {
            'name': 'role',
            'id': 'role',
            'type': 'select',
            'label': 'Perfil',
            'required': True,
            'cols': 6,
            'options': [
                {'value': 'admin', 'label': 'Administrador'},
                {'value': 'user', 'label': 'Usuário'},
                {'value': 'manager', 'label': 'Gerente'}
            ]
        },
        {
            'name': 'notes',
            'id': 'notes',
            'type': 'textarea',
            'label': 'Observações',
            'placeholder': 'Digite observações sobre o usuário...',
            'required': False,
            'cols': 12,
            'rows': 4
        },
        {
            'name': 'active',
            'id': 'active',
            'type': 'checkbox',
            'label': 'Usuário ativo',
            'checked': True,
            'cols': 12
        }
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
        # TODO: Implementar lógica de edição
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('user.user_view'))
    
    # Exemplo de dados do usuário (em produção, viria do banco de dados)
    user_data = {
        'name': 'Caíque',
        'email': 'caique@example.com',
        'phone': '(11) 99999-9999',
        'status': 'active',
        'role': 'admin',
        'notes': 'Usuário administrador do sistema',
        'active': True
    }
    
    # Exemplo de campos para o formulário
    fields = [
        {
            'name': 'name',
            'id': 'name',
            'type': 'text',
            'label': 'Nome',
            'placeholder': 'Digite o nome completo',
            'required': True,
            'cols': 12,
            'value': user_data.get('name')
        },
        {
            'name': 'email',
            'id': 'email',
            'type': 'email',
            'label': 'E-mail',
            'placeholder': 'usuario@example.com',
            'required': True,
            'cols': 6,
            'value': user_data.get('email')
        },
        {
            'name': 'phone',
            'id': 'phone',
            'type': 'tel',
            'label': 'Telefone',
            'placeholder': '(00) 00000-0000',
            'required': False,
            'cols': 6,
            'value': user_data.get('phone')
        },
        {
            'name': 'status',
            'id': 'status',
            'type': 'select',
            'label': 'Status',
            'required': True,
            'cols': 6,
            'options': [
                {'value': 'active', 'label': 'Ativo'},
                {'value': 'inactive', 'label': 'Inativo'}
            ],
            'value': user_data.get('status')
        },
        {
            'name': 'role',
            'id': 'role',
            'type': 'select',
            'label': 'Perfil',
            'required': True,
            'cols': 6,
            'options': [
                {'value': 'admin', 'label': 'Administrador'},
                {'value': 'user', 'label': 'Usuário'},
                {'value': 'manager', 'label': 'Gerente'}
            ],
            'value': user_data.get('role')
        },
        {
            'name': 'notes',
            'id': 'notes',
            'type': 'textarea',
            'label': 'Observações',
            'placeholder': 'Digite observações sobre o usuário...',
            'required': False,
            'cols': 12,
            'rows': 4,
            'value': user_data.get('notes')
        },
        {
            'name': 'active',
            'id': 'active',
            'type': 'checkbox',
            'label': 'Usuário ativo',
            'checked': user_data.get('active', False),
            'cols': 12
        }
    ]
    
    return render_template(
        'user/form_user.html',
        title="Editar Usuário",
        subtitle=f"Editando usuário ID: {id}",
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
    # TODO: Implementar lógica de exclusão
    flash('Funcionalidade de exclusão ainda não implementada', 'info')
    return redirect(url_for('user.user_view'))