from flask import Flask
from flask_session import Session

from src.auth import auth_bp
from src.profile import profile_bp
from config import Config
from src.supabase import init_supabase
import os
from flask import render_template

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates')
)

# Aplicar Config
app.config.from_mapping(Config)

# Inicializa sessão
Session(app)

# Inicializar Supabase
init_supabase(app)

# Registra as rotas do app
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)

@app.route('/')
def index():
    """Redireciona para login ou dashboard dependendo do estado de autenticação"""
    from flask import session
    from flask import redirect, url_for
    if 'user' in session:
        return render_template('dashboard.html', user=session['user']), 200
    return redirect(url_for('auth.login'))

# Tratamento de erros
@app.errorhandler(404)
def not_found(error):
    return "Página não encontrada", 404

@app.errorhandler(500)
def internal_error(error):
    return "Erro interno do servidor", 500

if __name__ == '__main__':
    app.run(debug=True)