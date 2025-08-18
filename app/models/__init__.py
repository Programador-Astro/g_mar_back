from .users import Usuario, Perfil  # Ajuste o nome da classe se for diferente
from .veiculos import Veiculos, Checklist  # Ajuste se necessário
from .clientes import Cliente, Endereco_Adm, Endereco_Motorista, Pedido, Produto_Pedido, Produto

# Exporta todos os modelos para facilitar importações
__all__ = [
    "Usuario",
    "Perfil",
    "Veiculos",
    "Checklist",
    "Cliente",
    "Endereco_Adm",
    "Endereco_Motorista",
    "Pedido",
    "Produto_Pedido",
    "Produto"
]
