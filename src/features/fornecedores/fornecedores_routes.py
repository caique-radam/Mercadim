from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from src.features.auth.auth_decorators import login_required
from src.features.fornecedores.fornecedores_service import (
    list_fornecedores, 
    create_fornecedor as create_fornecedor_service, 
    get_fornecedor_by_id, 
    update_fornecedor, 
    delete_fornecedor as delete_fornecedor_service
)

fornecedores_bp = Blueprint('fornecedores', __name__, url_prefix='/fornecedores')


def get_form_fields(fornecedor_data=None):
    """
    Retorna os campos do formulário de fornecedor.
    Se fornecedor_data for fornecido, preenche os valores (modo edição).
    """
    fields = [
        {
            'name': 'nome_fantasia',
            'id': 'nome_fantasia',
            'type': 'text',
            'label': 'Nome Fantasia',
            'placeholder': 'Digite o nome fantasia',
            'required': True,
            'cols': 12
        },
        {
            'name': 'email',
            'id': 'email',
            'type': 'email',
            'label': 'E-mail',
            'placeholder': 'fornecedor@example.com',
            'required': False,
            'cols': 6
        },
        {
            'name': 'telefone',
            'id': 'telefone',
            'type': 'tel',
            'label': 'Telefone',
            'placeholder': '(00) 00000-0000',
            'required': False,
            'cols': 6
        },
        {
            'name': 'cep',
            'id': 'cep',
            'type': 'text',
            'label': 'CEP',
            'placeholder': '00000-000',
            'required': False,
            'cols': 4
        },
        {
            'name': 'estado',
            'id': 'estado',
            'type': 'text',
            'label': 'Estado',
            'placeholder': 'UF',
            'required': False,
            'cols': 4
        },
        {
            'name': 'cidade',
            'id': 'cidade',
            'type': 'text',
            'label': 'Cidade',
            'placeholder': 'Digite a cidade',
            'required': False,
            'cols': 4
        },
        {
            'name': 'bairro',
            'id': 'bairro',
            'type': 'text',
            'label': 'Bairro',
            'placeholder': 'Digite o bairro',
            'required': False,
            'cols': 6
        },
        {
            'name': 'endereco',
            'id': 'endereco',
            'type': 'text',
            'label': 'Endereço',
            'placeholder': 'Digite o endereço completo',
            'required': False,
            'cols': 6
        },
        {
            'name': 'frete',
            'id': 'frete',
            'type': 'number',
            'label': 'Frete',
            'placeholder': '0.00',
            'required': False,
            'cols': 6,
            'step': '0.01'
        },
        {
            'name': 'status',
            'id': 'status',
            'type': 'checkbox',
            'label': 'Status Ativo',
            'required': False,
            'cols': 6
        }
    ]
    
    # Se estiver editando, preenche os valores
    if fornecedor_data:
        for field in fields:
            field_name = field['name']
            if field_name == 'status':
                field['checked'] = bool(fornecedor_data.get('status', False))
            elif field_name == 'frete':
                # Campo numérico: converte para string, trata None
                frete_value = fornecedor_data.get(field_name)
                field['value'] = str(frete_value) if frete_value is not None else ''
            else:
                # Campos de texto: trata None como string vazia
                value = fornecedor_data.get(field_name)
                field['value'] = str(value) if value is not None else ''
    else:
        # Modo criação: status padrão como ativo
        for field in fields:
            if field['name'] == 'status':
                field['checked'] = True
    
    return fields


def collect_form_data():
    """Coleta e limpa os dados do formulário"""
    return {
        'nome_fantasia': request.form.get('nome_fantasia', '').strip(),
        'email': request.form.get('email', '').strip() or None,
        'telefone': request.form.get('telefone', '').strip() or None,
        'cidade': request.form.get('cidade', '').strip() or None,
        'estado': request.form.get('estado', '').strip() or None,
        'endereco': request.form.get('endereco', '').strip() or None,
        'bairro': request.form.get('bairro', '').strip() or None,
        'cep': request.form.get('cep', '').strip() or None,
        'frete': request.form.get('frete', '').strip() or None,
        'status': request.form.get('status') == 'on' or request.form.get('status') == 'true'
    }


@fornecedores_bp.route('/')
@login_required
def fornecedores_view():
    """Rota para listar todos os fornecedores"""
    logged_user = session.get('user', {})

    fornecedores_data = list_fornecedores()

    if not fornecedores_data['success']:
        flash(f'Erro ao carregar fornecedores: {fornecedores_data.get("error", "Erro desconhecido")}', 'error')
        fornecedores_data['data'] = []

    headers = ["Nome Fantasia", "Email", "Telefone", "Cidade", "Estado", "Status"]
    rows = fornecedores_data['data']
    
    return render_template(
        'fornecedores/list_fornecedores.html',
        title="Lista de Fornecedores",
        headers=headers,
        rows=rows,
        add_url=url_for('fornecedores.create_fornecedor'),
        edit_url='fornecedores.edit_fornecedor',
        delete_url='fornecedores.delete_fornecedor',
        user=logged_user
    )


@fornecedores_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_fornecedor():
    """Rota para criar um novo fornecedor"""
    logged_user = session.get('user', {})
    
    if request.method == 'POST':
        fornecedor_data = collect_form_data()
        
        # Validação básica
        if not fornecedor_data['nome_fantasia']:
            flash('Nome fantasia é obrigatório', 'error')
            return redirect(url_for('fornecedores.create_fornecedor'))
        
        # Chama o serviço para criar o fornecedor
        result = create_fornecedor_service(fornecedor_data)
        
        if result['success']:
            flash('Fornecedor criado com sucesso!', 'success')
            return redirect(url_for('fornecedores.fornecedores_view'))
        else:
            flash(f'Erro ao criar fornecedor: {result.get("error", "Erro desconhecido")}', 'error')
            return redirect(url_for('fornecedores.create_fornecedor'))
    
    # GET: mostra formulário vazio
    fields = get_form_fields()
    
    return render_template(
        'fornecedores/form_fornecedor.html',
        title="Criar Novo Fornecedor",
        subtitle="Preencha os dados do novo fornecedor",
        fields=fields,
        action_url=url_for('fornecedores.create_fornecedor'),
        method='POST',
        cancel_url=url_for('fornecedores.fornecedores_view'),
        submit_label='Criar Fornecedor',
        user=logged_user
    )


@fornecedores_bp.route('/edit/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_fornecedor(id):
    """Rota para editar um fornecedor"""
    logged_user = session.get('user', {})
    
    if request.method == 'POST':
        fornecedor_data = collect_form_data()
        
        # Validação básica
        if not fornecedor_data['nome_fantasia']:
            flash('Nome fantasia é obrigatório', 'error')
            return redirect(url_for('fornecedores.edit_fornecedor', id=id))
        
        # Chama o serviço para atualizar o fornecedor
        result = update_fornecedor(id, fornecedor_data)
        
        if result['success']:
            flash('Fornecedor atualizado com sucesso!', 'success')
            return redirect(url_for('fornecedores.fornecedores_view'))
        else:
            flash(f'Erro ao atualizar fornecedor: {result.get("error", "Erro desconhecido")}', 'error')
            return redirect(url_for('fornecedores.edit_fornecedor', id=id))
    
    # GET: busca dados e mostra formulário preenchido
    result = get_fornecedor_by_id(id)
    
    if not result['success']:
        flash(f'Fornecedor não encontrado: {result.get("error", "Erro desconhecido")}', 'error')
        return redirect(url_for('fornecedores.fornecedores_view'))
    
    fornecedor_data = result['data']
    fields = get_form_fields(fornecedor_data)
    
    return render_template(
        'fornecedores/form_fornecedor.html',
        title="Editar Fornecedor",
        subtitle=f"Editando fornecedor: {fornecedor_data.get('nome_fantasia', '')}",
        fields=fields,
        action_url=url_for('fornecedores.edit_fornecedor', id=id),
        method='POST',
        cancel_url=url_for('fornecedores.fornecedores_view'),
        submit_label='Salvar Alterações',
        data=fornecedor_data,
        user=logged_user
    )


@fornecedores_bp.route('/delete/<string:id>', methods=['POST'])
@login_required
def delete_fornecedor(id):
    """Rota para deletar um fornecedor"""
    result = delete_fornecedor_service(id)
    
    if result['success']:
        flash('Fornecedor deletado com sucesso!', 'success')
    else:
        flash(f'Erro ao deletar fornecedor: {result.get("error", "Erro desconhecido")}', 'error')
    
    return redirect(url_for('fornecedores.fornecedores_view'))
