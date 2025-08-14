from flask import Blueprint
auth_bp = Blueprint('auth', __name__, template_folder='templates')

#Não entendi exatamente o pq mas esse codigo precisa existir
from . import routs