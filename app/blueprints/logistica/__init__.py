from flask import Blueprint
from flask_cors import CORS, cross_origin
logistica_bp = Blueprint('logistica', __name__, template_folder='/blueprints/logistica/templates/test.html')
CORS(logistica_bp) 

#Não entendi exatamente o pq mas esse codigo precisa existir
from . import routs