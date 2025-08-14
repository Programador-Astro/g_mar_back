
from .auth import auth_bp
from .logistica import logistica_bp
def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(logistica_bp, url_prefix='/logistica')