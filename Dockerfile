# Dockerfile para LangChain App
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo de la aplicacion
COPY app/ .

# Puerto para la API (si usas FastAPI)
EXPOSE 8000

# Comando por defecto
CMD ["python", "main.py"]
