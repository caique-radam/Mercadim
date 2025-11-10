from flask import Flask
from flask_session import Session

from src.features.auth import auth_bp
from src.features.profile import profile_bp
from src.features.user import user_bp
from src.features.fornecedores import fornecedores_bp
from src.features.produtos import produtos_bp
from src.features.venda import venda_bp
from src.features.dashboard import dashboard_bp
from config import Config
from src.core import init_supabase
from src.common.interface import get_interface_context
from src.common.template_utils import (
    format_currency, format_number, format_date, format_quantity,
    calcular_total_itens, get_produto_by_id
)
import os

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
app.register_blueprint(user_bp)
app.register_blueprint(fornecedores_bp)
app.register_blueprint(produtos_bp)
app.register_blueprint(venda_bp)
app.register_blueprint(dashboard_bp)

# ============================================
# REGISTRO DE FILTROS CUSTOMIZADOS
# ============================================
# Filtros podem ser usados nos templates com: {{ valor|format_currency }}
app.jinja_env.filters['format_currency'] = format_currency
app.jinja_env.filters['format_number'] = format_number
app.jinja_env.filters['format_date'] = format_date
app.jinja_env.filters['format_quantity'] = format_quantity

# ============================================
# CONTEXT PROCESSOR - Injeta contexto em todos os templates
# ============================================
@app.context_processor
def inject_interface_context():
    """Injeta variáveis de contexto da interface em todos os templates"""
    context = get_interface_context()
    
    # Adiciona funções auxiliares ao contexto
    # Essas funções podem ser chamadas diretamente nos templates
    context.update({
        'calcular_total_itens': calcular_total_itens,
        'get_produto_by_id': get_produto_by_id,
    })
    
    return context

@app.route('/')
def index():
    """Redireciona para login ou dashboard dependendo do estado de autenticação"""
    from flask import session, redirect, url_for
    if 'user' in session:
        return redirect(url_for('dashboard.dashboard_view'))
    return redirect(url_for('auth.login'))

# Tratamento de erros
@app.errorhandler(404)
def not_found(error):
    return "Página não encontrada", 404

@app.errorhandler(500)
def internal_error(error):
    return "Erro interno do servidor", 500

if __name__ == '__main__':
    # Configuração para Railway e outros ambientes de produção
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development').lower() != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)