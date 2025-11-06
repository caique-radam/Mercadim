"""
Serviço de Profile
Busca dados do perfil do usuário da tabela profiles

DECISÃO: Separar lógica de profile em serviço próprio
Isso facilita manutenção e reutilização
"""
from typing import Dict, Any, Optional
from src.core.database import supabase_client


def get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Busca o profile do usuário pelo ID do auth.users
    
    DECISÃO: Retornar estrutura padronizada {'success': bool, 'data': ..., 'error': ...}
    Isso mantém consistência com outros serviços
    
    Args:
        user_id: ID do usuário (UUID da tabela auth.users)
        
    Returns:
        {
            'success': bool,
            'data': dict com dados do profile (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        # Busca o profile relacionado ao user_id
        # A trigger garante que sempre existe um profile para cada usuário
        response = supabase_client().table('profiles').select('*').eq('id', user_id).execute()
        
        # Verifica se encontrou dados
        if response.data and len(response.data) > 0:
            profile = response.data[0]  # Retorna o primeiro (e único) resultado
            
            # DECISÃO: Processar dados do profile para facilitar uso
            # Combina first_name e last_name em name completo
            first_name = profile.get('first_name', '')
            last_name = profile.get('last_name', '')
            full_name = f"{first_name} {last_name}".strip() if (first_name or last_name) else None
            
            # Adiciona campo calculado para facilitar uso nos templates
            processed_profile = {
                **profile,  # Mantém todos os campos originais
                'name': full_name,  # Nome completo calculado
                'first_name': first_name,
                'last_name': last_name,
            }
            
            return {
                'success': True,
                'data': processed_profile
            }
        else:
            # Profile não encontrado - pode acontecer se trigger não executou
            # Retorna estrutura vazia mas com sucesso para não quebrar o fluxo
            return {
                'success': True,
                'data': None,
                'warning': 'Profile não encontrado na tabela profiles'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao buscar profile: {str(e)}'
        }


# Mantém compatibilidade com código existente
def get_logged_profile(user_id: str) -> Dict[str, Any]:
    """
    Alias para get_user_profile (mantido para compatibilidade)
    """
    return get_user_profile(user_id)