from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify
from src.features.auth.auth_decorators import login_required
from src.features.venda.venda_service import list_produtos_disponiveis, salvar_venda, list_vendas, get_venda_by_id
import json

venda_bp = Blueprint('venda', __name__, url_prefix='/venda')

@venda_bp.route('/')
@login_required
def venda_view():
    """
    Página principal de vendas
    O carrinho é gerenciado no cliente via JavaScript
    """
    produtos_data = list_produtos_disponiveis()
    
    # Verifica se a busca foi bem-sucedida
    if produtos_data.get('success'):
        produtos = produtos_data.get('data', [])
    else:
        produtos = []
        error_message = produtos_data.get('error', 'Erro ao carregar produtos')
        flash(f'Erro ao carregar produtos: {error_message}', 'error')
    
    return render_template('venda/venda_view.html', produtos=produtos)


@venda_bp.route('/finalizar', methods=['POST'])
@login_required
def finalizar():
    """
    Finaliza a venda
    Recebe os dados do carrinho via formulário
    """
    try:
        # Recebe dados do formulário
        carrinho_json = request.form.get('carrinho_json')
        forma_pagamento = request.form.get('pagamento')
        
        if not carrinho_json:
            flash('Nenhum item no carrinho', 'error')
            return redirect(url_for('venda.venda_view'))
        
        if not forma_pagamento:
            flash('Selecione uma forma de pagamento', 'error')
            return redirect(url_for('venda.venda_view'))
        
        # Parse do carrinho
        carrinho = json.loads(carrinho_json)
        
        if not carrinho or len(carrinho) == 0:
            flash('Carrinho vazio', 'error')
            return redirect(url_for('venda.venda_view'))
        
        # Obtém o ID do usuário da sessão
        user = session.get('user', {})
        user_id = user.get('id')
        
        if not user_id:
            flash('Usuário não autenticado', 'error')
            return redirect(url_for('venda.venda_view'))
        
        # Salva a venda
        response = salvar_venda(carrinho, forma_pagamento, user_id)
        
        if response.get('success'):
            flash('Venda finalizada com sucesso!', 'success')
            return redirect(url_for('venda.venda_view'))
        else:
            flash(response.get('error', 'Erro ao finalizar venda'), 'error')
            return redirect(url_for('venda.venda_view'))
            
    except json.JSONDecodeError:
        flash('Erro ao processar carrinho', 'error')
        return redirect(url_for('venda.venda_view'))
    except Exception as e:
        flash(f'Erro ao finalizar venda: {str(e)}', 'error')
        return redirect(url_for('venda.venda_view'))


@venda_bp.route('/cancelar')
@login_required
def cancelar():
    """Cancela a venda atual"""
    flash('Venda cancelada', 'warning')
    return redirect(url_for('venda.venda_view'))


@venda_bp.route('/list')
@login_required
def list_vendas_view():
    """Rota para listar todas as vendas"""
    logged_user = session.get('user', {})

    vendas_data = list_vendas()

    if not vendas_data['success']:
        flash(f'Erro ao carregar vendas: {vendas_data.get("error", "Erro desconhecido")}', 'error')
        vendas_data['data'] = []

    headers = ["Data/Hora", "Valor Total", "Método de Pagamento"]
    rows = vendas_data['data']
    
    return render_template(
        'venda/list_vendas.html',
        title="Histórico de Vendas",
        headers=headers,
        rows=rows,
        view_url='venda.view_venda',
        user=logged_user
    )


@venda_bp.route('/view/<string:id>')
@login_required
def view_venda(id):
    """Rota para visualizar os detalhes de uma venda"""
    logged_user = session.get('user', {})
    
    result = get_venda_by_id(id)
    
    if not result['success']:
        flash(f'Venda não encontrada: {result.get("error", "Erro desconhecido")}', 'error')
        return redirect(url_for('venda.list_vendas_view'))
    
    venda_data = result['data']
    
    return render_template(
        'venda/venda_detail.html',
        title="Detalhes da Venda",
        venda=venda_data,
        user=logged_user
    )