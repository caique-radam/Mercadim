"""
Blueprint de Profile
Rotas para gerenciamento de perfil do usuário
"""
from flask import Blueprint, render_template, redirect, url_for, session
from src.features.auth.auth_decorators import login_required

profile_bp = Blueprint("profile", __name__, url_prefix="/profile", template_folder="templates")


@profile_bp.route("/")
@login_required
def profile_view():
    """
    Página de perfil do usuário
    Permite visualizar e editar dados do perfil
    """
    # Dados do usuário já estão na sessão
    user = session.get('user', {})
    return render_template('profile/profile.html', user=user)
