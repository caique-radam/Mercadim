from flask import Flask, render_template
from src.auth import auth_bp
import os

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates')
)
# Registra as rotas do app
app.register_blueprint(auth_bp)

@app.route('/')
def home():
    return render_template('base-admin.html')

if __name__ == '__main__':
    app.run(debug=True)