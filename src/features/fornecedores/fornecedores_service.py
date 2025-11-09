from src.core.database import supabase_client


def prepare_data(fornecedor_data: dict, is_update=False):
    """
    Prepara os dados do fornecedor para inserção ou atualização no banco.
    
    Args:
        fornecedor_data: Dicionário com dados do formulário
        is_update: Se True, permite campos vazios serem None (para update)
    
    Returns:
        Dicionário com dados prontos para o banco
    """
    prepared = {}
    
    # Campos de texto: remove espaços e converte vazio para None
    text_fields = ['nome_fantasia', 'email', 'telefone', 'cidade', 'estado', 'endereco', 'bairro', 'cep']
    for field in text_fields:
        if field in fornecedor_data:
            # Se o campo foi enviado no formulário, processa
            raw_value = fornecedor_data.get(field)
            if raw_value is not None:
                value = str(raw_value).strip() if raw_value else ''
                # Em update, permite None para limpar campos opcionais
                # Em create, só inclui se tiver valor
                if value:
                    prepared[field] = value
                elif is_update:
                    # Em update, campo vazio significa limpar (None)
                    prepared[field] = None
            elif is_update:
                # Se foi explicitamente None, inclui
                prepared[field] = None
        elif not is_update and field == 'nome_fantasia':
            # Na criação, nome_fantasia é obrigatório, mas já foi validado antes
            pass
    
    # Campo numérico: frete
    if 'frete' in fornecedor_data:
        frete_value = fornecedor_data.get('frete')
        if frete_value is not None and str(frete_value).strip():
            try:
                prepared['frete'] = float(str(frete_value).strip())
            except (ValueError, TypeError):
                pass  # Ignora se não for número válido
        elif is_update:
            # Em update, se foi enviado vazio, pode ser None
            prepared['frete'] = None
    
    # Campo booleano: status
    if 'status' in fornecedor_data:
        prepared['status'] = bool(fornecedor_data.get('status'))
    elif not is_update:
        # Na criação, padrão é True
        prepared['status'] = True
    
    return prepared


def list_fornecedores():
    """
    Lista todos os fornecedores da tabela fornecedores
    
    Returns:
        {
            'success': bool,
            'data': list de listas com dados dos fornecedores (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        response = (
            supabase_client()
            .table("fornecedores")
            .select("*")
            .execute()
        )

        fornecedores_data = []
        for fornecedor in response.data:
            # O primeiro elemento é o ID - será usado nas ações mas não exibido na tabela
            fornecedores_data.append([
                fornecedor.get('id', ''),  # ID - não será exibido
                fornecedor.get('nome_fantasia', ''),
                fornecedor.get('email', ''),
                fornecedor.get('telefone', ''),
                fornecedor.get('cidade', ''),
                fornecedor.get('estado', ''),
                'Ativo' if fornecedor.get('status', False) else 'Inativo'
            ])

        return {"success": True, "data": fornecedores_data}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_fornecedor_by_id(fornecedor_id: str):
    """
    Busca um fornecedor pelo ID
    
    Args:
        fornecedor_id: ID do fornecedor (bigint)
        
    Returns:
        {
            'success': bool,
            'data': dict com dados do fornecedor (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        response = (
            supabase_client()
            .table("fornecedores")
            .select("*")
            .eq("id", fornecedor_id)
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
                "error": "Fornecedor não encontrado"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_fornecedor(fornecedor_data: dict):
    """
    Cria um novo fornecedor na tabela fornecedores
    
    Args:
        fornecedor_data: Dicionário com os dados do fornecedor
        
    Returns:
        {
            'success': bool,
            'data': dict com dados do fornecedor criado (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        # Validação básica
        if not fornecedor_data.get('nome_fantasia', '').strip():
            return {
                "success": False,
                "error": "Nome fantasia é obrigatório"
            }
        
        # Prepara os dados
        insert_data = prepare_data(fornecedor_data, is_update=False)
        
        # Insere o fornecedor
        response = (
            supabase_client()
            .table("fornecedores")
            .insert(insert_data)
            .execute()
        )
        
        if response.data and len(response.data) > 0:
            return {
                "success": True,
                "data": response.data[0],
                "message": "Fornecedor criado com sucesso"
            }
        else:
            return {
                "success": False,
                "error": "Erro ao criar fornecedor"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_fornecedor(fornecedor_id: str, fornecedor_data: dict):
    """
    Atualiza um fornecedor existente
    
    Args:
        fornecedor_id: ID do fornecedor (bigint)
        fornecedor_data: Dicionário com os dados a serem atualizados
        
    Returns:
        {
            'success': bool,
            'data': dict com dados do fornecedor atualizado (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        # Prepara os dados
        update_data = prepare_data(fornecedor_data, is_update=True)
        
        if not update_data:
            return {
                "success": False,
                "error": "Nenhum dado para atualizar"
            }
        
        # Atualiza o fornecedor
        response = (
            supabase_client()
            .table("fornecedores")
            .update(update_data)
            .eq("id", fornecedor_id)
            .execute()
        )
        
        if response.data and len(response.data) > 0:
            return {
                "success": True,
                "data": response.data[0],
                "message": "Fornecedor atualizado com sucesso"
            }
        else:
            return {
                "success": False,
                "error": "Fornecedor não encontrado"
            }
                
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_fornecedor(fornecedor_id: str):
    """
    Deleta um fornecedor
    
    Args:
        fornecedor_id: ID do fornecedor (bigint)
        
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
            .table("fornecedores")
            .delete()
            .eq("id", fornecedor_id)
            .execute()
        )
        
        # Verifica se deletou algo
        if response.data and len(response.data) > 0:
            return {
                "success": True,
                "message": "Fornecedor deletado com sucesso"
            }
        else:
            # Verifica se ainda existe
            check = (
                supabase_client()
                .table("fornecedores")
                .select("id")
                .eq("id", fornecedor_id)
                .execute()
            )
            
            if check.data and len(check.data) > 0:
                return {
                    "success": False,
                    "error": "Fornecedor não foi deletado (pode ter restrições)"
                }
            else:
                return {
                    "success": True,
                    "message": "Fornecedor deletado com sucesso"
                }
                    
    except Exception as e:
        return {"success": False, "error": f"Erro ao deletar fornecedor: {str(e)}"}
