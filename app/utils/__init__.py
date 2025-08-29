
import os, re, fitz, time, googlemaps, datetime, pytz
from io import BytesIO
from dotenv import load_dotenv
from app.models import *
from functools import wraps
from flask import request, jsonify, session

load_dotenv()


def limpar_pdf_pedido(pdf_file):
    try:
        pdf_bytes = pdf_file.read()
        pdf_stream = BytesIO(pdf_bytes)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")

        # Extrai todo o texto do PDF
        texto = ""
        for page in doc:
            texto += page.get_text("text")  # extração mais precisa
        doc.close()

        # Expressões regulares para os campos
        patterns = {
            "codigo_pedido": r"Nº Pedido:\s*(\d+)",
            "cliente": r"\nCliente:\s*(.+)",
            "cod_cliente": r"Cod\.Cliente:\s*(\d+)",
            "endereco": r"Endereço:\s*(.+)",
            "bairro": r"Bairro:\s*(.+)",
            "cidade": r"Cidade:\s*(.+)",
            "uf": r"UF:\s*([A-Z]{2})",
            "vendendor": r"RCA:s*(.+)",
        }

        # Busca dos dados principais
        dados_extraidos = {}
        for chave, regex in patterns.items():
            match = re.search(regex, texto)
            dados_extraidos[chave] = limpar_texto(match.group(1)) if match else "Não encontrado"

        produtos_e_qtds = re.findall(
            r"(\d+)\s+(DG|SMO|MON|AG|NTZ|A73)\s+--\s+(.+?)\s+--(?:.*?CX\s*10L\s*)+.*?(\d+,\d+)",
            texto
        )
        
        produtos = []
        for codigo, sigla, produto, quantidade in produtos_e_qtds:
            produtos.append({
                "codigo": codigo,
                "sigla": sigla,
                "produto": limpar_texto(produto),
                "quantidade": quantidade.replace(',', '.')
            })


        # Resultado final
        return {
            **dados_extraidos,
            "produtos": produtos
        }

    except Exception as e:
        return {"msg": "Erro ao processar o PDF", "error": str(e)}

def limpar_texto(texto):
    if not texto:
        return ""
    texto = texto.strip()
    texto = re.sub(r'[\r\n]+', ' ', texto)  # Remove quebras de linha
    texto = re.sub(r'\s+/\w*$', '', texto)  # Remove "/X" no final de linhas
    texto = re.sub(r'\s+', ' ', texto)      # Normaliza múltiplos espaços
    return texto



def geocodificar_google(endereco, bairro=None, cidade=None):
    try:
        
        if cidade != None and bairro != None:
            print(f"🔎Geocodificando Com cidade e Biarro: {endereco, cidade, bairro}")
            geocodificar = f"{endereco}, {bairro}, {cidade}"
        else:
            print(f"🔎Geocodificando: {endereco}")
            geocodificar = f"{endereco}"
        API_KEY = os.getenv('GOOGLE_KEY')
        # Cria o cliente do Google Maps
        gmaps = googlemaps.Client(key=API_KEY)

        # Limite de queries por segundo (QPS)
        QPS = int(os.getenv('QPS', 5))
        WAIT_TIME = 1 / QPS
        
        resultado = gmaps.geocode(geocodificar)

        time.sleep(WAIT_TIME)  # Controla o rate limit
        if resultado:
            location = resultado[0]["geometry"]["location"]
            print(f"📍 Coordenadas: {location['lat']}, {location['lng']}")
            return location['lat'], location['lng']
        else:
            print("⚠️ Endereço não encontrado")
            return None, None
    except Exception as e:
        print(f"⛔ Erro na geocodificação: {e}")
        return None, None


def get_agora(estado="Sao_Paulo"):

    # Pega a hora do servidor em UTC
    agora_utc = datetime.datetime.now(pytz.utc)

    # Converte para o fuso horário de Brasília para enviar ao frontend
    # Ou simplesmente envie a UTC e converta no frontend se precisar
    fuso_horario_brasil = pytz.timezone(f'America/{estado}')
    agora_brasil = agora_utc.astimezone(fuso_horario_brasil)

    # Retorna a hora formatada em JSON
    return agora_brasil.strftime('%Y-%m-%d %H:%M:%S')





def verifica_setor(setor_necessario):
    """
    Decorador que verifica se o usuário logado tem o setor necessário para acessar a rota.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obtém o ID do usuário a partir da sessão
            id_user = session.get('id_user')

            if not id_user:
                return jsonify({"erro": "Usuário não está logado."}), 401

            usuario = Usuario.query.filter_by(id=id_user).first()
            print(f"Setor esperado: {setor_necessario}")
            print(f"Setor do usuário: {usuario.perfil.setor}")
            if not usuario:
                return jsonify({"erro": "Usuário não encontrado."}), 404

            # Verifica se o setor do usuário é o setor necessário
            if usuario.perfil.setor != setor_necessario:
                return jsonify({"erro": "Acesso negado. Setor não autorizado."}), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator
