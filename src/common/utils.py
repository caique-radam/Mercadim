"""
Módulo Utils - Funções utilitárias

Contém funções auxiliares reutilizáveis em toda a aplicação.
"""
import re

def is_valid_email(email):
    """
    Valida formato de email usando regex.
    
    Args:
        email: String com o email a ser validado
        
    Returns:
        True se o email é válido, False caso contrário
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    """
    Valida força da senha.
    
    Requisitos:
    - Mínimo 8 caracteres
    - Pelo menos 1 letra maiúscula
    - Pelo menos 1 letra minúscula
    - Pelo menos 1 número
    
    Args:
        password: String com a senha a ser validada
        
    Returns:
        True se a senha atende aos requisitos, False caso contrário
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

