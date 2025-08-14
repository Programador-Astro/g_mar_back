from .users import Usuario, Perfil  # Ajuste o nome da classe se for diferente
from .veiculos import Veiculos, Checklist  # Ajuste se necessário


# Exporta todos os modelos para facilitar importações
__all__ = [
    "Usuario",
    "Perfil",
    "Veiculos",
    "Checklist"
]
