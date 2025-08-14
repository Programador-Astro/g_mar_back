from flask import Blueprint
logistica_bp = Blueprint('logistica', __name__, template_folder='/blueprints/logistica/templates/test.html')

#Não entendi exatamente o pq mas esse codigo precisa existir
from . import routs