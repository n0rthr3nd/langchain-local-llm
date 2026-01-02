# LangChain + Ollama en Docker (Windows)

Entorno completo para desarrollar con LangChain usando LLMs locales sin costes.

## Requisitos Previos

- **Docker Desktop para Windows** (con WSL2)
- **16 GB RAM** recomendado (8 GB minimo)
- **10 GB espacio en disco** para modelos

## Inicio Rapido

### 1. Iniciar Ollama

```powershell
# Iniciar solo Ollama primero
docker-compose up -d ollama

# Verificar que esta corriendo
docker logs ollama-server
```

### 2. Descargar Modelos

```powershell
# Modelo principal (3.2 GB)
docker exec ollama-server ollama pull llama3.2

# Modelo de embeddings para RAG (274 MB)
docker exec ollama-server ollama pull nomic-embed-text

# Verificar modelos instalados
docker exec ollama-server ollama list
```

### 3. Iniciar Aplicacion

```powershell
# Iniciar todo
docker-compose up -d

# Ver logs
docker-compose logs -f langchain-app
```

### 4. Ejecutar Ejemplos

```powershell
# Ejemplos basicos
docker exec -it langchain-app python main.py

# Ejemplo RAG
docker exec -it langchain-app python rag_example.py

# Iniciar API REST
docker exec -it langchain-app python api_server.py
```

## Endpoints de la API

Una vez iniciada la API en `http://localhost:8000`:

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/models` | GET | Listar modelos disponibles |
| `/chat` | POST | Chat simple |
| `/chat/stream` | POST | Chat con streaming |
| `/analyze` | POST | Analisis de texto |

### Ejemplo de uso con curl:

```bash
# Chat simple
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, quien eres?"}'

# Analisis de sentimiento
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Me encanta este producto!", "task": "sentiment"}'
```

## Modelos Disponibles

| Modelo | Tamano | RAM Necesaria | Uso Recomendado |
|--------|--------|---------------|-----------------|
| `phi3:mini` | 2.3 GB | 8 GB | Tareas simples |
| `llama3.2` | 4.7 GB | 16 GB | Uso general |
| `mistral` | 4.1 GB | 16 GB | Buen balance |
| `llama3.1:70b` | 40 GB | 64 GB | Alta calidad |

Para cambiar de modelo:

```powershell
# Descargar nuevo modelo
docker exec ollama-server ollama pull mistral

# Configurar en docker-compose.yml o variable de entorno
# MODEL_NAME=mistral
```

## Estructura del Proyecto

```
langchain-local-llm/
├── docker-compose.yml    # Configuracion de servicios
├── Dockerfile            # Imagen de la app
├── requirements.txt      # Dependencias Python
├── app/
│   ├── main.py          # Ejemplos basicos
│   ├── rag_example.py   # Ejemplo RAG completo
│   └── api_server.py    # API REST con FastAPI
└── scripts/
    └── setup.ps1        # Script de configuracion
```

## Uso con GPU (NVIDIA)

Si tienes GPU NVIDIA, descomenta las lineas en `docker-compose.yml`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

Requiere:
- NVIDIA drivers actualizados
- NVIDIA Container Toolkit instalado

## Troubleshooting

### Ollama no responde

```powershell
# Reiniciar contenedor
docker-compose restart ollama

# Ver logs
docker logs ollama-server
```

### Error de memoria

Reduce el modelo o aumenta la memoria de Docker Desktop:
Settings > Resources > Memory

### Modelo no encontrado

```powershell
# Listar modelos disponibles
docker exec ollama-server ollama list

# Descargar modelo faltante
docker exec ollama-server ollama pull <nombre-modelo>
```

## Desarrollo Local (sin Docker)

Si prefieres ejecutar sin Docker:

1. Instalar Ollama nativo: https://ollama.ai
2. Crear entorno virtual:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   pip install -r requirements.txt
   ```
3. Ejecutar:
   ```powershell
   cd app
   python main.py
   ```
