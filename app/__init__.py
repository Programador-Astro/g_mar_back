from flask import Flask
from .extensions import db, cors, mail, migrate, jwt, login_manager
from .config import get_config
from .blueprints import register_blueprints
from .models import *

def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=["http://localhost:5173", "https://gestor-docker-1.onrender.com/"], supports_credentials=True)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        # O user_id é uma string. É uma boa prática converter para o tipo correto.
        # No seu caso, o ID é um Integer.
        try:
            user = Usuario.query.get(int(user_id))
            return user
        except (ValueError, TypeError):
            return None



    register_blueprints(app)

    with app.app_context():
        db.create_all()
    return app