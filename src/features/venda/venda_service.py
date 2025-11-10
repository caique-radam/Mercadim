from src.core.database import supabase_client

def list_produtos_disponiveis(limit=500):
    """
    Lista produtos disponíveis (quantidade > 0) para venda
    Otimizado com limite
    
    Args:
        limit: Número máximo de produtos a retornar (padrão: 500)
    
    Returns:
        {
            'success': bool,
            'data': list de dicionários com dados dos produtos (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        # Busca produtos diretamente do banco, com limite
        response = (
            supabase_client()
            .table("produtos")
            .select("id, nome, preco_venda, quantidade, uni_medida, codigo_barra")
            .gt("quantidade", 0)
            .order("nome", desc=False)
            .limit(limit)
            .execute()
        )

        produtos_disponiveis = []
        for produto in response.data:
            produtos_disponiveis.append({
                'id': produto.get('id'),
                'nome': produto.get('nome', ''),
                'preco_venda': float(produto.get('preco_venda', 0)) if produto.get('preco_venda') else 0,
                'quantidade': float(produto.get('quantidade', 0)) if produto.get('quantidade') else 0,
                'uni_medida': produto.get('uni_medida', ''),
                'codigo_barra': str(int(produto.get('codigo_barra'))) if produto.get('codigo_barra') else ''
            })

        return {"success": True, "data": produtos_disponiveis}
    except Exception as e:
        return {"success": False, "error": str(e)}

def salvar_venda(carrinho: list, forma_pagamento: str, user_id: int):
    """
    Salva uma venda no banco de dados
    
    Args:
        carrinho: Lista de itens do carrinho [{id, nome, preco_venda, quantidade, uni_medida}]
        forma_pagamento: Forma de pagamento (dinheiro, cartao, pix)
        user_id: ID do usuário que está realizando a venda (não é salvo no banco, apenas para validação)
    
    Returns:
        {
            'success': bool,
            'message': str (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        from datetime import datetime
        
        if not user_id:
            return {"success": False, "error": "ID do usuário é obrigatório"}
        
        if not carrinho or len(carrinho) == 0:
            return {"success": False, "error": "Carrinho vazio"}
        
        # Calcula o valor total da venda
        valor_venda = sum(item.get('preco_venda', 0) * item.get('quantidade', 0) for item in carrinho)
        
        # Cria o registro da venda conforme schema do banco
        # Tabela: vendas
        # Campos: id (auto), data_venda, valor_venda, metodo_pagamento
        venda_data = {
            'valor_venda': float(valor_venda),
            'metodo_pagamento': forma_pagamento,
            'data_venda': datetime.now().isoformat()  # Supabase converte ISO para timestamp
        }
        
        # Insere a venda no banco
        venda_response = (
            supabase_client()
            .table("vendas")
            .insert(venda_data)
            .execute()
        )
        
        if not venda_response.data or len(venda_response.data) == 0:
            return {"success": False, "error": "Erro ao criar registro de venda"}
        
        venda_id = venda_response.data[0].get('id')
        
        # Cria os itens da venda e atualiza o estoque
        itens_venda = []
        for item in carrinho:
            produto_id = item.get('id')
            quantidade_vendida = float(item.get('quantidade', 0))
            preco_venda = float(item.get('preco_venda', 0))
            
            # Busca o produto atual para verificar estoque
            produto_atual = (
                supabase_client()
                .table("produtos")
                .select("quantidade")
                .eq("id", produto_id)
                .execute()
            )
            
            if not produto_atual.data or len(produto_atual.data) == 0:
                return {"success": False, "error": f"Produto {produto_id} não encontrado"}
            
            estoque_atual = float(produto_atual.data[0].get('quantidade', 0))
            
            if estoque_atual < quantidade_vendida:
                return {"success": False, "error": f"Estoque insuficiente para o produto {item.get('nome', '')}"}
            
            # Cria o item da venda conforme schema do banco
            # Tabela: itens_vendas
            # Campos: id (auto), quantidade, subtotal, preco_unitario, id_vendas, id_produto
            item_venda = {
                'id_vendas': venda_id,  # Nome correto conforme schema
                'id_produto': produto_id,
                'quantidade': quantidade_vendida,
                'preco_unitario': preco_venda,
                'subtotal': float(preco_venda * quantidade_vendida)
            }
            itens_venda.append(item_venda)
            
            # Atualiza o estoque do produto
            nova_quantidade = estoque_atual - quantidade_vendida
            (
                supabase_client()
                .table("produtos")
                .update({"quantidade": nova_quantidade})
                .eq("id", produto_id)
                .execute()
            )
        
        # Insere todos os itens da venda
        # Tabela: itens_vendas (não itens_venda)
        if itens_venda:
            (
                supabase_client()
                .table("itens_vendas")
                .insert(itens_venda)
                .execute()
            )
        
        # Limpa cache do dashboard após nova venda
        try:
            from src.features.dashboard.dashboard_service import clear_dashboard_cache
            clear_dashboard_cache()
        except:
            pass  # Não falha se não conseguir limpar cache
        
        return {
            "success": True,
            "message": "Venda finalizada com sucesso",
            "venda_id": venda_id
        }
        
    except Exception as e:
        return {"success": False, "error": f"Erro ao salvar venda: {str(e)}"}


def list_vendas(limit=100, offset=0):
    """
    Lista vendas da tabela vendas
    Otimizado com paginação
    
    Args:
        limit: Número máximo de vendas a retornar (padrão: 100)
        offset: Número de registros a pular (padrão: 0)
    
    Returns:
        {
            'success': bool,
            'data': list de listas com dados das vendas (se success=True),
            'error': str (se success=False),
            'total': int (total de vendas, se disponível)
        }
    """
    try:
        response = (
            supabase_client()
            .table("vendas")
            .select("*", count="exact")
            .order("data_venda", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        vendas_data = []
        for venda in response.data:
            # Formata a data
            data_venda = venda.get('data_venda', '')
            if data_venda:
                try:
                    from datetime import datetime
                    if isinstance(data_venda, str):
                        # Tenta parsear ISO format
                        dt = datetime.fromisoformat(data_venda.replace('Z', '+00:00'))
                        data_venda = dt.strftime('%d/%m/%Y %H:%M')
                except:
                    pass
            
            # Formata o valor
            valor_venda = venda.get('valor_venda', 0)
            valor_str = f"R$ {float(valor_venda):.2f}".replace('.', ',') if valor_venda else 'R$ 0,00'
            
            # Formata método de pagamento
            metodo_pagamento = venda.get('metodo_pagamento', '')
            metodo_str = metodo_pagamento.capitalize() if metodo_pagamento else '-'
            
            # O primeiro elemento é o ID - será usado nas ações mas não exibido na tabela
            vendas_data.append([
                venda.get('id', ''),  # ID - não será exibido
                data_venda,
                valor_str,
                metodo_str
            ])

        # Retorna dados com total (se disponível)
        result = {"success": True, "data": vendas_data}
        if hasattr(response, 'count') and response.count is not None:
            result['total'] = response.count
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_venda_by_id(venda_id: str):
    """
    Busca uma venda pelo ID com seus itens
    
    Args:
        venda_id: ID da venda
        
    Returns:
        {
            'success': bool,
            'data': dict com dados da venda e itens (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        # Busca a venda
        venda_response = (
            supabase_client()
            .table("vendas")
            .select("*")
            .eq("id", venda_id)
            .execute()
        )
        
        if not venda_response.data or len(venda_response.data) == 0:
            return {
                "success": False,
                "error": "Venda não encontrada"
            }
        
        venda = venda_response.data[0]
        
        # Formata a data
        data_venda = venda.get('data_venda', '')
        if data_venda:
            try:
                from datetime import datetime
                if isinstance(data_venda, str):
                    dt = datetime.fromisoformat(data_venda.replace('Z', '+00:00'))
                    data_venda = dt.strftime('%d/%m/%Y %H:%M')
            except:
                pass
        
        # Busca os itens da venda com informações do produto
        itens_response = (
            supabase_client()
            .table("itens_vendas")
            .select("*, produtos(nome, uni_medida)")
            .eq("id_vendas", venda_id)
            .execute()
        )
        
        itens = []
        for item in itens_response.data:
            produto = item.get('produtos', {})
            produto_nome = produto.get('nome', '') if isinstance(produto, dict) else ''
            uni_medida = produto.get('uni_medida', '') if isinstance(produto, dict) else ''
            
            itens.append({
                'id': item.get('id'),
                'produto_nome': produto_nome,
                'quantidade': float(item.get('quantidade', 0)),
                'uni_medida': uni_medida,
                'preco_unitario': float(item.get('preco_unitario', 0)),
                'subtotal': float(item.get('subtotal', 0))
            })
        
        return {
            "success": True,
            "data": {
                'id': venda.get('id'),
                'data_venda': data_venda,
                'valor_venda': float(venda.get('valor_venda', 0)),
                'metodo_pagamento': venda.get('metodo_pagamento', ''),
                'itens': itens
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}