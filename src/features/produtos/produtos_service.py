from src.core.database import supabase_client


def prepare_data(produto_data: dict, is_update=False):
    """
    Prepara os dados do produto para inserção ou atualização no banco.
    
    Args:
        produto_data: Dicionário com dados do formulário
        is_update: Se True, permite campos vazios serem None (para update)
    
    Returns:
        Dicionário com dados prontos para o banco
    """
    prepared = {}
    
    # Campo obrigatório: nome
    nome = produto_data.get('nome', '').strip() if produto_data.get('nome') else ''
    if nome:
        prepared['nome'] = nome
    
    # Campos numéricos
    numeric_fields = {
        'preco_custo': None,
        'preco_venda': 255,  # Valor padrão
        'quantidade': None,
        'codigo_barra': None
    }
    
    for field, default_value in numeric_fields.items():
        if field in produto_data and produto_data.get(field) is not None:
            value = produto_data.get(field, '').strip()
            if value:
                try:
                    prepared[field] = float(value)
                except (ValueError, TypeError):
                    pass
            elif is_update and field in produto_data:
                # Em update, se campo foi enviado vazio, pode ser None
                prepared[field] = None
        elif not is_update and default_value is not None:
            # Na criação, aplica valor padrão se não foi fornecido
            prepared[field] = default_value
    
    # Campo inteiro: id_fornecedor
    if 'id_fornecedor' in produto_data:
        fornecedor_id = produto_data.get('id_fornecedor', '').strip()
        if fornecedor_id:
            try:
                prepared['id_fornecedor'] = int(fornecedor_id)
            except (ValueError, TypeError):
                pass
        elif is_update:
            # Em update, se foi enviado vazio, remove o fornecedor
            prepared['id_fornecedor'] = None
    
    # Campos de texto
    text_fields = ['validade_lote', 'uni_medida']
    for field in text_fields:
        if field in produto_data:
            value = produto_data.get(field, '').strip() if produto_data.get(field) else ''
            if value:
                prepared[field] = value
            elif is_update:
                # Em update, permite None
                prepared[field] = None
    
    # Remove campos vazios (exceto valores numéricos que podem ser 0)
    numeric_field_names = ['preco_custo', 'preco_venda', 'quantidade', 'codigo_barra', 'id_fornecedor']
    prepared = {k: v for k, v in prepared.items() if v != '' or k in numeric_field_names}
    
    return prepared


def list_produtos(limit=100, offset=0):
    """
    Lista produtos da tabela produtos com informações do fornecedor
    Otimizado com paginação
    
    Args:
        limit: Número máximo de produtos a retornar (padrão: 100)
        offset: Número de registros a pular (padrão: 0)
    
    Returns:
        {
            'success': bool,
            'data': list de listas com dados dos produtos (se success=True),
            'error': str (se success=False),
            'total': int (total de produtos, se disponível)
        }
    """
    try:
        # Busca produtos com join no fornecedor, com limite e offset
        response = (
            supabase_client()
            .table("produtos")
            .select("*, fornecedores(nome_fantasia)", count="exact")
            .order("id", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        produtos_data = []
        for produto in response.data:
            # Extrai nome do fornecedor
            fornecedor = produto.get('fornecedores', {})
            fornecedor_nome = fornecedor.get('nome_fantasia', '') if isinstance(fornecedor, dict) else ''
            
            # Formatação de preços
            preco_custo = produto.get('preco_custo')
            preco_custo_str = f"R$ {float(preco_custo):.2f}".replace('.', ',') if preco_custo is not None else 'R$ 0,00'
            
            preco_venda = produto.get('preco_venda')
            preco_venda_str = f"R$ {float(preco_venda):.2f}".replace('.', ',') if preco_venda is not None else 'R$ 0,00'
            
            # Formatação de quantidade
            quantidade = produto.get('quantidade')
            uni_medida = produto.get('uni_medida', '')
            quantidade_str = f"{float(quantidade):.2f} {uni_medida}".replace('.', ',') if quantidade is not None else f"0 {uni_medida}"
            
            # Validade
            validade = produto.get('validade_lote', '') or ''
            if validade:
                try:
                    from datetime import datetime
                    if isinstance(validade, str):
                        validade = datetime.strptime(validade, '%Y-%m-%d').strftime('%d/%m/%Y')
                except:
                    pass
            
            # Código de barras
            codigo_barra = produto.get('codigo_barra', '') or ''
            codigo_barra_str = str(int(codigo_barra)) if codigo_barra else ''
            
            produtos_data.append([
                produto.get('id', ''),  # ID - não será exibido
                produto.get('nome', ''),
                preco_custo_str,
                preco_venda_str,
                quantidade_str,
                validade,
                codigo_barra_str,
                fornecedor_nome
            ])

        # Retorna dados com total (se disponível)
        result = {"success": True, "data": produtos_data}
        if hasattr(response, 'count') and response.count is not None:
            result['total'] = response.count
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_produto_by_id(produto_id: str):
    """
    Busca um produto pelo ID
    
    Args:
        produto_id: ID do produto (bigint)
        
    Returns:
        {
            'success': bool,
            'data': dict com dados do produto (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        response = (
            supabase_client()
            .table("produtos")
            .select("*, fornecedores(nome_fantasia)")
            .eq("id", produto_id)
            .execute()
        )
        
        if response.data and len(response.data) > 0:
            return {
                "success": True,
                "data": response.data[0]
            }
        else:
            return {
                "success": False,
                "error": "Produto não encontrado"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_fornecedores_for_select():
    """
    Busca lista de fornecedores para usar em selects/dropdowns
    
    Returns:
        {
            'success': bool,
            'data': list de dicts com id e nome_fantasia (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        response = (
            supabase_client()
            .table("fornecedores")
            .select("id, nome_fantasia")
            .eq("status", True)  # Apenas fornecedores ativos
            .execute()
        )
        
        fornecedores = []
        for fornecedor in response.data:
            fornecedores.append({
                'id': fornecedor.get('id'),
                'nome': fornecedor.get('nome_fantasia', '')
            })
        
        return {"success": True, "data": fornecedores}
    except Exception as e:
        return {"success": False, "error": str(e), "data": []}


def create_produto(produto_data: dict):
    """
    Cria um novo produto na tabela produtos
    
    Args:
        produto_data: Dicionário com os dados do produto
        
    Returns:
        {
            'success': bool,
            'data': dict com dados do produto criado (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        # Validação básica
        if not produto_data.get('nome', '').strip():
            return {
                "success": False,
                "error": "Nome do produto é obrigatório"
            }
        
        # Prepara os dados
        insert_data = prepare_data(produto_data, is_update=False)
        
        # Insere o produto
        response = (
            supabase_client()
            .table("produtos")
            .insert(insert_data)
            .execute()
        )
        
        if response.data and len(response.data) > 0:
            return {
                "success": True,
                "data": response.data[0],
                "message": "Produto criado com sucesso"
            }
        else:
            return {
                "success": False,
                "error": "Erro ao criar produto"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_produto(produto_id: str, produto_data: dict):
    """
    Atualiza um produto existente
    
    Args:
        produto_id: ID do produto (bigint)
        produto_data: Dicionário com os dados a serem atualizados
        
    Returns:
        {
            'success': bool,
            'data': dict com dados do produto atualizado (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        # Prepara os dados
        update_data = prepare_data(produto_data, is_update=True)
        
        if not update_data:
            return {
                "success": False,
                "error": "Nenhum dado para atualizar"
            }
        
        # Atualiza o produto
        response = (
            supabase_client()
            .table("produtos")
            .update(update_data)
            .eq("id", produto_id)
            .execute()
        )
        
        if response.data and len(response.data) > 0:
            return {
                "success": True,
                "data": response.data[0],
                "message": "Produto atualizado com sucesso"
            }
        else:
            return {
                "success": False,
                "error": "Produto não encontrado"
            }
                
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_produto(produto_id: str):
    """
    Deleta um produto
    
    Args:
        produto_id: ID do produto (bigint)
        
    Returns:
        {
            'success': bool,
            'message': str (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        response = (
            supabase_client()
            .table("produtos")
            .delete()
            .eq("id", produto_id)
            .execute()
        )
        
        # Verifica se deletou algo
        if response.data and len(response.data) > 0:
            return {
                "success": True,
                "message": "Produto deletado com sucesso"
            }
        else:
            # Verifica se ainda existe
            check = (
                supabase_client()
                .table("produtos")
                .select("id")
                .eq("id", produto_id)
                .execute()
            )
            
            if check.data and len(check.data) > 0:
                return {
                    "success": False,
                    "error": "Produto não foi deletado (pode ter restrições)"
                }
            else:
                return {
                    "success": True,
                    "message": "Produto deletado com sucesso"
                }
                    
    except Exception as e:
        return {"success": False, "error": f"Erro ao deletar produto: {str(e)}"}
