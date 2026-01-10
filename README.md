# LangChain + Ollama en Docker

Entorno completo para desarrollar con LangChain usando LLMs locales sin costes.

## 🚀 Plataformas Soportadas

- **Windows** (Docker Desktop con WSL2)
- **Linux** (x86_64 y ARM64)
- **macOS** (Intel y Apple Silicon)
- **🥧 Raspberry Pi 5** (8GB RAM) - [Ver guía específica](RASPBERRY_PI_SETUP.md)
- **☸️ Kubernetes (k3s)** - [Ver guía de despliegue](K8S_QUICKSTART.md) | [Documentación completa](K8S_DEPLOYMENT.md)

## Requisitos Previos

### Windows / macOS / Linux (x86_64)
- **Docker Desktop** o Docker Engine
- **16 GB RAM** recomendado (8 GB mínimo)
- **10 GB espacio en disco** para modelos

### Raspberry Pi 5
- **8GB RAM** (recomendado)
- **Docker** instalado
- **32GB+ microSD** o SSD USB
- Ver [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md) para guía completa

## Inicio Rápido

### 🥧 Para Raspberry Pi 5

**Usa la configuración optimizada para ARM64:**

```bash
# Instalación automática (recomendado)
chmod +x scripts/setup_rpi.sh
./scripts/setup_rpi.sh

# O manualmente:
docker compose -f docker-compose.rpi.yml up -d
docker exec ollama-server ollama pull gemma2:2b
```

📖 **Guía completa:** [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md)

---

### ☸️ Para Kubernetes (k3s)

**Despliegue en cluster k3s con auto-scaling y alta disponibilidad:**

```bash
# 1. Construir e importar imagen
./k8s/scripts/build-and-push.sh

# 2. Desplegar servicios
./k8s/scripts/deploy.sh

# 3. Descargar modelos
kubectl apply -f k8s/base/model-download-job.yaml
kubectl logs -n llm-services job/model-download -f

# 4. Verificar
kubectl get pods -n llm-services
```

**Acceso Web:** `https://northr3nd.duckdns.org/ia/chat`

📖 **Guías:**
- [Quick Start (5 minutos)](K8S_QUICKSTART.md)
- [Documentación completa](K8S_DEPLOYMENT.md)
- [Ejemplos de integración](k8s/EXAMPLES.md)

**Ventajas del despliegue en k3s:**
- ✅ Alta disponibilidad (múltiples réplicas de la API)
- ✅ Auto-scaling basado en CPU/memoria
- ✅ Balanceo de carga automático
- ✅ Integración nativa con otros servicios del cluster
- ✅ Actualizaciones rolling sin downtime
- ✅ NetworkPolicies para seguridad

---

### 💻 Para Windows / macOS / Linux

### 1. Clonar y levantar servicios

```bash
# Iniciar solo Ollama primero
docker compose up -d ollama

# Levantar todos los servicios
docker-compose up -d
```

### 2. Descargar modelos

```bash
# Modelo principal (4.7 GB)
docker exec ollama-server ollama pull llama3.2

# Modelos alternativos (opcional)
docker exec ollama-server ollama pull mistral
docker exec ollama-server ollama pull phi3:mini

# Verificar modelos instalados
docker exec ollama-server ollama list
```

### 3. Iniciar Aplicación

```bash
# Iniciar todo
docker compose up -d

# Ver logs
docker compose logs -f langchain-app
```

La interfaz web estará lista para usar. El backend API está en `http://localhost:8000`.

### 4. Ver logs

```bash
# Ejemplos básicos
docker exec -it langchain-app python main.py

# Ejemplo RAG
docker exec -it langchain-app python rag_example.py

# Iniciar API REST
docker exec -it langchain-app python api_server.py
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

## Modelos Disponibles

### Para PC / Laptop (16GB+ RAM)

| Modelo | Tamaño | RAM Necesaria | Uso Recomendado |
|--------|--------|---------------|-----------------|
| `llama3.2` | 4.7 GB | 16 GB | Uso general |
| `mistral` | 4.1 GB | 16 GB | Buen balance |
| `llama3.1:70b` | 40 GB | 64 GB | Alta calidad |

### Para Raspberry Pi / 8GB RAM

| Modelo | Tamaño | RAM Necesaria | Uso Recomendado |
|--------|--------|---------------|-----------------|
| `gemma2:2b` | 2.7 GB | 6 GB | ✅ Recomendado para RPI |
| `phi3:mini` | 2.3 GB | 6 GB | Código y razonamiento |
| `llama3.2:3b` | 2.0 GB | 5 GB | Tareas simples |
| `tinyllama` | 600 MB | 3 GB | Ultra ligero |

Para cambiar de modelo:

```bash
# Descargar nuevo modelo
docker exec ollama-server ollama pull mistral

# Configurar en .env
# MODEL_NAME=mistral
```

## Estructura del Proyecto

```
langchain-local-llm/
├── docker-compose.yml        # Configuración para PC/Laptop
├── docker-compose.rpi.yml    # 🥧 Configuración para Raspberry Pi
├── Dockerfile                # Imagen multi-arquitectura
├── requirements.txt          # Dependencias Python
├── .env.example             # Variables de entorno (PC)
├── .env.rpi                 # 🥧 Variables de entorno (RPI)
├── RASPBERRY_PI_SETUP.md    # 🥧 Guía completa para RPI
├── app/
│   ├── main.py              # Ejemplos básicos
│   ├── rag_example.py       # Ejemplo RAG completo
│   ├── agent_example.py     # Agentes con herramientas
│   └── api_server.py        # API REST con FastAPI
└── scripts/
    ├── setup.ps1            # Script Windows
    └── setup_rpi.sh         # 🥧 Script para Raspberry Pi
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
