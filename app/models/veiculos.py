from app import db

class Veiculos(db.Model):
    __tablename__ = 'veiculos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    placa = db.Column(db.String(10), unique=True, nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, default=True)
    capacidade = db.Column(db.Float, nullable=False)
    km_atual = db.Column(db.Integer, nullable=False)

    src_ft_frontal = db.Column(db.String(200), nullable=True)
    src_ft_lateral1 = db.Column(db.String(200), nullable=True)
    src_ft_lateral2 = db.Column(db.String(200), nullable=True)
    src_ft_traseira = db.Column(db.String(200), nullable=True)


    autor = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Relacionamento: um veículo -> vários checklists
    checklists = db.relationship(
        "Checklist",
        back_populates="veiculo",
        cascade="all, delete-orphan"
    )


class Checklist(db.Model):
    __tablename__ = 'checklist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    placa = db.Column(db.String(10), db.ForeignKey('veiculos.placa'), nullable=False)
    km = db.Column(db.Integer, nullable=False)
    temperatura = db.Column(db.Float, nullable=False)
    combustivel = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    autor = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    obs =  db.Column(db.String(300), nullable=True)
    src_ft_frontal  = db.Column(db.String(200), nullable=True)
    src_ft_lateral1 = db.Column(db.String(200), nullable=True)
    src_ft_lateral2 = db.Column(db.String(200), nullable=True)
    src_ft_traseira = db.Column(db.String(200), nullable=True)
    # Relacionamento inverso
    veiculo = db.relationship(
        "Veiculos",
        back_populates="checklists"
    )
