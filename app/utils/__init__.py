import jwt, datetime, time, os, dotenv

from dotenv import load_dotenv


def gerar_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1), # Expira em 1 hora
        "iat": datetime.datetime.utcnow() # Issued at (emitido em)
    }
    token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm="HS256")
    return token

def decodificar_token(token):
    try:
        payload = jwt.decode(token,  os.getenv('SECRET_KEY'), algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token expirado."}
    except jwt.InvalidTokenError:
        return {"error": "Token inválido."}