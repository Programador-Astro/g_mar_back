from . import auth_bp
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, jsonify
from flask_login import login_user, logout_user, current_user
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt, get_jti
from app import db
from app.utils import gerar_token, decodificar_token
from app.models import *


@auth_bp.route('/', methods=['POST'])
def root():
    data = request.get_json()
    usuario  = Usuario.query.filter_by(email= data['email']).first()
    if not usuario:
        return 'USER NOT FOUND', 404
    if not check_password_hash(usuario.pwd, data['pwd']):
        return 'INVALID PASSWORD', 401
    access_token = create_access_token(identity=data['email'])
    usuario.jwt = access_token
    usuario.jwt_iat = get_jti(access_token)
   
    db.session.add(usuario)
    login_user(usuario)
    db.session.commit()
    
    return jsonify(access_token=access_token, current=current_user.id)



@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    current_user = get_jwt_identity()
    print(current_user,'===============================')
    user = Usuario.query.filter_by(email=current_user).first()
    if user:
        if user.jwt == None:
            return jsonify({"msg": "Usuário já está deslogado"}), 400
        user.jwt = None
        user.jwt_iat = None 
        db.session.commit()

        return jsonify({"msg": "Logout bem-sucedido"}), 200
    else:
        return jsonify({"msg": "Usuário não encontrado"}), 404
    

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()   
    if not data or not data.get('email') or not data.get('pwd'):
        return jsonify({"msg": "Dados inválidos"}), 400
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Usuário já existe"}), 400
    hashed_password = generate_password_hash(data['pwd'])
    new_perfil = Perfil(nome=data['nome'], sobrenome=data['sobrenome'], tell=data['tell'], cargo=data['cargo'], setor=data['setor'], cnh=data['cnh'])
    db.session.add(new_perfil)
    db.session.flush()

    new_user = Usuario(email=data['email'], pwd=hashed_password, perfil_id=new_perfil.id, autor=1)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "Usuário registrado com sucesso"}), 201