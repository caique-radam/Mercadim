from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from src.features.auth.auth_decorators import login_required
from src.features.produtos.produtos_service import (
    list_produtos, 
    create_produto as create_produto_service, 
    get_produto_by_id, 
    update_produto, 
    delete_produto as delete_produto_service,
    get_fornecedores_for_select
)

produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos')


def get_form_fields(produto_data=None, fornecedores=None):
    """
    Retorna os campos do formulário de produto.
    Se produto_data for fornecido, preenche os valores (modo edição).
    """
    # Prepara opções do select de fornecedores
    fornecedor_options = []
    if fornecedores:
        fornecedor_options = [{'value': str(f['id']), 'label': f['nome']} for f in fornecedores]
    
    fields = [
        {
            'name': 'nome',
            'id': 'nome',
            'type': 'text',
            'label': 'Nome do Produto',
            'placeholder': 'Digite o nome do produto',
            'required': True,
            'cols': 12
        },
        {
            'name': 'preco_custo',
            'id': 'preco_custo',
            'type': 'number',
            'label': 'Preço de Custo',
            'placeholder': '0.00',
            'required': False,
            'cols': 4,
            'step': '0.01'
        },
        {
            'name': 'preco_venda',
            'id': 'preco_venda',
            'type': 'number',
            'label': 'Preço de Venda',
            'placeholder': '0.00',
            'required': False,
            'cols': 4,
            'step': '0.01'
        },
        {
            'name': 'quantidade',
            'id': 'quantidade',
            'type': 'number',
            'label': 'Quantidade',
            'placeholder': '0',
            'required': False,
            'cols': 4,
            'step': '0.01'
        },
        {
            'name': 'uni_medida',
            'id': 'uni_medida',
            'type': 'text',
            'label': 'Unidade de Medida',
            'placeholder': 'Ex: kg, un, litros',
            'required': False,
            'cols': 6
        },
        {
            'name': 'validade_lote',
            'id': 'validade_lote',
            'type': 'date',
            'label': 'Validade do Lote',
            'placeholder': '',
            'required': False,
            'cols': 6
        },
        {
            'name': 'codigo_barra',
            'id': 'codigo_barra',
            'type': 'number',
            'label': 'Código de Barras',
            'placeholder': '7891234567890',
            'required': False,
            'cols': 6,
            'step': '1'
        },
        {
            'name': 'id_fornecedor',
            'id': 'id_fornecedor',
            'type': 'select',
            'label': 'Fornecedor',
            'required': False,
            'cols': 6,
            'options': fornecedor_options,
            'empty_option': 'Selecione um fornecedor'
        }
    ]
    
    # Se estiver editando, preenche os valores
    if produto_data:
        for field in fields:
            field_name = field['name']
            if field_name == 'id_fornecedor':
                # Extrai o id_fornecedor (pode vir do objeto fornecedores ou direto)
                fornecedor_id = produto_data.get('id_fornecedor')
                field['value'] = str(fornecedor_id) if fornecedor_id else ''
            elif field_name == 'validade_lote':
                # Data pode vir em formato diferente
                validade = produto_data.get('validade_lote', '') or ''
                field['value'] = validade
            else:
                field['value'] = produto_data.get(field_name, '')
    
    return fields


def collect_form_data():
    """Coleta e limpa os dados do formulário"""
    return {
        'nome': request.form.get('nome', '').strip(),
        'preco_custo': request.form.get('preco_custo', '').strip() or None,
        'preco_venda': request.form.get('preco_venda', '').strip() or None,
        'quantidade': request.form.get('quantidade', '').strip() or None,
        'validade_lote': request.form.get('validade_lote', '').strip() or None,
        'codigo_barra': request.form.get('codigo_barra', '').strip() or None,
        'id_fornecedor': request.form.get('id_fornecedor', '').strip() or None,
        'uni_medida': request.form.get('uni_medida', '').strip() or None
    }


@produtos_bp.route('/')
@login_required
def produtos_view():
    """Rota para listar todos os produtos"""
    logged_user = session.get('user', {})

    produtos_data = list_produtos()

    if not produtos_data['success']:
        flash(f'Erro ao carregar produtos: {produtos_data.get("error", "Erro desconhecido")}', 'error')
        produtos_data['data'] = []

    headers = ["Nome", "Preço Custo", "Preço Venda", "Quantidade", "Validade", "Código de Barras", "Fornecedor"]
    rows = produtos_data['data']
    
    return render_template(
        'produtos/list_produtos.html',
        title="Lista de Produtos",
        headers=headers,
        rows=rows,
        add_url=url_for('produtos.create_produto'),
        edit_url='produtos.edit_produto',
        delete_url='produtos.delete_produto',
        user=logged_user
    )


@produtos_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_produto():
    """Rota para criar um novo produto"""
    logged_user = session.get('user', {})
    
    # Busca fornecedores para o select
    fornecedores_result = get_fornecedores_for_select()
    fornecedores = fornecedores_result.get('data', []) if fornecedores_result.get('success') else []
    
    if request.method == 'POST':
        produto_data = collect_form_data()
        
        # Validação básica
        if not produto_data['nome']:
            flash('Nome do produto é obrigatório', 'error')
            return redirect(url_for('produtos.create_produto'))
        
        # Chama o serviço para criar o produto
        result = create_produto_service(produto_data)
        
        if result['success']:
            flash('Produto criado com sucesso!', 'success')
            return redirect(url_for('produtos.produtos_view'))
        else:
            flash(f'Erro ao criar produto: {result.get("error", "Erro desconhecido")}', 'error')
            return redirect(url_for('produtos.create_produto'))
    
    # GET: mostra formulário vazio
    fields = get_form_fields(fornecedores=fornecedores)
    
    return render_template(
        'produtos/form_produto.html',
        title="Criar Novo Produto",
        subtitle="Preencha os dados do novo produto",
        fields=fields,
        action_url=url_for('produtos.create_produto'),
        method='POST',
        cancel_url=url_for('produtos.produtos_view'),
        submit_label='Criar Produto',
        user=logged_user
    )


@produtos_bp.route('/edit/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_produto(id):
    """Rota para editar um produto"""
    logged_user = session.get('user', {})
    
    # Busca fornecedores para o select
    fornecedores_result = get_fornecedores_for_select()
    fornecedores = fornecedores_result.get('data', []) if fornecedores_result.get('success') else []
    
    if request.method == 'POST':
        produto_data = collect_form_data()
        
        # Validação básica
        if not produto_data['nome']:
            flash('Nome do produto é obrigatório', 'error')
            return redirect(url_for('produtos.edit_produto', id=id))
        
        # Chama o serviço para atualizar o produto
        result = update_produto(id, produto_data)
        
        if result['success']:
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('produtos.produtos_view'))
        else:
            flash(f'Erro ao atualizar produto: {result.get("error", "Erro desconhecido")}', 'error')
            return redirect(url_for('produtos.edit_produto', id=id))
    
    # GET: busca dados e mostra formulário preenchido
    result = get_produto_by_id(id)
    
    if not result['success']:
        flash(f'Produto não encontrado: {result.get("error", "Erro desconhecido")}', 'error')
        return redirect(url_for('produtos.produtos_view'))
    
    produto_data = result['data']
    fields = get_form_fields(produto_data=produto_data, fornecedores=fornecedores)
    
    return render_template(
        'produtos/form_produto.html',
        title="Editar Produto",
        subtitle=f"Editando produto: {produto_data.get('nome', '')}",
        fields=fields,
        action_url=url_for('produtos.edit_produto', id=id),
        method='POST',
        cancel_url=url_for('produtos.produtos_view'),
        submit_label='Salvar Alterações',
        data=produto_data,
        user=logged_user
    )


@produtos_bp.route('/delete/<string:id>', methods=['POST'])
@login_required
def delete_produto(id):
    """Rota para deletar um produto"""
    result = delete_produto_service(id)
    
    if result['success']:
        flash('Produto deletado com sucesso!', 'success')
    else:
        flash(f'Erro ao deletar produto: {result.get("error", "Erro desconhecido")}', 'error')
    
    return redirect(url_for('produtos.produtos_view'))
