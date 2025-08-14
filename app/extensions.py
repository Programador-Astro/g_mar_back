from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_login import LoginManager

login_manager = LoginManager()
jwt = JWTManager()
db = SQLAlchemy()
cors = CORS()
migrate = Migrate()
mail = Mail()