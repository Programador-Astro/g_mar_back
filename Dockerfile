# Etapa 1: Builder
FROM python:3.10-slim as builder

WORKDIR /app

# Instala dependências do sistema necessárias para compilar alguns pacotes Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc

# Copia e instala as dependências do Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Copia dependências instaladas da etapa de build
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia a aplicação
COPY . .

# Define variáveis de ambiente padrão
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expõe a porta usada pelo gunicorn
EXPOSE 8080

# Usa o Gunicorn como servidor WSGI (mais robusto que flask run)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "run:app"]
