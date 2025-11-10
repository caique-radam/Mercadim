from src.core.database import supabase_client
from datetime import datetime, timedelta
import time

# Cache simples em memória para dados do dashboard
_dashboard_cache = {}
_cache_ttl = 60  # Cache válido por 60 segundos


def _get_inicio_dia(data=None):
    """Retorna o início do dia (00:00:00) para uma data"""
    if data is None:
        data = datetime.now()
    return data.replace(hour=0, minute=0, second=0, microsecond=0)


def _get_fim_dia(data=None):
    """Retorna o fim do dia (23:59:59) para uma data"""
    if data is None:
        data = datetime.now()
    return data.replace(hour=23, minute=59, second=59, microsecond=999999)


def _get_inicio_mes(data=None):
    """Retorna o início do mês para uma data"""
    if data is None:
        data = datetime.now()
    return data.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _get_produtos_map(produto_ids):
    """
    Busca nomes de múltiplos produtos de uma vez (otimização para evitar N+1)
    
    Args:
        produto_ids: Lista de IDs de produtos
        
    Returns:
        Dict com {produto_id: nome}
    """
    if not produto_ids:
        return {}
    
    try:
        response = (
            supabase_client()
            .table("produtos")
            .select("id, nome")
            .in_("id", produto_ids)
            .execute()
        )
        
        produtos_map = {}
        for produto in response.data:
            produtos_map[produto.get('id')] = produto.get('nome', 'Produto Desconhecido')
        
        return produtos_map
    except:
        return {}


def _calcular_receita_vendas(data_inicio, data_fim=None):
    """Calcula a receita total de vendas em um período"""
    try:
        query = (
            supabase_client()
            .table("vendas")
            .select("valor_venda")
            .gte("data_venda", data_inicio.isoformat())
        )
        
        if data_fim:
            query = query.lte("data_venda", data_fim.isoformat())
        
        response = query.execute()
        return sum(float(v.get('valor_venda', 0)) for v in response.data)
    except:
        return 0.0


def _get_cache_key(function_name, *args, **kwargs):
    """Gera uma chave de cache baseada na função e argumentos"""
    key_parts = [function_name]
    if args:
        key_parts.extend(str(arg) for arg in args)
    if kwargs:
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)


def _get_cached_or_compute(cache_key, compute_func, ttl=_cache_ttl):
    """
    Retorna valor do cache se válido, senão computa e armazena
    
    Args:
        cache_key: Chave do cache
        compute_func: Função para computar o valor se não estiver em cache
        ttl: Tempo de vida do cache em segundos (padrão: 60)
    
    Returns:
        Valor do cache ou resultado da função
    """
    current_time = time.time()
    
    # Verifica se existe no cache e se ainda é válido
    if cache_key in _dashboard_cache:
        cached_value, cached_time = _dashboard_cache[cache_key]
        if current_time - cached_time < ttl:
            return cached_value
    
    # Computa novo valor
    result = compute_func()
    _dashboard_cache[cache_key] = (result, current_time)
    
    # Limpa cache antigo (mantém apenas últimos 100 itens)
    if len(_dashboard_cache) > 100:
        oldest_key = min(_dashboard_cache.keys(), key=lambda k: _dashboard_cache[k][1])
        del _dashboard_cache[oldest_key]
    
    return result


def clear_dashboard_cache():
    """Limpa o cache do dashboard (útil após operações que alteram dados)"""
    global _dashboard_cache
    _dashboard_cache.clear()


def _contar_vendas(data_inicio, data_fim=None):
    """Conta o número de vendas em um período"""
    try:
        query = (
            supabase_client()
            .table("vendas")
            .select("id", count="exact")
            .gte("data_venda", data_inicio.isoformat())
        )
        
        if data_fim:
            query = query.lte("data_venda", data_fim.isoformat())
        
        response = query.execute()
        # Usa count se disponível, senão conta os dados
        if hasattr(response, 'count') and response.count is not None:
            return response.count
        return len(response.data) if response.data else 0
    except:
        return 0


def get_produtos_proximos_vencimento(dias=30, limit=50):
    """
    Busca produtos próximos do vencimento dentro do período especificado
    
    Args:
        dias: Número de dias para verificar (padrão: 30)
        limit: Limite de produtos a retornar (padrão: 50)
    
    Returns:
        {
            'success': bool,
            'data': list de dicts com dados dos produtos (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        hoje = datetime.now()
        data_limite = (hoje + timedelta(days=dias)).strftime('%Y-%m-%d')
        data_atual = hoje.strftime('%Y-%m-%d')
        
        response = (
            supabase_client()
            .table("produtos")
            .select("id, nome, validade_lote, quantidade, uni_medida")
            .not_.is_("validade_lote", "null")
            .gte("validade_lote", data_atual)
            .lte("validade_lote", data_limite)
            .gt("quantidade", 0)
            .order("validade_lote", desc=False)
            .limit(limit)
            .execute()
        )
        
        produtos = []
        for produto in response.data:
            validade_str = produto.get('validade_lote', '')
            if validade_str:
                try:
                    data_validade = datetime.strptime(validade_str, '%Y-%m-%d')
                    dias_para_vencer = (data_validade - hoje).days
                    
                    produtos.append({
                        'id': produto.get('id'),
                        'nome': produto.get('nome', ''),
                        'validade_lote': data_validade.strftime('%d/%m/%Y'),
                        'dias_para_vencer': dias_para_vencer,
                        'quantidade': float(produto.get('quantidade', 0)),
                        'uni_medida': produto.get('uni_medida', '')
                    })
                except (ValueError, TypeError):
                    continue
        
        return {"success": True, "data": produtos}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


def get_produto_mais_vendido():
    """
    Busca o produto mais vendido (baseado na quantidade total vendida)
    Otimizado para evitar N+1 queries usando JOIN
    
    Returns:
        {
            'success': bool,
            'data': dict com dados do produto mais vendido (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        # Usa JOIN para buscar dados do produto junto com itens_vendas
        response = (
            supabase_client()
            .table("itens_vendas")
            .select("id_produto, quantidade, produtos(nome)")
            .execute()
        )
        
        if not response.data:
            return {
                "success": True,
                "data": None,
                "message": "Nenhuma venda encontrada"
            }
        
        # Agrupa por produto e soma as quantidades
        vendas_por_produto = {}
        for item in response.data:
            produto_id = item.get('id_produto')
            quantidade = float(item.get('quantidade', 0))
            
            if produto_id:
                if produto_id not in vendas_por_produto:
                    # Extrai nome do produto do JOIN
                    produto_info = item.get('produtos', {})
                    produto_nome = produto_info.get('nome', 'Produto Desconhecido') if isinstance(produto_info, dict) else 'Produto Desconhecido'
                    
                    vendas_por_produto[produto_id] = {
                        'id': produto_id,
                        'nome': produto_nome,
                        'quantidade_total': 0
                    }
                vendas_por_produto[produto_id]['quantidade_total'] += quantidade
        
        if not vendas_por_produto:
            return {
                "success": True,
                "data": None,
                "message": "Nenhuma venda encontrada"
            }
        
        # Encontra o produto com maior quantidade vendida
        produto_mais_vendido = max(
            vendas_por_produto.values(),
            key=lambda x: x['quantidade_total']
        )
        
        return {"success": True, "data": produto_mais_vendido}
    except Exception as e:
        return {"success": False, "error": str(e), "data": None}


def get_produtos_estoque_baixo(limite=10, max_results=50):
    """
    Busca produtos com estoque baixo (quantidade <= limite)
    
    Args:
        limite: Quantidade máxima para considerar estoque baixo (padrão: 10)
        max_results: Número máximo de resultados a retornar (padrão: 50)
    
    Returns:
        {
            'success': bool,
            'data': list de dicts com dados dos produtos (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        response = (
            supabase_client()
            .table("produtos")
            .select("id, nome, quantidade, uni_medida")
            .lte("quantidade", limite)
            .order("quantidade", desc=False)
            .limit(max_results)
            .execute()
        )
        
        produtos = [
            {
                'id': p.get('id'),
                'nome': p.get('nome', ''),
                'quantidade': float(p.get('quantidade', 0)),
                'uni_medida': p.get('uni_medida', '')
            }
            for p in response.data
        ]
        
        return {"success": True, "data": produtos}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


def get_receita_periodo():
    """
    Calcula a receita do dia e do mês atual
    Com cache para melhor performance
    
    Returns:
        {
            'success': bool,
            'data': dict com receita_hoje, receita_mes, receita_mes_anterior (se success=True),
            'error': str (se success=False)
        }
    """
    cache_key = _get_cache_key("get_receita_periodo")
    
    def compute():
        try:
            hoje = datetime.now()
            inicio_dia = _get_inicio_dia(hoje)
            inicio_mes = _get_inicio_mes(hoje)
            inicio_mes_anterior = _get_inicio_mes(inicio_mes - timedelta(days=1))
            fim_mes_anterior = inicio_mes - timedelta(seconds=1)
            
            receita_hoje = _calcular_receita_vendas(inicio_dia)
            receita_mes = _calcular_receita_vendas(inicio_mes)
            receita_mes_anterior = _calcular_receita_vendas(inicio_mes_anterior, fim_mes_anterior)
            
            # Calcula variação percentual
            variacao_percentual = 0
            if receita_mes_anterior > 0:
                variacao_percentual = ((receita_mes - receita_mes_anterior) / receita_mes_anterior) * 100
            
            return {
                "success": True,
                "data": {
                    "receita_hoje": receita_hoje,
                    "receita_mes": receita_mes,
                    "receita_mes_anterior": receita_mes_anterior,
                    "variacao_percentual": variacao_percentual
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": {
                    "receita_hoje": 0,
                    "receita_mes": 0,
                    "receita_mes_anterior": 0,
                    "variacao_percentual": 0
                }
            }
    
    return _get_cached_or_compute(cache_key, compute, ttl=30)  # Cache menor para receita (30s)


def get_vendas_dia():
    """
    Retorna quantidade de vendas do dia e comparação com ontem
    
    Returns:
        {
            'success': bool,
            'data': dict com vendas_hoje, vendas_ontem (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        hoje = datetime.now()
        ontem = hoje - timedelta(days=1)
        
        inicio_hoje = _get_inicio_dia(hoje)
        fim_hoje = _get_fim_dia(hoje)
        inicio_ontem = _get_inicio_dia(ontem)
        fim_ontem = _get_fim_dia(ontem)
        
        vendas_hoje = _contar_vendas(inicio_hoje, fim_hoje)
        vendas_ontem = _contar_vendas(inicio_ontem, fim_ontem)
        
        return {
            "success": True,
            "data": {
                "vendas_hoje": vendas_hoje,
                "vendas_ontem": vendas_ontem,
                "variacao": vendas_hoje - vendas_ontem
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {"vendas_hoje": 0, "vendas_ontem": 0, "variacao": 0}
        }


def get_top_produtos_vendidos(limit=5):
    """
    Retorna os top N produtos mais vendidos
    Otimizado para evitar N+1 queries usando JOIN
    
    Args:
        limit: Número de produtos a retornar (padrão: 5)
    
    Returns:
        {
            'success': bool,
            'data': list de dicts com dados dos produtos (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        # Usa JOIN para buscar dados do produto junto com itens_vendas
        response = (
            supabase_client()
            .table("itens_vendas")
            .select("id_produto, quantidade, preco_unitario, produtos(nome)")
            .execute()
        )
        
        if not response.data:
            return {
                "success": True,
                "data": [],
                "message": "Nenhuma venda encontrada"
            }
        
        # Agrupa por produto e soma as quantidades e receita
        vendas_por_produto = {}
        for item in response.data:
            produto_id = item.get('id_produto')
            quantidade = float(item.get('quantidade', 0))
            preco_unitario = float(item.get('preco_unitario', 0))
            
            if produto_id:
                if produto_id not in vendas_por_produto:
                    # Extrai nome do produto do JOIN
                    produto_info = item.get('produtos', {})
                    produto_nome = produto_info.get('nome', 'Produto Desconhecido') if isinstance(produto_info, dict) else 'Produto Desconhecido'
                    
                    vendas_por_produto[produto_id] = {
                        'id': produto_id,
                        'nome': produto_nome,
                        'quantidade_total': 0,
                        'receita_total': 0
                    }
                vendas_por_produto[produto_id]['quantidade_total'] += quantidade
                vendas_por_produto[produto_id]['receita_total'] += quantidade * preco_unitario
        
        # Ordena por quantidade total e pega os top N
        produtos_ordenados = sorted(
            vendas_por_produto.values(),
            key=lambda x: x['quantidade_total'],
            reverse=True
        )[:limit]
        
        return {"success": True, "data": produtos_ordenados}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


def get_valor_total_estoque():
    """
    Calcula o valor total do estoque (quantidade × preço de custo)
    Com cache para melhor performance
    
    Returns:
        {
            'success': bool,
            'data': dict com valor_total (se success=True),
            'error': str (se success=False)
        }
    """
    cache_key = _get_cache_key("get_valor_total_estoque")
    
    def compute():
        try:
            response = (
                supabase_client()
                .table("produtos")
                .select("quantidade, preco_custo")
                .execute()
            )
            
            valor_total = sum(
                float(p.get('quantidade', 0) or 0) * float(p.get('preco_custo', 0) or 0)
                for p in response.data
            )
            
            return {
                "success": True,
                "data": {"valor_total": valor_total}
            }
        except Exception as e:
            return {"success": False, "error": str(e), "data": {"valor_total": 0}}
    
    return _get_cached_or_compute(cache_key, compute, ttl=120)  # Cache maior para estoque (2min)


def get_vendas_ultimos_dias(dias=7):
    """
    Retorna dados de vendas dos últimos N dias para gráfico
    
    Args:
        dias: Número de dias para buscar (padrão: 7)
    
    Returns:
        {
            'success': bool,
            'data': list de dicts com data e valor (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        hoje = datetime.now()
        data_inicio = _get_inicio_dia(hoje - timedelta(days=dias-1))
        
        response = (
            supabase_client()
            .table("vendas")
            .select("data_venda, valor_venda")
            .gte("data_venda", data_inicio.isoformat())
            .order("data_venda", desc=False)
            .execute()
        )
        
        # Agrupa por dia
        vendas_por_dia = {}
        for venda in response.data:
            data_venda_str = venda.get('data_venda', '')
            if data_venda_str:
                try:
                    if isinstance(data_venda_str, str):
                        dt = datetime.fromisoformat(data_venda_str.replace('Z', '+00:00'))
                    else:
                        dt = data_venda_str
                    
                    data_key = dt.strftime('%Y-%m-%d')
                    valor = float(venda.get('valor_venda', 0))
                    
                    vendas_por_dia[data_key] = vendas_por_dia.get(data_key, 0) + valor
                except:
                    continue
        
        # Preenche todos os dias do período (mesmo que não tenha venda)
        dados_grafico = []
        for i in range(dias):
            data = _get_inicio_dia(hoje - timedelta(days=dias-1-i))
            data_key = data.strftime('%Y-%m-%d')
            data_formatada = data.strftime('%d/%m')
            
            dados_grafico.append({
                'data': data_formatada,
                'valor': vendas_por_dia.get(data_key, 0)
            })
        
        return {"success": True, "data": dados_grafico}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


def get_ticket_medio():
    """
    Calcula o ticket médio (valor médio por venda) do dia e do mês
    
    Returns:
        {
            'success': bool,
            'data': dict com ticket_medio_hoje, ticket_medio_mes (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        hoje = datetime.now()
        inicio_dia = _get_inicio_dia(hoje)
        inicio_mes = _get_inicio_mes(hoje)
        
        # Ticket médio do dia
        receita_hoje = _calcular_receita_vendas(inicio_dia)
        num_vendas_hoje = _contar_vendas(inicio_dia)
        ticket_medio_hoje = receita_hoje / num_vendas_hoje if num_vendas_hoje > 0 else 0
        
        # Ticket médio do mês
        receita_mes = _calcular_receita_vendas(inicio_mes)
        num_vendas_mes = _contar_vendas(inicio_mes)
        ticket_medio_mes = receita_mes / num_vendas_mes if num_vendas_mes > 0 else 0
        
        return {
            "success": True,
            "data": {
                "ticket_medio_hoje": ticket_medio_hoje,
                "ticket_medio_mes": ticket_medio_mes
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {"ticket_medio_hoje": 0, "ticket_medio_mes": 0}
        }
