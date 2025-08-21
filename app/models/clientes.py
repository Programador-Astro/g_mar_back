from app import db

class Cliente(db.Model):
    __tablename__ = 'clientes'  

    id = db.Column(db.Integer, primary_key=True)
    codigo_externo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    telefone_cadastro = db.Column(db.String(15), nullable=True)
    telefone_motorista = db.Column(db.String(15), nullable=True)

    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    endereco_adm = db.relationship('Endereco_Adm', backref='cliente')
    endereco_motorista = db.relationship('Endereco_Motorista', backref='cliente')

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

class Endereco_Adm(db.Model):
    __tablename__ = 'enderecos_adm'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    endereco = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    ponto_ref = db.Column(db.String(100), nullable=True)
    obs = db.Column(db.String(100), nullable=True)

class Endereco_Motorista(db.Model):
    __tablename__ = 'enderecos_motoristas'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    endereco = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    ponto_ref = db.Column(db.String(100), nullable=True)
    obs = db.Column(db.String(100), nullable=True)


class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    cod_externo = db.Column(db.String(50), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False)
    data_entrega = db.Column(db.DateTime, nullable=True, default=None)

    endereco_adm_id = db.Column(db.Integer, db.ForeignKey('enderecos_adm.id'), nullable=False)
    endereco_motorista_id = db.Column(db.Integer, db.ForeignKey('enderecos_motoristas.id'), nullable=True)
    motorista_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    cliente = db.relationship('Cliente', backref='pedidos')
    endereco_adm = db.relationship('Endereco_Adm', backref='pedidos')
    endereco_motorista = db.relationship('Endereco_Motorista', backref='pedidos')
    motorista = db.relationship('Usuario', backref='pedidos', lazy=True)

    produtos = db.relationship('Produto_Pedido', backref='pedido', lazy=True)

class Produto_Pedido(db.Model):
    __tablename__ = 'produtos_pedidos'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)

    produto = db.relationship('Produto', backref='produtos_pedidos')


class Produto(db.Model):
    
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    
    preco = db.Column(db.Float, nullable=False)
    #descricao = db.Column(db.String(255), nullable=True)
    peso = db.Column(db.Float, nullable=True)

