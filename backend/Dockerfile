FROM python:3.12-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# (misma cabecera que arriba)

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

# Copia solo la carpeta app
COPY . /app/

# Variables de entorno seguras por defecto (puedes sobreescribir con docker-compose/.env)
ENV PYTHONUNBUFFERED=1
ENV UVICORN_WORKERS=4
ENV HOST=0.0.0.0
ENV PORT=8000

# Exponer puerto
EXPOSE 8000

# CMD: Gunicorn + Uvicorn workers (recomendado producción)
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]

