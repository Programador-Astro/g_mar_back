from . import comercial_bp
from flask import request, jsonify, render_template, url_for, session
from flask_login import current_user, login_required
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jti, get_jwt
from app.models import *
from app import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from app.utils import limpar_pdf_pedido, geocodificar_google, get_agora, verifica_setor
import os


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')

@comercial_bp.route('/', methods=['GET'])
@verifica_setor('comercial')
def root():
    user = session.get('id_user')
    return f'{user} OK comercial'




@comercial_bp.route('/get_pedidos', methods=['GET'])
@jwt_required()
def get_pedidos():
    pedidos = Pedido.query.all()
    pedidos_list = []
    try:
        for pedido in pedidos:
            pedidos_list.append({
                "id": pedido.id,
                "cod_externo": pedido.cod_externo,
                "cliente_id": pedido.cliente_id,
                "status": pedido.status,
                "data_criacao": pedido.data_criacao.strftime('%d-%m-%Y %H:%M:%S'),
                "data_entrega": pedido.data_entrega.strftime('%d-%m-%Y %H:%M:%S') if pedido.data_entrega else None,
                "endereco_adm": pedido.endereco_adm.endereco if pedido.endereco_adm else None,
                "bairro":  pedido.endereco_adm.bairro if pedido.endereco_adm.bairro else None,
                "cidade":  pedido.endereco_adm.cidade if pedido.endereco_adm.cidade else None,
                "endereco_motorista": pedido.endereco_motorista.endereco if pedido.endereco_motorista else None,
                "cliente": pedido.cliente.nome if pedido.cliente else None,
                "motorista": pedido.motorista.nome if pedido.motorista else None,
                "produtos": [
                    {
                        "nome": pp.produto.nome,
                        "quantidade": pp.quantidade
                    }
                    for pp in pedido.produtos
                ]
            })
        return jsonify(pedidos_list), 200
    except Exception as e:
        print(f"Erro ao cadastrar cliente: {e}")
        return jsonify({"msg": "Erro ao buscar   os pedidos"}), 500

@comercial_bp.route('/get_pedido/<cod_externo>', methods=['GET'])
@jwt_required()
def get_pedido(cod_externo):
    try:
        pedido = Pedido.query.filter_by(cod_externo=cod_externo).first()

        if not pedido:
            return jsonify({"msg": "Pedido não encontrado"}), 404

        # Dados do pedido
        pedido_dict = pedido.to_dict()

        # Dados do cliente
        cliente_dict = pedido.cliente.to_dict() if pedido.cliente else None

        # Endereços
        endereco_adm_dict = pedido.endereco_adm.to_dict() if pedido.endereco_adm else None
        endereco_motorista_dict = pedido.endereco_motorista.to_dict() if pedido.endereco_motorista else None

        # Produtos do pedido
        produtos_list = []
        for pp in pedido.produtos:
            produto_dict = pp.produto.to_dict()
            produto_dict["quantidade"] = pp.quantidade
            produtos_list.append(produto_dict)

        response = {
            "pedido": pedido_dict,
            "cliente": cliente_dict,
            "endereco_adm": endereco_adm_dict,
            "endereco_motorista": endereco_motorista_dict,
            "produtos": produtos_list
        }

        return jsonify(response), 200

    except Exception as e:
        print("Erro ao buscar pedido:", e)
        return jsonify({"msg": "Erro ao buscar o pedido"}), 500



@comercial_bp.route('/get_clientes')
@jwt_required()
def get_clientes():
    try:
        clientes = Cliente.query.all()

        if not clientes:
            return jsonify({"msg": "Nehum cliente encontrado"}), 401

        dados = [cliente.to_dict() for cliente in clientes]

        return jsonify({"dados": dados})
    except:
        return jsonify({'msg': 'algo deu errado'}), 401

@comercial_bp.route('/get_cliente/<codigo_cliente>', methods=['GET'])
@jwt_required()
def get_cliente(codigo_cliente):
    cliente = Cliente.query.filter_by(codigo_externo=codigo_cliente).first()

    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404

    # Serializar cliente
    cliente_dict = cliente.to_dict()

    # Serializar endereços
    cliente_dict["enderecos_adm"] = [
        {
            "id": e.id,
            "endereco": e.endereco,
            "numero": e.numero,
            "latitude": e.latitude,
            "longitude": e.longitude,
            "ponto_ref": e.ponto_ref,
            "obs": e.obs,
        }
        for e in cliente.endereco_adm
    ]

    cliente_dict["enderecos_motorista"] = [
        {
            "id": e.id,
            "endereco": e.endereco,
            "numero": e.numero,
            "latitude": e.latitude,
            "longitude": e.longitude,
            "ponto_ref": e.ponto_ref,
            "obs": e.obs,
        }
        for e in cliente.endereco_motorista
    ]

    # Serializar pedidos com produtos
    cliente_dict["pedidos"] = []
    for pedido in cliente.pedidos:
        cliente_dict["pedidos"].append({
            "id": pedido.id,
            "cod_externo": pedido.cod_externo,
            "status": pedido.status,
            "data_criacao": pedido.data_criacao.strftime('%d-%m-%Y %H:%M:%S'),
            "data_entrega": pedido.data_entrega.strftime('%d-%m-%Y %H:%M:%S') if pedido.data_entrega else None,
            "produtos": [
                {
                    "nome": pp.produto.nome,
                    "quantidade": pp.quantidade
                }
                for pp in pedido.produtos
            ]
        })

    return jsonify({"dados": cliente_dict}), 200

@comercial_bp.route('/cadastrar_cliente', methods=['POST'])
@jwt_required()
def cadastrar_cliente():
    #current_user = Usuario.query.filter_by(email=get_jwt_identity()).first()
    payload  = get_jwt()
    if not payload:
        return jsonify({"msg": "Usuário não autenticado"}), 401
    file = request.files.get('arquivo')
    #file = request.files["arquivo"]
    if file:
        #try:
            #Verfica se o cliente existe cadastrando se não exitir
            dados_pedido = limpar_pdf_pedido(file)
            if not dados_pedido:
                return jsonify({"msg": "Erro ao processar os dados do pedido (169)"}), 400
           
            # Verifica se o cliente já existe
            cliente = Cliente.query.filter_by(codigo_externo=dados_pedido['cod_cliente']).first()

            if cliente:
                return jsonify({'msg': "cliente já cadastrado"})
                
            if not cliente:
                
                try:
                    cliente = Cliente(
                        codigo_externo=dados_pedido['cod_cliente'],
                        nome=dados_pedido['cliente'],
                        email=dados_pedido.get('email', None),
                        telefone_cadastro=dados_pedido.get('telefone_cadastro', None),
                        telefone_motorista=dados_pedido.get('telefone_motorista', None),


                        #current_user.id
                        usuario_id=payload['id']
                    )
                    db.session.add(cliente)
                    db.session.flush() 
                
                except Exception as e:
                    print(f"Erro ao cadastrar cliente: {e}")
                    return jsonify({"msg": "Erro ao cadastrar cliente"}), 500

                

                #geocodificando o endereco
                try:    
                    # garante que nenhum campo obrigatório é None
                    bairro = dados_pedido.get('bairro') 
                    cidade = dados_pedido.get('cidade') 

                    lat, lng = geocodificar_google(dados_pedido['endereco'], bairro=bairro, cidade=cidade)
                    novo_endereco = Endereco_Adm(
                        cliente_id= cliente.id,
                        endereco=dados_pedido['endereco'],
                        latitude=lat,  
                        longitude=lng, 
                        numero=dados_pedido.get('numero', ''),
                        ponto_ref=dados_pedido.get('ponto_ref', ''),
                        obs=dados_pedido.get('obs', ''),
                        bairro=bairro,
                        cidade=cidade
                    )
                    db.session.add(novo_endereco)
                    db.session.flush()
                        
                    
                except Exception as e:
                    
                    print(f"Erro ao geocodificar o endereço: {e}")
                    return jsonify({"msg": "Erro ao geocodificar o endereço"}), 500


                db.session.commit()


            return jsonify({"msg": "Cliente cadastrado com sucesso"}), 201
            
        #except Exception as e:
        #    print(f"Erro ao procsessar o PDF: {e}")
        #    return jsonify({"msg": "Erro ao processar o PDF"}), 500
    else:
        # Significa que o cadastro será feito por JSON
        data = request.get_json()
        if not data or not data.get('codigo_externo'):
            print('Error data/codigo')
            return jsonify({"msg": "Dados inválidos"}), 400
        
        cliente = Cliente.query.filter_by(codigo_externo=data['codigo_externo']).first()
        if cliente:
            print('Error cliente já exiSte')
            
            return jsonify({"msg": "Cliente já existe", "codigo_cliente": cliente.codigo_externo}), 400

        novo_cliente = Cliente(
            codigo_externo = data['codigo_externo'],
            nome = data['nome'],
            email=data['email'] if data['email'] else None,
            telefone_cadastro = data['tell_cadastro'],
            telefone_motorista  = data['tell_motorista']  if data['tell_motorista'] else None,
            usuario_id = payload['id'] 
        )

        db.session.add(novo_cliente)
        db.session.flush()
        if data['endereco_nota']:
            lat, lng = geocodificar_google(data['endereco_nota'])
            endereco_nota = Endereco_Adm(
                cliente_id = novo_cliente.id,
                endereco= data['endereco_nota'],
                latitude = lat,
                longitude = lng,
                numero = data['numero'],
                ponto_ref = data['ponto_ref'],
                obs = data['obs'],
                bairro = data['bairro'],
                cidade = data['cidade']
                
        )
        db.session.add(endereco_nota)
        if data['endereco_motorista']:
            lat, lng = geocodificar_google(data['endereco_motorista'])
            endereco_motorista = Endereco_Motorista(
                cliente_id = novo_cliente.id,
                endereco= data['endereco_motorista'],
                latitude = lat,
                longitude = lng,
                numero = data['numero_motorista'],
                ponto_ref = data['ponto_ref_motorista'],
                obs = data['obs_motorista'],
                bairro = data['bairro'],
                cidade = data['cidade']
            )
            db.session.add(endereco_motorista)
        db.session.commit()
        return jsonify({"msg": "Cliente cadastrado com sucesso"}), 200
    


@comercial_bp.route('/cadastrar_pedido', methods=['POST'])
@jwt_required()
def cadastrar_pedido():
    payload = get_jwt()
    file = request.files.get('arquivo')
    if file:
    
            dados_pedido = limpar_pdf_pedido(file)
            if not dados_pedido:
                return jsonify({"msg": "Erro ao processar os dados do pedido"}), 400
            cliente = Cliente.query.filter_by(codigo_externo=dados_pedido['cod_cliente']).first()
            if not cliente:
                return jsonify({"msg": "Cliente não encontrado"}), 404
            
            pedido = Pedido.query.filter_by(cod_externo=dados_pedido['codigo_pedido']).first()
            if pedido:
                return jsonify({"msg": "Pedido já cadastrado"}), 400
            end = Endereco_Adm.query.filter_by(cliente_id=cliente.id).first()
            #return f"{end.id}"
            novo_pedido = Pedido(
                cod_externo=dados_pedido['codigo_pedido'],
                cliente_id=cliente.id,
                status='Pendente',
                data_criacao=get_agora(),
                data_entrega=None,
                endereco_adm_id=end.id,
                vendendor_id = payload['id']
                #endereco_motorista_id=end.id #int(request.form.get('endereco_motorista')) if request.form.get('endereco_motorista') else None     
            )
            db.session.flush()

            db.session.add(novo_pedido)

            #ESTUDAR MELHOR MANEIRA DE FAZER ISSO PARA CONSUMIER MENOS
            for produto in dados_pedido['produtos']:
                    produto_db = Produto.query.filter_by(codigo=produto['codigo']).first()
                    if produto_db:
                        produto_pedido = Produto_Pedido(
                            pedido_id=novo_pedido.id,
                            produto_id=produto_db.id,
                            quantidade=produto['quantidade']
                        )
                        db.session.add(produto_pedido) 

                    if not produto_db:
                        if "ACAI" in produto['produto'].upper():
                            categoria_produto='Açaí'
                        if "CR" in produto['produto'].upper():
                            categoria_produto='Creme'
                        novo_produto = Produto(
                            nome=produto['produto'],
                            codigo=produto['codigo'],
                            categoria=categoria_produto,
                            tipo='CX 10L',
                            preco=0.0,)  # Defina um preço padrão ou obtenha de outra forma
                        db.session.add(novo_produto)
                        db.session.flush()
                        produto_pedido = Produto_Pedido(
                            pedido_id=novo_pedido.id,
                            produto_id=novo_produto.id,
                            quantidade=produto['quantidade']
                        )
                        db.session.add(produto_pedido)
            db.session.commit()
            return jsonify(dados_pedido), 200
        

@comercial_bp.route('/cadastrar_endereco_motorista', methods=['POST', 'PUT'])
@jwt_required()
def cadastrar_endereco_motorista():
    data = request.get_json() #CODIGO_CLIENTE, ENDERECO

    if request.method == 'POST':
        lat, lng = geocodificar_google(data['endereco'])
        cliente = Cliente.query.filter_by(codigo_externo=data['codigo_externo']).first()
        if not cliente:
            print('cliente não encontrado', data['codigo_externo'], '====================================')
        novo_endereco = Endereco_Motorista(
            cliente_id=cliente.id,
            endereco= data['endereco'],
            latitude=lat,  
            longitude=lng,
            numero=data['numero'],
            ponto_ref= data['ponto_ref'],
            obs= data['obs']
            )
        db.session.add(novo_endereco)
        db.session.commit()
        return jsonify({"msg": "Endereço adicionado com sucesso"}), 201

    if request.method == 'PUT':
        pass


@comercial_bp.route('/cadastrar')
@jwt_required()
def cadastrar():
    data = request.get_json()
    payload = get_jwt()
    pwd = generate_password_hash(data['pwd'])
"""

    novo_perfil = Perfil(
        nome = data['nome'],
        sobrenome = data['sobrenome'],
        tell = data['tell'],
        setor = data['setor'],
        cargo = data['cargo'],
        cnh = data['cnh'],
    )
    
    novo_user = Usuario(
        email = data['email'],
        pwd = pwd,
        autor = payload['id']
        perfil_id = novo_perfil.id
    )"""


@comercial_bp.route('/update_cliente/<codigo_externo>')
@jwt_required()
def update_cliente(codigo_externo):
    dados = request.get_json()
    print(dados)
    return jsonify({'msg':f'Dados recebidos ({dados})'})


@comercial_bp.route('/teste', methods=['POST'])
def teste():
    file = request.files.get('arquivo')
    if not file:
        return jsonify({"msg": "Arquivo não enviado"}), 400

    pedido = limpar_pdf_pedido(file)
    if not pedido:
        return jsonify({"msg": "Erro ao processar o PDF"}), 400

    return jsonify(pedido), 200

