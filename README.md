# ChatGPT Local con Ollama

Aplicación web completa estilo ChatGPT usando Ollama como backend LLM. Stack completo: React + TypeScript + FastAPI + Docker.

## Características

- **Frontend Moderno**: React + TypeScript + Vite + Tailwind CSS
- **UI tipo ChatGPT**: Chat en tiempo real con streaming de respuestas
- **Backend FastAPI**: API REST con endpoints para chat y modelos
- **Streaming en tiempo real**: Respuestas token por token
- **Gestión de conversaciones**: Guardar, cargar y exportar conversaciones
- **Configuración de modelos**: Cambiar modelo, temperature y max tokens
- **Renderizado de Markdown**: Soporte completo con resaltado de sintaxis
- **100% Local**: Sin enviar datos a servicios externos
- **Docker**: Todo se ejecuta en contenedores

## Requisitos Previos

- **Docker Desktop para Windows** (con WSL2)
- **16 GB RAM** recomendado (8 GB minimo)
- **10 GB espacio en disco** para modelos

## Inicio Rápido

### 1. Clonar y levantar servicios

```powershell
# Clonar el repositorio (si no lo has hecho)
git clone <tu-repo>
cd langchain-local-llm

# Levantar todos los servicios
docker-compose up -d
```

### 2. Descargar modelos

```powershell
# Modelo principal (2GB - rápido y eficiente)
docker exec ollama-server ollama pull llama3.2

# Modelos alternativos (opcional)
docker exec ollama-server ollama pull mistral
docker exec ollama-server ollama pull phi3:mini

# Verificar modelos instalados
docker exec ollama-server ollama list
```

### 3. Acceder a la aplicación

Abre tu navegador en:

```
http://localhost:3000
```

La interfaz web estará lista para usar. El backend API está en `http://localhost:8000`.

### 4. Ver logs

```powershell
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f web          # Frontend
docker-compose logs -f langchain-app  # Backend
docker-compose logs -f ollama        # Ollama
```

## Arquitectura

```
┌─────────────────────────────────────────────────┐
│                   Usuario                        │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│  Frontend (React + Vite)                        │
│  Puerto: 3000                                   │
│  - UI tipo ChatGPT                              │
│  - Streaming SSE                                │
│  - Gestión de conversaciones                    │
└───────────────────┬─────────────────────────────┘
                    │ HTTP/API
                    ▼
┌─────────────────────────────────────────────────┐
│  Backend (FastAPI)                              │
│  Puerto: 8000                                   │
│  - /models (GET)                                │
│  - /chat (POST)                                 │
│  - /chat/stream (POST)                          │
└───────────────────┬─────────────────────────────┘
                    │ LangChain
                    ▼
┌─────────────────────────────────────────────────┐
│  Ollama Server                                  │
│  Puerto: 11434                                  │
│  - Modelos LLM locales                          │
│  - GPU/CPU support                              │
└─────────────────────────────────────────────────┘
```

## Endpoints de la API

### GET /models

Lista modelos disponibles en Ollama.

```bash
curl http://localhost:8000/models
```

### POST /chat

Chat sin streaming (respuesta completa).

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hola, ¿cómo estás?"}
    ],
    "model": "llama3.2",
    "temperature": 0.7,
    "max_tokens": 512
  }'
```

### POST /chat/stream

Chat con streaming (tokens en tiempo real).

```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Escribe un poema corto"}
    ],
    "model": "llama3.2",
    "temperature": 0.9
  }'
```

## Configuración

### Variables de Entorno

Puedes configurar el backend editando `docker-compose.yml`:

```yaml
environment:
  - OLLAMA_BASE_URL=http://ollama:11434
  - MODEL_NAME=llama3.2
  - PORT=8000
  - MAX_INPUT_LENGTH=10000
```

### Cambiar modelo por defecto

```yaml
# En docker-compose.yml
environment:
  - MODEL_NAME=mistral  # Cambiar aquí
```

## Modelos Recomendados

| Modelo | Tamaño | RAM | Uso |
|--------|--------|-----|-----|
| `phi3:mini` | 2.3 GB | 8 GB | Tareas simples, desarrollo |
| `llama3.2` | 2 GB | 8 GB | Uso general, rápido |
| `mistral` | 4.1 GB | 16 GB | Balance calidad/velocidad |
| `llama3.1:8b` | 4.7 GB | 16 GB | Alta calidad |
| `llama3.1:70b` | 40 GB | 64 GB | Máxima calidad (requiere GPU) |

## Estructura del Proyecto

```
langchain-local-llm/
├── frontend/                  # Frontend React
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   ├── MessageItem.tsx
│   │   │   ├── ModelSelector.tsx
│   │   │   └── ConversationList.tsx
│   │   ├── hooks/           # Custom hooks
│   │   │   └── useChat.ts
│   │   ├── types/           # TypeScript types
│   │   │   └── index.ts
│   │   ├── utils/           # Utilidades
│   │   │   ├── api.ts
│   │   │   └── storage.ts
│   │   ├── styles/          # Estilos
│   │   │   └── index.css
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.ts
├── app/                      # Backend Python
│   ├── api_server.py        # API FastAPI principal
│   ├── main.py              # Ejemplos
│   ├── rag_example.py
│   └── tests/               # Tests
│       └── test_api.py
├── docker-compose.yml        # Orquestación de servicios
├── Dockerfile               # Backend container
├── requirements.txt         # Dependencias Python
└── README.md
```

## Desarrollo Local

### Frontend (sin Docker)

```powershell
cd frontend
npm install
npm run dev
```

Accede en `http://localhost:5173`

### Backend (sin Docker)

```powershell
# Instalar Ollama: https://ollama.ai
# Descargar modelo
ollama pull llama3.2

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
cd app
python api_server.py
```

### Ejecutar tests

```powershell
# En el contenedor
docker exec langchain-app pytest tests/ -v

# Local
cd app
pytest tests/ -v
```

## Uso con GPU NVIDIA

Si tienes GPU NVIDIA, el rendimiento será mucho mejor.

### Requisitos

1. Drivers NVIDIA actualizados
2. [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

### Verificar

```powershell
# Verificar que Docker puede ver la GPU
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

El docker-compose.yml ya está configurado para usar GPU. Si no tienes GPU, comenta estas líneas:

```yaml
# deploy:
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
#           count: all
#           capabilities: [gpu]
```

## Funcionalidades de la UI

### Gestión de Conversaciones

- **Nueva conversación**: Botón en la barra lateral
- **Cambiar conversación**: Click en conversación guardada
- **Eliminar conversación**: Botón de basura (hover)
- **Auto-guardado**: Las conversaciones se guardan automáticamente en localStorage

### Controles de Chat

- **Enviar mensaje**: Enter (Shift+Enter para nueva línea)
- **Stop generación**: Botón de stop durante streaming
- **Regenerar**: Regenera la última respuesta
- **Limpiar chat**: Elimina todos los mensajes

### Configuración

- **Modelo**: Selecciona entre modelos disponibles
- **Temperature**: 0.0 (determinista) a 2.0 (creativo)
- **Max Tokens**: Longitud máxima de respuesta
- **System Prompt**: Instrucciones para el asistente

### Export/Import

Las conversaciones se guardan en localStorage y pueden exportarse/importarse manualmente desde el navegador.

## Troubleshooting

### Ollama no responde

```powershell
# Reiniciar contenedor
docker-compose restart ollama

# Ver logs
docker logs ollama-server

# Verificar que está corriendo
docker exec ollama-server ollama list
```

### Error de memoria

```powershell
# Aumentar memoria de Docker Desktop
# Settings > Resources > Memory > 8 GB o más

# O usar un modelo más pequeño
docker exec ollama-server ollama pull phi3:mini
```

### Frontend no carga

```powershell
# Verificar que el contenedor está corriendo
docker ps | grep chatgpt-web

# Reconstruir frontend
docker-compose up -d --build web

# Ver logs
docker logs chatgpt-web
```

### Backend error 503

```powershell
# Verificar que Ollama está corriendo
docker ps | grep ollama-server

# Verificar conectividad desde el backend
docker exec langchain-app curl http://ollama:11434/api/tags
```

### Puerto 3000 ya en uso

Cambia el puerto en `docker-compose.yml`:

```yaml
ports:
  - "3001:80"  # Cambiar 3000 a 3001
```

## Despliegue en Producción

Para producción, considera:

1. **HTTPS**: Usa un proxy reverso (nginx, Caddy, Traefik)
2. **Autenticación**: Implementa auth en el backend
3. **Rate limiting**: Limita peticiones por IP
4. **CORS**: Restringe orígenes permitidos
5. **Logs**: Configura logging centralizado
6. **Backup**: Backup de modelos y datos

## Licencia

Este proyecto es de código abierto. Ver LICENSE para más detalles.

## Recursos

- [Ollama](https://ollama.ai/)
- [LangChain](https://python.langchain.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request
