from flask_login import UserMixin
from app import db


class Usuario(db.Model, UserMixin):

    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key = True, autoincrement=True) 
    email = db.Column('email', db.VARCHAR(100), unique=True)
    pwd = db.Column('pwd', db.VARCHAR(188))

    jwt = db.Column(db.String(500), nullable=True, unique=True)
    jwt_iat = db.Column(db.String(50), nullable=True, unique=True)

    flag_confirm_email = db.Column(db.Boolean, default=False)
    status = db.Column(db.Boolean, default=True)
    perfil_id = db.Column(db.Integer, db.ForeignKey('perfil.id'), nullable=False)

    #Autor é a pessoa que criou esté usuario
    autor = db.Column('autor',db.Integer, nullable=False)

    
class Perfil(db.Model):
    __tablename__ = 'perfil'

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome        = db.Column('nome', db.VARCHAR(15), nullable=False)
    sobrenome   = db.Column('sobrenome', db.VARCHAR(100), nullable=False)
    tell        = db.Column('tell', db.VARCHAR(20), unique=True)
    setor       = db.Column('setor', db.VARCHAR(50))
    cargo       = db.Column('cargo', db.VARCHAR(50))
    cnh         = db.Column('cnh', db.VARCHAR(20), unique=True, nullable=True) 
    usuarios = db.relationship('Usuario', backref='perfil', lazy=True)
   