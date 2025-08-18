
import os, re, fitz, time, googlemaps, datetime, pytz
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

def limpar_pdf_pedido(pdf_file):

    try:
        pdf_bytes = pdf_file.read()
        pdf_stream = BytesIO(pdf_bytes)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        # Extração dos dados
        codigo_pedido_match = re.search(r"Nº Pedido:\s*(\d+)", text)
        cliente_match = re.search(r"\nCliente:\s*(.+)", text)
        cod_cliente_match = re.search(r"Cod\.Cliente:\s*(\d+)", text)
        endereco_match = re.search(r"Endereço:\s*(.+)", text)
        bairro_match = re.search(r"Bairro:\s*(.+)", text)
        cidade_match = re.search(r"Cidade:\s*(.+)", text)
        uf_match = re.search(r"UF:\s*([A-Z]{2})", text)
        produtos_e_qtds = re.findall(r"(\d+)\s+DG\s+--\s+(.+?)\s+--\s+CX 10L\s+CX 10L\s+(\d+,\d+)", text)

        # Limpeza dos dados
        codigo_pedido = codigo_pedido_match.group(1) if codigo_pedido_match else "Não encontrado"
        cliente = limpar_texto(cliente_match.group(1)) if cliente_match else "Não encontrado"
        cod_cliente = cod_cliente_match.group(1) if cod_cliente_match else "Não encontrado"
        endereco = limpar_texto(endereco_match.group(1)) if endereco_match else "Não encontrado"
        bairro = limpar_texto(bairro_match.group(1)) if bairro_match else "Não encontrado"
        cidade = limpar_texto(cidade_match.group(1)) if cidade_match else "Não encontrado"
        uf = uf_match.group(1) if uf_match else "Não encontrado"
        return {
            "codigo_pedido": codigo_pedido,
            "cliente": cliente,
            "cod_cliente": cod_cliente,
            "endereco": endereco,
            "bairro": bairro,
            "cidade": cidade,
            "uf": uf,
            "produtos": [
                {"codigo":codigo, "produto": limpar_texto(produto), "quantidade": quantidade.replace(',', '.')}
                for codigo, produto, quantidade in produtos_e_qtds
            ]
        }

    
    except: 
        return ({"msg": "Erro ao processar o PDF"})

def limpar_texto(texto):
        if not texto:
            return ""
        texto = texto.strip()
        texto = re.sub(r'[\r\n]+', ' ', texto)  # Remove quebras de linha
        texto = re.sub(r'/[A-Za-z]?$', '', texto)  # Remove / ou /(letra) no final
        texto = re.sub(r'\s+', ' ', texto)  # Normaliza espaços
        return texto.strip()



def geocodificar_google(endereco):
    print(f"🔎 Geocodificando: {endereco}")
    try:
        API_KEY = os.getenv('GOOGLE_KEY')
        # Cria o cliente do Google Maps
        gmaps = googlemaps.Client(key=API_KEY)

        # Limite de queries por segundo (QPS)
        QPS = int(os.getenv('QPS', 5))
        WAIT_TIME = 1 / QPS
        resultado = gmaps.geocode(endereco)
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