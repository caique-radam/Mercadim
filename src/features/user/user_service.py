import time
from src.core.database import supabase_client

def list_users():
    try:
        response = (
            supabase_client()
            .table("user_full")
            .select("*")
            .execute()
        )

        users_data = []
        for user in response.data:
            # O primeiro elemento é o ID (UUID) - será usado nas ações mas não exibido na tabela
            # O template usa row[1:] para pular o ID ao exibir as células
            users_data.append([
                user.get('id', ''),  # ID (UUID) - não será exibido
                user.get('first_name', ''),
                user.get('last_name', ''),
                user.get('email', ''),
                user.get('role', ''),
                user.get('phone', '')
            ])

        return {"success": True, "data": users_data}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_user_by_id(user_id: str):
    """
    Busca um usuário pelo ID
    
    Args:
        user_id: ID do usuário (UUID)
        
    Returns:
        {
            'success': bool,
            'data': dict com dados do usuário (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        response = (
            supabase_client()
            .table("user_full")
            .select("*")
            .eq("id", user_id)
            .execute()
        )
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            return {
                "success": True,
                "data": user
            }
        else:
            return {
                "success": False,
                "error": "Usuário não encontrado"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_user(user_data: dict):
    """
    Cria um novo usuário no auth.users com raw_user_meta_data.
    A trigger do Supabase automaticamente cria o registro em public.profiles.
    
    Args:
        user_data: Dicionário com os dados do usuário
            - first_name: str
            - last_name: str
            - email: str
            - phone: str (opcional)
            - password: str
            - confirm_password: str
            
    Returns:
        {
            'success': bool,
            'data': dict com dados do usuário criado (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        client = supabase_client()
        email = user_data.get('email', '').strip()
        
        if not email:
            return {
                "success": False,
                "error": "Email é obrigatório"
            }
        
        # Validação de senha
        password = user_data.get('password', '').strip()
        confirm_password = user_data.get('confirm_password', '').strip()
        
        if not password:
            return {
                "success": False,
                "error": "Senha é obrigatória"
            }
        
        if password != confirm_password:
            return {
                "success": False,
                "error": "As senhas não correspondem"
            }
        
        # Prepara os metadados do usuário (raw_user_meta_data)
        # A trigger do Supabase usará esses dados para criar o profile
        user_metadata = {
            "first_name": user_data.get('first_name', '').strip(),
            "last_name": user_data.get('last_name', '').strip(),
        }
        
        # Remove campos vazios
        user_metadata = {k: v for k, v in user_metadata.items() if v}
        
        # Cria o usuário no auth.users com raw_user_meta_data
        # A trigger automaticamente criará o registro em public.profiles
        try:
            auth_response = client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,  # Confirma o email automaticamente
                "user_metadata": user_metadata,  # Será salvo em raw_user_meta_data
                "phone": user_data.get('phone', '') or None,
            })
            
            user_id = auth_response.user.id if auth_response.user else None
            
            if not user_id:
                return {
                    "success": False,
                    "error": "Erro ao criar usuário no sistema de autenticação"
                }
            
            # Aguarda um momento para a trigger processar
            # Em seguida, busca o profile criado pela trigger
            time.sleep(0.5)  # Pequeno delay para garantir que a trigger executou
            
            # Busca o profile criado pela trigger
            profile_response = (
                client
                .table("profiles")
                .select("*")
                .eq("id", user_id)
                .execute()
            )
            
            if profile_response.data and len(profile_response.data) > 0:
                return {
                    "success": True,
                    "data": profile_response.data[0],
                    "message": "Usuário criado com sucesso"
                }
            else:
                # Se a trigger não executou, tenta criar manualmente
                try:
                    profile_data = {
                        'id': user_id,
                        'first_name': user_data.get('first_name', '').strip(),
                        'last_name': user_data.get('last_name', '').strip(),
                    }
                    profile_data = {k: v for k, v in profile_data.items() if v}
                    
                    manual_profile = (
                        client
                        .table("profiles")
                        .insert(profile_data)
                        .execute()
                    )
                    
                    if manual_profile.data:
                        return {
                            "success": True,
                            "data": manual_profile.data[0],
                            "message": "Usuário criado com sucesso (profile criado manualmente)"
                        }
                except:
                    pass
                
                # Se falhou ao criar o profile, remove o usuário do auth
                try:
                    client.auth.admin.delete_user(user_id)
                except:
                    pass
                
                return {
                    "success": False,
                    "error": "Erro ao criar perfil do usuário. A trigger pode não estar configurada."
                }
                
        except Exception as auth_error:
            return {
                "success": False,
                "error": f"Erro ao criar usuário: {str(auth_error)}"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_user(user_id: str, user_data: dict):
    """
    Atualiza um usuário existente tanto no auth.users quanto em public.profiles
    
    Args:
        user_id: ID do usuário (UUID)
        user_data: Dicionário com os dados a serem atualizados
            - first_name: str (opcional) - vai para profiles e user_metadata
            - last_name: str (opcional) - vai para profiles e user_metadata
            - phone: str (opcional) - vai para auth.users
            - password: str (opcional) - vai para auth.users
            - confirm_password: str (opcional) - usado apenas para validação
            
    Returns:
        {
            'success': bool,
            'data': dict com dados do usuário atualizado (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        client = supabase_client()
        
        # Prepara os dados para atualização no profile (first_name, last_name)
        profile_update_data = {}
        if 'first_name' in user_data and user_data.get('first_name'):
            profile_update_data['first_name'] = user_data['first_name'].strip()
        if 'last_name' in user_data and user_data.get('last_name'):
            profile_update_data['last_name'] = user_data['last_name'].strip()
        
        # Prepara os dados para atualização no auth.users
        auth_update_payload = {}
        
        # Phone (se fornecido ou para limpar)
        if 'phone' in user_data:
            phone_value = user_data['phone'].strip() if user_data.get('phone') else None
            auth_update_payload['phone'] = phone_value
        
        # Password (se fornecido)
        if 'password' in user_data and user_data.get('password'):
            auth_update_payload['password'] = user_data['password'].strip()
        
        # Prepara user_metadata (first_name, last_name para raw_user_meta_data)
        auth_metadata = {}
        if 'first_name' in user_data and user_data.get('first_name'):
            auth_metadata['first_name'] = user_data['first_name'].strip()
        if 'last_name' in user_data and user_data.get('last_name'):
            auth_metadata['last_name'] = user_data['last_name'].strip()
        
        # Remove campos vazios, mas preserva phone se foi fornecido (mesmo que None)
        profile_update_data = {k: v for k, v in profile_update_data.items() if v}
        auth_metadata = {k: v for k, v in auth_metadata.items() if v}
        
        # Verifica se há algo para atualizar
        if not profile_update_data and not auth_update_payload and not auth_metadata:
            return {
                "success": False,
                "error": "Nenhum dado para atualizar"
            }
        
        # Atualiza o auth.users primeiro (se necessário)
        if auth_update_payload or auth_metadata:
            try:
                # Se há metadados, mescla com os existentes
                if auth_metadata:
                    current_user = client.auth.admin.get_user_by_id(user_id)
                    current_metadata = {}
                    
                    if current_user and hasattr(current_user, 'user_metadata'):
                        current_metadata = current_user.user_metadata or {}
                    
                    # Mescla os metadados existentes com os novos
                    updated_metadata = {**current_metadata, **auth_metadata}
                    auth_update_payload["user_metadata"] = updated_metadata
                
                # Atualiza o usuário no auth
                client.auth.admin.update_user_by_id(user_id, auth_update_payload)
            except Exception as auth_error:
                return {
                    "success": False,
                    "error": f"Erro ao atualizar usuário no auth: {str(auth_error)}"
                }
        
        # Atualiza o profile em public.profiles (se necessário)
        if profile_update_data:
            profile_response = (
                client
                .table("profiles")
                .update(profile_update_data)
                .eq("id", user_id)
                .execute()
            )
            
            if profile_response.data and len(profile_response.data) > 0:
                return {
                    "success": True,
                    "data": profile_response.data[0],
                    "message": "Usuário atualizado com sucesso"
                }
            else:
                return {
                    "success": False,
                    "error": "Usuário não encontrado na tabela profiles"
                }
        else:
            # Se só atualizou o auth, busca o profile
            profile_response = (
                client
                .table("profiles")
                .select("*")
                .eq("id", user_id)
                .execute()
            )
            
            if profile_response.data and len(profile_response.data) > 0:
                return {
                    "success": True,
                    "data": profile_response.data[0],
                    "message": "Usuário atualizado com sucesso"
                }
            else:
                return {
                    "success": False,
                    "error": "Usuário não encontrado"
                }
                
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_user(user_id: str):
    """
    Deleta um usuário tanto do auth.users quanto de public.profiles
    
    Args:
        user_id: ID do usuário (UUID)
        
    Returns:
        {
            'success': bool,
            'message': str (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        client = supabase_client()
        errors = []
        
        # Deleta do auth.users primeiro
        auth_deleted = False
        try:
            client.auth.admin.delete_user(user_id)
            auth_deleted = True
        except Exception as auth_error:
            # Se falhar ao deletar do auth, continua tentando deletar o profile
            # (pode ser que o usuário não exista no auth ou não tenha permissão)
            errors.append(f"Erro ao deletar do auth: {str(auth_error)}")
        
        # Deleta do public.profiles
        profile_deleted = False
        try:
            response = (
                client
                .table("profiles")
                .delete()
                .eq("id", user_id)
                .execute()
            )
            
            # Verifica se realmente deletou algo
            # O Supabase retorna os dados deletados em response.data
            if response.data and len(response.data) > 0:
                profile_deleted = True
            else:
                # Verifica se o profile ainda existe
                check_response = (
                    client
                    .table("profiles")
                    .select("id")
                    .eq("id", user_id)
                    .execute()
                )
                if check_response.data and len(check_response.data) > 0:
                    errors.append("Profile não foi deletado (pode não existir ou ter restrições)")
                else:
                    profile_deleted = True  # Não existe mais, consideramos como deletado
                    
        except Exception as profile_error:
            errors.append(f"Erro ao deletar profile: {str(profile_error)}")
        
        # Se pelo menos um foi deletado, considera sucesso parcial
        if profile_deleted or auth_deleted:
            messages = []
            if auth_deleted:
                messages.append("deletado do sistema de autenticação")
            if profile_deleted:
                messages.append("deletado do perfil")
            
            if errors:
                return {
                    "success": True,
                    "message": f"Usuário {' e '.join(messages)}, mas houve avisos: {'; '.join(errors)}"
                }
            else:
                return {
                    "success": True,
                    "message": f"Usuário deletado com sucesso ({' e '.join(messages)})"
                }
        else:
            # Nenhum foi deletado
            return {
                "success": False,
                "error": f"Erro ao deletar usuário: {'; '.join(errors) if errors else 'Nenhum registro foi deletado'}"
            }
            
    except Exception as e:
        return {"success": False, "error": f"Erro inesperado ao deletar usuário: {str(e)}"}