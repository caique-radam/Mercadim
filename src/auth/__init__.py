from flask import Blueprint, render_template, redirect

auth_bp = Blueprint("auth", __name__, template_folder="templates", url_prefix="/auth")

# LOGIN
# RECUPERAR SENHA
# ROTA PROTEGIDA

@auth_bp.route("/login")
def login():
    return "LOGIN"

@auth_bp.route("/forgot-password")
def forgot_password():
    return "FORGOT PASSWORD"