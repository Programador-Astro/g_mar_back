from . import logistica_bp
from flask import request, jsonify, render_template, url_for
from flask_login import current_user, login_required
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jti, get_jwt
from app.models import *
from app import db
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')

@logistica_bp.route('/', methods=['GET'])
def root():
    return f'{current_user.id}'


@logistica_bp.route('/veiculos', methods=['GET', 'POST'])
@jwt_required()
def veiculos():

    if request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('placa') or not data.get('modelo'):
            return jsonify({"msg": "Dados inválidos"}), 400
        
        new_veiculo = Veiculos(
            placa=data['placa'],
            modelo=data['modelo'],
            ano=data['ano'],
            capacidade=int(data['capacidade']),
            km_atual=int(data['km_atual']),
            autor=int(current_user.id) 
            )
        
        db.session.add(new_veiculo)
        db.session.commit()
        return jsonify({"msg": "Veículo adicionado com sucesso"}), 201
    
    # Se for um GET, retorna a lista de veículos
    veiculos = Veiculos.query.all()
    veiculos_list = []
    for veiculo in veiculos:
        veiculos_list.append(veiculo.placa)
    """ for veiculo in veiculos:
            veiculos_list.append({
                'id': veiculo.id,
                'placa': veiculo.placa,
                'modelo': veiculo.modelo,
                'ano': veiculo.ano,
                'status': veiculo.status,
                'capacidade': veiculo.capacidade,
                'km_atual': veiculo.km_atual

            })"""
    return jsonify(veiculos_list), 200


@logistica_bp.route('/checklist/<placa>', methods=['GET', 'POST'])
@jwt_required()
def checklist(placa):

    if request.method == 'POST':


        veiculo = Veiculos.query.filter_by(placa=placa).first()
        if veiculo:
            # 1. Criando a instância do Checklist, mas sem os caminhos das fotos ainda (Vou fazer isso iterando e verificando)

            new_checklist = Checklist(
                placa=veiculo.placa, # Use o ID do veículo, não a placa. A sua tabela Checklist usa 'veiculo_id'
                km=int(request.form.get('km')),
                temperatura=float(request.form.get('temperatura')),
                combustivel=float(request.form.get('combustivel')),
                autor=int(1)  # Use o ID do usuário autenticado,
                
            )

            db.session.add(new_checklist)
            db.session.flush()

            placa = veiculo.placa
            fotos_salvas = {}
            # 2. Iterando sobre os arquivos enviados e salvando-os
            for campo in ["fotoFrontal", "fotoTraseira", "fotoLateral1", "fotoLateral2"]:
                arquivo = request.files.get(campo)
                if arquivo and arquivo.filename:
                    ext = os.path.splitext(secure_filename(arquivo.filename))[1]
                    filename = f"{new_checklist.id}_{placa}_{campo}{ext}"
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    arquivo.save(filepath)
                    
                    # 3. Atualizando o objeto new_checklist com os caminhos dos arquivos
                    #    Mapeando os campos
                    if campo == "fotoFrontal":
                        new_checklist.src_ft_frontal = filepath
                    elif campo == "fotoTraseira":
                        new_checklist.src_ft_traseira = filepath
                    elif campo == "fotoLateral1":
                        new_checklist.src_ft_lateral1 = filepath
                    elif campo == "fotoLateral2":
                        new_checklist.src_ft_lateral2 = filepath

            # 4. Finalizar e Salvar
            db.session.commit()

            return jsonify({"msg": "Checklist adicionado com sucesso"}), 201
            

    # Se for um GET, retorna a lista de checklists
    checklists = Checklist.query.all()
    checklist_list = []
    for checklist in checklists:
        if checklist.placa == placa:
            checklist_list.append({
                'id': checklist.id,
                'placa': checklist.placa,
                'km': checklist.km,
                'temperatura': checklist.temperatura,
                'combustivel': checklist.combustivel,
                'data': checklist.data.strftime('%d-%m-%y %H:%M:%S'),
                'autor': Usuario.query.get(checklist.autor).perfil.nome
            })
    return jsonify(checklist_list), 200


@logistica_bp.route("/get_img/<int:id>")
def get_img(id):
    checklist = Checklist.query.filter_by(id=id).first()

    if not checklist:
        return jsonify({"msg": "Checklist not found"}), 404

    fotos = []
    for coluna, valor in checklist.__dict__.items():
        if coluna.startswith('src_ft_') and valor:
            # Pega o nome do arquivo (ex.: 12_SYA1I92_fotoFrontal.png)
            filename = os.path.basename(valor)
            # Monta a URL usando Flask (pasta static/uploads)
            file_url = url_for('static', filename=f'uploads/{filename}', _external=False)
            fotos.append({
                "nome": coluna.replace("src_ft_", ""),
                "url": file_url
            })

    return jsonify({
        "id": checklist.id,
        "data": checklist.data.strftime("%Y-%m-%d") if checklist.data else None,
        "km": checklist.km,
        "temperatura": checklist.temperatura,
        "combustivel": checklist.combustivel,
        "fotos": fotos
    }), 200