from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify
from src.features.auth.auth_decorators import login_required

venda_bp = Blueprint('venda', __name__, url_prefix='/venda')

@venda_bp.route('/')
@login_required
def venda_view():
    # Dados mockados para testar a aparência
    produtos = [
        {'id': 1, 'codigo': 'PROD001', 'nome': 'Arroz 5kg', 'preco': 24.90},
        {'id': 2, 'codigo': 'PROD002', 'nome': 'Feijão 1kg', 'preco': 8.50},
        {'id': 3, 'codigo': 'PROD003', 'nome': 'Açúcar 1kg', 'preco': 5.90},
        {'id': 4, 'codigo': 'PROD004', 'nome': 'Óleo de Soja 900ml', 'preco': 7.80},
        {'id': 5, 'codigo': 'PROD005', 'nome': 'Macarrão 500g', 'preco': 4.20},
        {'id': 6, 'codigo': 'PROD006', 'nome': 'Leite Integral 1L', 'preco': 5.50},
        {'id': 7, 'codigo': 'PROD007', 'nome': 'Café 500g', 'preco': 12.90},
        {'id': 8, 'codigo': 'PROD008', 'nome': 'Sabão em Pó 1kg', 'preco': 15.80},
        {'id': 9, 'codigo': 'PROD009', 'nome': 'Detergente 500ml', 'preco': 2.90},
        {'id': 10, 'codigo': 'PROD010', 'nome': 'Papel Higiênico 4un', 'preco': 18.50},
    ]
    
    # Carrinho mockado
    carrinho = [
        {
            'id': 1,
            'produto': {'nome': 'Arroz 5kg', 'codigo': 'PROD001', 'preco': 24.90},
            'quantidade': 2
        },
        {
            'id': 2,
            'produto': {'nome': 'Feijão 1kg', 'codigo': 'PROD002', 'preco': 8.50},
            'quantidade': 3
        },
        {
            'id': 3,
            'produto': {'nome': 'Açúcar 1kg', 'codigo': 'PROD003', 'preco': 5.90},
            'quantidade': 1
        },
    ]
    
    # Calcular total
    total = sum(item['produto']['preco'] * item['quantidade'] for item in carrinho)
    
    return render_template('venda/venda_view.html', 
                         produtos=produtos, 
                         carrinho=carrinho, 
                         total=total)


# Rotas mockadas para testar a aparência (apenas redirecionam de volta)
@venda_bp.route('/adicionar', methods=['POST'])
@login_required
def adicionar_item():
    """Rota mockada - retorna JSON se for AJAX, senão redireciona"""
    # Verifica se é uma requisição AJAX
    is_ajax = request.is_json or request.content_type == 'application/json'
    
    if is_ajax:
        data = request.get_json()
        produto_id = data.get('produto_id')
        quantidade = data.get('quantidade', 1)
        
        # Aqui você implementaria a lógica real de adicionar ao carrinho
        # Por enquanto, apenas retorna sucesso
        return jsonify({
            'success': True,
            'message': 'Item adicionado com sucesso'
        })
    else:
        flash('Item adicionado (mock)', 'info')
        return redirect(url_for('venda.venda_view'))


@venda_bp.route('/diminuir/<int:item_id>', methods=['POST'])
@login_required
def diminuir_item(item_id):
    """Rota mockada - retorna JSON se for AJAX, senão redireciona"""
    is_ajax = request.is_json or request.content_type == 'application/json'
    
    if is_ajax:
        # Aqui você implementaria a lógica real de diminuir quantidade
        return jsonify({
            'success': True,
            'message': 'Quantidade diminuída com sucesso'
        })
    else:
        flash('Quantidade diminuída (mock)', 'info')
        return redirect(url_for('venda.venda_view'))


@venda_bp.route('/aumentar/<int:item_id>', methods=['POST'])
@login_required
def aumentar_item(item_id):
    """Rota mockada - retorna JSON se for AJAX, senão redireciona"""
    is_ajax = request.is_json or request.content_type == 'application/json'
    
    if is_ajax:
        # Aqui você implementaria a lógica real de aumentar quantidade
        return jsonify({
            'success': True,
            'message': 'Quantidade aumentada com sucesso'
        })
    else:
        flash('Quantidade aumentada (mock)', 'info')
        return redirect(url_for('venda.venda_view'))


@venda_bp.route('/remover/<int:item_id>', methods=['POST'])
@login_required
def remover_item(item_id):
    """Rota mockada - retorna JSON se for AJAX, senão redireciona"""
    is_ajax = request.is_json or request.content_type == 'application/json'
    
    if is_ajax:
        # Aqui você implementaria a lógica real de remover item
        return jsonify({
            'success': True,
            'message': 'Item removido com sucesso'
        })
    else:
        flash('Item removido (mock)', 'info')
        return redirect(url_for('venda.venda_view'))


@venda_bp.route('/finalizar', methods=['POST'])
@login_required
def finalizar():
    """Rota mockada - apenas redireciona de volta para testar aparência"""
    flash('Venda finalizada (mock)', 'success')
    return redirect(url_for('venda.venda_view'))


@venda_bp.route('/cancelar')
@login_required
def cancelar():
    """Rota mockada - apenas redireciona de volta para testar aparência"""
    flash('Venda cancelada (mock)', 'warning')
    return redirect(url_for('venda.venda_view'))