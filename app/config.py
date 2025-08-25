from dotenv import load_dotenv
import os
from datetime import timedelta
load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret')
    CORS_HEADERS = 'Content-Type'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    MAIL_SERVER = os.getenv('ENVIO_EMAIL_SERVER')
    MAIL_PORT = int(os.getenv('ENVIO_EMAIL_PORTA', 587))
    MAIL_USERNAME = os.getenv('ENVIO_EMAIL_EMAIL')
    MAIL_PASSWORD = os.getenv('ENVIO_EMAIL_SENHA')
    MAIL_USE_TLS = os.getenv('ENVIO_EMAIL_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USE_SSL = os.getenv('ENVIO_EMAIL_SSL', 'False').lower() in ['true', '1', 'yes']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


# Função para escolher a configuração correta
def get_config():
    env = os.getenv('FLASK_ENV', 'development').lower()
    if env == 'production':
        return ProductionConfig
    else:
        return DevelopmentConfig
