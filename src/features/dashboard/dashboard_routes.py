from flask import Blueprint, render_template, session, redirect, url_for
from src.features.auth.auth_decorators import login_required
from src.features.dashboard.dashboard_service import (
    get_produtos_proximos_vencimento,
    get_produto_mais_vendido,
    get_produtos_estoque_baixo,
    get_receita_periodo,
    get_vendas_dia,
    get_top_produtos_vendidos,
    get_valor_total_estoque,
    get_vendas_ultimos_dias,
    get_ticket_medio
)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def dashboard_view():
    """Rota do dashboard com cards informativos"""
    logged_user = session.get('user', {})
    
    # Busca os dados para os cards
    produtos_vencimento = get_produtos_proximos_vencimento(30)
    produto_mais_vendido = get_produto_mais_vendido()
    produtos_estoque_baixo = get_produtos_estoque_baixo(10)
    receita_data = get_receita_periodo()
    vendas_data = get_vendas_dia()
    top_produtos = get_top_produtos_vendidos(5)
    valor_estoque = get_valor_total_estoque()
    vendas_grafico = get_vendas_ultimos_dias(7)
    ticket_medio = get_ticket_medio()
    
    return render_template(
        'dashboard.html',
        user=logged_user,
        produtos_vencimento=produtos_vencimento.get('data', []) if produtos_vencimento.get('success') else [],
        produto_mais_vendido=produto_mais_vendido.get('data') if produto_mais_vendido.get('success') else None,
        produtos_estoque_baixo=produtos_estoque_baixo.get('data', []) if produtos_estoque_baixo.get('success') else [],
        receita=receita_data.get('data', {}) if receita_data.get('success') else {},
        vendas=vendas_data.get('data', {}) if vendas_data.get('success') else {},
        top_produtos=top_produtos.get('data', []) if top_produtos.get('success') else [],
        valor_estoque=valor_estoque.get('data', {}).get('valor_total', 0) if valor_estoque.get('success') else 0,
        vendas_grafico=vendas_grafico.get('data', []) if vendas_grafico.get('success') else [],
        ticket_medio=ticket_medio.get('data', {}) if ticket_medio.get('success') else {}
    )

