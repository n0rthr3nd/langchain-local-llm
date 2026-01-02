# Inicio Rápido - ChatGPT Local con Ollama

## TL;DR - 3 Comandos para Empezar

```powershell
# 1. Levantar todos los servicios
docker-compose up -d

# 2. Descargar modelo
docker exec ollama-server ollama pull llama3.2

# 3. Abrir navegador
# http://localhost:3000
```

¡Listo! Ya tienes tu ChatGPT local funcionando.

---

## Estructura de Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **Frontend (Web)** | 3000 | Interfaz de usuario tipo ChatGPT |
| **Backend (API)** | 8000 | API REST con FastAPI |
| **Ollama** | 11434 | Servidor de modelos LLM |

## Comandos Útiles

### Ver Logs

```powershell
# Todos los servicios
docker-compose logs -f

# Solo frontend
docker-compose logs -f web

# Solo backend
docker-compose logs -f langchain-app

# Solo Ollama
docker-compose logs -f ollama
```

### Gestión de Modelos

```powershell
# Listar modelos instalados
docker exec ollama-server ollama list

# Descargar modelo
docker exec ollama-server ollama pull <modelo>

# Eliminar modelo
docker exec ollama-server ollama rm <modelo>
```

### Reiniciar Servicios

```powershell
# Reiniciar todo
docker-compose restart

# Reiniciar solo un servicio
docker-compose restart web
docker-compose restart langchain-app
docker-compose restart ollama
```

### Detener y Limpiar

```powershell
# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (¡cuidado, borra modelos!)
docker-compose down -v

# Reconstruir desde cero
docker-compose up -d --build
```

## Cambiar Configuración

### Cambiar Puerto del Frontend

Edita `docker-compose.yml`:

```yaml
web:
  ports:
    - "3001:80"  # Cambia 3000 a 3001
```

### Cambiar Modelo por Defecto

Edita `docker-compose.yml`:

```yaml
langchain-app:
  environment:
    - MODEL_NAME=mistral  # Cambia llama3.2 a mistral
```

### Aumentar Memoria para Docker

1. Abre Docker Desktop
2. Settings → Resources → Memory
3. Aumenta a 8 GB o más
4. Apply & Restart

## Modelos Recomendados

| Modelo | Tamaño | RAM | Comando |
|--------|--------|-----|---------|
| `phi3:mini` | 2.3 GB | 8 GB | `docker exec ollama-server ollama pull phi3:mini` |
| `llama3.2` | 2 GB | 8 GB | `docker exec ollama-server ollama pull llama3.2` |
| `mistral` | 4.1 GB | 16 GB | `docker exec ollama-server ollama pull mistral` |
| `llama3.1:8b` | 4.7 GB | 16 GB | `docker exec ollama-server ollama pull llama3.1:8b` |

## Problemas Comunes

### ❌ "Ollama no disponible"

```powershell
docker-compose restart ollama
docker logs ollama-server
```

### ❌ "Puerto 3000 ya en uso"

Cambia el puerto en `docker-compose.yml` (ver arriba).

### ❌ "Error de memoria"

Aumenta memoria de Docker Desktop o usa modelo más pequeño (`phi3:mini`).

### ❌ "Frontend no carga"

```powershell
docker-compose up -d --build web
docker logs chatgpt-web
```

### ❌ "Backend error 503"

```powershell
# Verificar que Ollama está corriendo
docker ps | grep ollama-server

# Verificar conectividad
docker exec langchain-app curl http://ollama:11434/api/tags
```

## Testing de API

### Con cURL

```bash
# Health check
curl http://localhost:8000/

# Listar modelos
curl http://localhost:8000/models

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hola"}],"model":"llama3.2"}'
```

### Con PowerShell

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/"

# Chat
$body = @{
    messages = @(@{role="user"; content="Hola"})
    model = "llama3.2"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"
```

## Desarrollo Local (Sin Docker)

### Frontend

```powershell
cd frontend
npm install
npm run dev
# Abre http://localhost:5173
```

### Backend

```powershell
# Instalar Ollama: https://ollama.ai
ollama pull llama3.2

python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt

cd app
python api_server.py
# Abre http://localhost:8000
```

## Documentación Completa

- **README.md** - Documentación completa
- **API_EXAMPLES.md** - Ejemplos de uso de la API
- **DOCKER_COMPOSE_EXPLICADO.md** - Detalles de Docker Compose

## Soporte

Si encuentras problemas:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica que todos los servicios están corriendo: `docker ps`
3. Revisa la sección Troubleshooting en README.md
4. Abre un issue en GitHub

---

**¡Disfruta tu ChatGPT local! 🚀**
