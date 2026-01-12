# 🔌 Configuración de MongoDB MCP

Guía rápida para conectar el servidor MCP a tu base de datos MongoDB existente.

## 📋 Requisitos Previos

- Tu base de datos MongoDB debe estar accesible (local, remota, o MongoDB Atlas)
- Conocer la URI de conexión a tu MongoDB
- Nombre de la base de datos que quieres consultar

## ⚙️ Configuración

### 1. Crear archivo `.env`

Crea un archivo `.env` en la raíz del proyecto (o copia `.env.example`):

```bash
cp .env.example .env
```

### 2. Configurar la URI de MongoDB

Edita `.env` y actualiza las variables de MongoDB:

```bash
# Para MongoDB local en tu máquina
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=tu_base_de_datos

# Para MongoDB Atlas
MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net
MONGODB_DATABASE=tu_base_de_datos

# Para MongoDB con autenticación
MONGODB_URI=mongodb://usuario:password@host:27017/database?authSource=admin
MONGODB_DATABASE=tu_base_de_datos
```

**⚠️ IMPORTANTE**: Si ejecutas el proyecto con Docker y tu MongoDB está en `localhost`:
```bash
# Usar host.docker.internal en lugar de localhost
MONGODB_URI=mongodb://host.docker.internal:27017
```

### 3. Actualizar `docker-compose.yml` (Opcional)

Si quieres configurar las variables directamente en `docker-compose.yml`:

```yaml
services:
  langchain-api:
    environment:
      - MONGODB_URI=tu_uri_aqui
      - MONGODB_DATABASE=tu_base_de_datos
```

## 🚀 Iniciar el Sistema

### Con Docker (Recomendado)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f langchain-api

# Verificar que está corriendo
docker-compose ps
```

### Sin Docker

```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar API server
cd app
python api_server.py
```

## 🧪 Probar la Conexión

### Opción 1: Script de prueba

```bash
# Desde el contenedor Docker
docker exec -it langchain-app python /app/mcp_server/mongodb_mcp.py

# O localmente
cd app/mcp_server
python mongodb_mcp.py
```

### Opción 2: Explorar tu base de datos

```bash
# Ver colecciones, documentos y estructura
docker exec -it langchain-app python /app/mcp_server/query_examples.py

# O localmente
cd app/mcp_server
python query_examples.py
```

### Opción 3: Ejemplo de integración con LLM

```bash
# Ver cómo el LLM puede consultar tus datos
docker exec -it langchain-app python /app/mcp_server/llm_integration_example.py

# O localmente
cd app/mcp_server
python llm_integration_example.py
```

## 📊 Ejemplo de Uso

Una vez configurado, el LLM podrá responder preguntas sobre tus datos:

```python
from mcp_server import create_mongodb_mcp_server
import json

server = create_mongodb_mcp_server()

# Listar colecciones
result = server.execute_tool("mongodb_list_collections", {})
print(json.dumps(json.loads(result), indent=2))

# Contar documentos
result = server.execute_tool("mongodb_count", {
    "collection": "usuarios",
    "filter_json": "{}"
})
print(json.dumps(json.loads(result), indent=2))

# Buscar documentos
result = server.execute_tool("mongodb_find", {
    "collection": "productos",
    "filter_json": '{"categoria": "electronics"}',
    "limit": 5
})
print(json.dumps(json.loads(result), indent=2))

server.close()
```

## 🔍 Verificar Configuración

### 1. Verificar variables de entorno

```bash
# Desde Docker
docker exec -it langchain-app env | grep MONGODB

# O revisar tu .env
cat .env | grep MONGODB
```

### 2. Probar conexión directa con mongosh

```bash
# Probar que MongoDB es accesible
mongosh "tu_uri_de_conexion" --eval "db.adminCommand('ping')"
```

### 3. Verificar desde Python

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)

print("✅ Conexión exitosa!")
print("Bases de datos:", client.list_database_names())

db_name = os.getenv("MONGODB_DATABASE")
db = client[db_name]
print(f"Colecciones en '{db_name}':", db.list_collection_names())

client.close()
```

## 🛠️ Solución de Problemas

### Error: "No module named 'pymongo'"

```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Error: "Connection refused" o "Connection timeout"

**Causa**: MongoDB no es accesible desde el contenedor Docker.

**Solución**:
1. Si MongoDB está en localhost, usa `host.docker.internal`:
   ```bash
   MONGODB_URI=mongodb://host.docker.internal:27017
   ```

2. Verifica que MongoDB está corriendo:
   ```bash
   mongosh mongodb://localhost:27017 --eval "db.version()"
   ```

3. Si usas MongoDB Atlas, verifica:
   - Tu IP está en la whitelist
   - Usuario/password son correctos
   - URI incluye `mongodb+srv://`

### Error: "Authentication failed"

**Solución**: Verifica usuario, password y authSource:
```bash
MONGODB_URI=mongodb://usuario:password@host:27017/database?authSource=admin
```

### Error: "Database does not exist"

**Solución**: Verifica el nombre de la base de datos:
```bash
# Listar bases de datos disponibles
mongosh "tu_uri" --eval "show dbs"

# Actualizar MONGODB_DATABASE en .env
MONGODB_DATABASE=nombre_correcto
```

### El LLM no puede acceder a los datos

**Verifica**:
1. ✅ Variables de entorno configuradas
2. ✅ MongoDB accesible (prueba con mongosh)
3. ✅ Servicios corriendo (docker-compose ps)
4. ✅ Logs sin errores (docker-compose logs)

## 📚 Documentación Adicional

- **Documentación completa**: `app/mcp_server/README.md`
- **Ejemplos de consultas**: `app/mcp_server/query_examples.py`
- **Integración con LLM**: `app/mcp_server/llm_integration_example.py`
- **Herramientas disponibles**: Ver `app/mcp_server/mongodb_mcp.py`

## 💡 Próximos Pasos

1. ✅ Configurar conexión a MongoDB
2. ✅ Probar con `query_examples.py`
3. ⚙️ Integrar con tu API server (ver `llm_integration_example.py`)
4. 🤖 Permitir que el LLM consulte tus datos

## 🆘 Ayuda

Si tienes problemas:

1. Verifica los logs:
   ```bash
   docker-compose logs -f langchain-api
   ```

2. Ejecuta los scripts de prueba:
   ```bash
   docker exec -it langchain-app python /app/mcp_server/mongodb_mcp.py
   ```

3. Verifica la configuración:
   ```bash
   docker exec -it langchain-app env | grep MONGODB
   ```

---

**¿Listo?** Ejecuta:
```bash
docker-compose up -d
docker exec -it langchain-app python /app/mcp_server/query_examples.py
```
