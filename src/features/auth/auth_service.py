"""
Serviço de Autenticação
Centraliza toda a lógica de autenticação com Supabase

DECISÃO: Criar uma camada de serviço para:
1. Padronizar o tratamento de erros
2. Abstrair a API do Supabase (que retorna objetos, não dicts)
3. Facilitar testes e manutenção
4. Garantir consistência em todas as operações de auth
"""
from typing import Dict, Optional, Any
from src.core.database import supabase_client


def login(email: str, password: str) -> Dict[str, Any]:
    """
    Realiza login do usuário no Supabase
    
    DECISÃO: Sempre retornar dict padronizado {'success': bool, 'data': ..., 'error': ...}
    Isso facilita tratamento uniforme nas rotas
    
    Args:
        email: Email do usuário
        password: Senha do usuário
        
    Returns:
        {
            'success': bool,
            'data': AuthResponse (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        # O Supabase retorna um objeto AuthResponse, não um dict
        # Precisamos acessar .user e .session como atributos
        response = supabase_client().auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        # Verifica se a resposta tem os dados necessários
        if response.user and response.session:
            return {
                'success': True,
                'data': response
            }
        else:
            return {
                'success': False,
                'error': 'Resposta inválida do servidor de autenticação'
            }
            
    except Exception as e:
        # Captura qualquer exceção do Supabase
        error_message = str(e)
        
        # Mensagens específicas do Supabase
        if 'Invalid login credentials' in error_message or 'Invalid credentials' in error_message:
            return {
                'success': False,
                'error': 'Email ou senha incorretos'
            }
        elif 'Email not confirmed' in error_message:
            return {
                'success': False,
                'error': 'Email não confirmado. Verifique sua caixa de entrada.'
            }
        else:
            return {
                'success': False,
                'error': f'Erro ao fazer login: {error_message}'
            }


def get_user(access_token: str) -> Dict[str, Any]:
    """
    Obtém informações do usuário usando o token de acesso
    
    DECISÃO: Validar token antes de usar em rotas protegidas
    Isso evita que tokens expirados sejam aceitos
    
    Args:
        access_token: Token de acesso do usuário
        
    Returns:
        {
            'success': bool,
            'data': User (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        # O Supabase retorna um objeto UserResponse
        response = supabase_client().auth.get_user(access_token)
        
        if response.user:
            return {
                'success': True,
                'data': response.user
            }
        else:
            return {
                'success': False,
                'error': 'Token inválido ou usuário não encontrado'
            }
            
    except Exception as e:
        error_message = str(e)
        if 'JWT' in error_message or 'expired' in error_message.lower() or 'invalid' in error_message.lower():
            return {
                'success': False,
                'error': 'Token expirado ou inválido'
            }
        else:
            return {
                'success': False,
                'error': f'Erro ao validar token: {error_message}'
            }


def sign_out(access_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Realiza logout do usuário
    
    DECISÃO: Tornar access_token opcional porque pode já estar expirado
    Mesmo assim, tentamos fazer logout no Supabase se possível
    
    Args:
        access_token: Token de acesso (opcional)
        
    Returns:
        {
            'success': bool,
            'error': str (se success=False)
        }
    """
    try:
        if access_token:
            # Tenta fazer logout no Supabase
            supabase_client().auth.sign_out()
        
        # Sempre retorna sucesso, mesmo se o token estiver inválido
        # porque já limpamos a sessão local
        return {
            'success': True
        }
        
    except Exception as e:
        # Se der erro, ainda retornamos sucesso porque limpamos a sessão local
        # O importante é que o usuário não tenha mais acesso
        return {
            'success': True,
            'error': f'Aviso: Erro ao fazer logout remoto: {str(e)}'
        }


def reset_password_email(email: str, redirect_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Envia email para redefinição de senha
    
    DECISÃO: Sempre retornar sucesso por segurança (não revelar se email existe)
    Isso evita enumeração de emails cadastrados
    
    Args:
        email: Email do usuário
        redirect_url: URL para redirecionamento após reset (opcional)
        
    Returns:
        {
            'success': bool,
            'error': str (se success=False)
        }
    """
    try:
        # DECISÃO: O método reset_password_for_email do Supabase aceita:
        # - email (string obrigatório)
        # - opções como segundo parâmetro (dict opcional)
        # Se não houver redirect_url, passamos apenas o email
        if redirect_url:
            supabase_client().auth.reset_password_for_email(email, {
                'redirect_to': redirect_url
            })
        else:
            supabase_client().auth.reset_password_for_email(email)
        
        # Sempre retorna sucesso por segurança
        return {
            'success': True
        }
        
    except Exception as e:
        # Mesmo em erro, retornamos sucesso para não revelar se email existe
        return {
            'success': True,
            'error': f'Aviso: {str(e)}'
        }


def update_password(new_password: str, access_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Atualiza a senha do usuário
    
    DECISÃO: O Supabase gerencia tokens de reset automaticamente
    Quando o usuário clica no link do email, o Supabase cria uma sessão temporária
    O método update_user funciona com a sessão atual do cliente
    
    Args:
        new_password: Nova senha
        access_token: Token de acesso (opcional, geralmente não necessário)
                     O Supabase gerencia isso através do link do email
        
    Returns:
        {
            'success': bool,
            'data': UpdatedUser (se success=True),
            'error': str (se success=False)
        }
    """
    try:
        # DECISÃO: O Supabase gerencia o token de reset automaticamente
        # Quando o usuário clica no link do email, o Supabase adiciona os tokens
        # na URL e cria uma sessão temporária. O método update_user usa essa sessão.
        # Não precisamos passar o token explicitamente na maioria dos casos.
        response = supabase_client().auth.update_user({
            'password': new_password
        })
        
        if response.user:
            return {
                'success': True,
                'data': response.user
            }
        else:
            return {
                'success': False,
                'error': 'Erro ao atualizar senha'
            }
            
    except Exception as e:
        error_message = str(e)
        if 'password' in error_message.lower() and 'weak' in error_message.lower():
            return {
                'success': False,
                'error': 'Senha muito fraca. Use pelo menos 8 caracteres com maiúsculas, minúsculas e números.'
            }
        else:
            return {
                'success': False,
                'error': f'Erro ao atualizar senha: {error_message}'
            }


def refresh_session(refresh_token: str) -> Dict[str, Any]:
    """
    Renova a sessão usando refresh token
    
    DECISÃO: Retornar dados formatados para facilitar atualização da sessão
    
    Args:
        refresh_token: Token de refresh
        
    Returns:
        {
            'success': bool,
            'data': {
                'access_token': str,
                'refresh_token': str,
                'user': User
            },
            'error': str (se success=False)
        }
    """
    try:
        # O Supabase retorna um objeto SessionResponse
        response = supabase_client().auth.refresh_session(refresh_token)
        
        if response.session and response.user:
            return {
                'success': True,
                'data': {
                    'access_token': response.session.access_token,
                    'refresh_token': response.session.refresh_token,
                    'user': response.user
                }
            }
        else:
            return {
                'success': False,
                'error': 'Resposta inválida ao renovar sessão'
            }
            
    except Exception as e:
        error_message = str(e)
        if 'expired' in error_message.lower() or 'invalid' in error_message.lower():
            return {
                'success': False,
                'error': 'Refresh token expirado ou inválido'
            }
        else:
            return {
                'success': False,
                'error': f'Erro ao renovar sessão: {error_message}'
            }

