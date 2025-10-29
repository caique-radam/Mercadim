from flask import Blueprint, render_template, redirect

auth_bp = Blueprint("auth", __name__, template_folder="templates")

# LOGIN
# RECUPERAR SENHA
# ROTA PROTEGIDA

@auth_bp.route("/login")
def login():
    return render_template('login-form.html')

@auth_bp.route("/forgot-password")
def forgot_password():
    return "FORGOT PASSWORD"