# API REST de Streaming - Documentación Técnica

Guía técnica para integrar servicios externos con los endpoints de streaming del sistema LangChain Local LLM.

## Información General

- **Base URL**: `http://localhost:8000` (configurable vía variable `PORT`)
- **Protocolo**: HTTP/HTTPS
- **Formato**: JSON para peticiones, texto plano para respuestas streaming
- **Autenticación**: API Key opcional mediante header `X-API-KEY`

---

## Endpoint de Streaming

### `POST /chat/stream`

Endpoint principal para conversaciones con streaming en tiempo real.

**URL**: `http://localhost:8000/chat/stream`

**Método**: `POST`

**Content-Type**: `application/json`

**Autenticación**: Header `X-API-KEY` (opcional, requerido si está configurada)

### Parámetros de la Petición

| Parámetro | Tipo | Requerido | Rango/Valores | Por Defecto | Descripción |
|-----------|------|-----------|---------------|-------------|-------------|
| `messages` | Array | ✅ Sí | - | - | Array de mensajes con `role` y `content` |
| `model` | String | ❌ No | Cualquier modelo en Ollama | Configurado en `MODEL_NAME` | Nombre del modelo LLM a usar |
| `temperature` | Float | ❌ No | 0.0 - 2.0 | 0.7 | Controla la aleatoriedad de las respuestas |
| `max_tokens` | Integer | ❌ No | 1 - 4096 | 2048 | Longitud máxima de la respuesta |
| `system_prompt` | String | ❌ No | - | "Eres un asistente útil." | Instrucciones del sistema |
| `use_knowledge_base` | Boolean | ❌ No | true/false | false | Activar RAG con base de conocimiento |
| `embedding_model` | String | ❌ No | - | `EMBEDDING_MODEL` configurado | Modelo para embeddings (si RAG activo) |
| `use_mongodb_tools` | Boolean | ❌ No | true/false | false | Activar herramientas de MongoDB |

### Estructura del Mensaje

```json
{
  "role": "user|assistant|system",
  "content": "texto del mensaje"
}
```

### Ejemplo de Petición Completa

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Eres un asistente técnico especializado"
    },
    {
      "role": "user",
      "content": "Explica qué es un webhook"
    }
  ],
  "model": "qwen3:14b",
  "temperature": 0.7,
  "max_tokens": 1024,
  "use_knowledge_base": false,
  "use_mongodb_tools": false
}
```

### Características Avanzadas

#### RAG (Retrieval-Augmented Generation)

Para usar la base de conocimiento vectorial:

```json
{
  "messages": [
    {"role": "user", "content": "¿Qué información hay sobre el tema X?"}
  ],
  "use_knowledge_base": true,
  "embedding_model": "qwen3-embedding:8b"
}
```

#### MongoDB Tools

Para consultas a bases de datos MongoDB:

```json
{
  "messages": [
    {"role": "user", "content": "¿Cuántos usuarios hay en la base de datos?"}
  ],
  "use_mongodb_tools": true
}
```

---

## Autenticación

### Configuración de API Key

**Variable de entorno**: `API_KEY`

Si `API_KEY` está configurada en el servidor, todas las peticiones deben incluir el header:

```
X-API-KEY: tu-clave-secreta-aqui
```

**Códigos de respuesta**:
- ✅ `200 OK`: Autenticación exitosa o no requerida
- ❌ `403 Forbidden`: API Key inválida o faltante

---

## Formato de Respuesta

### Streaming de Texto

La respuesta es un stream de texto plano (`text/plain`) que se envía token por token a medida que se genera.

**Content-Type**: `text/plain`

**Encoding**: UTF-8

**Flujo**: Continuo hasta completar la respuesta

### Lectura del Stream

El stream debe leerse usando `ReadableStream` o equivalente:

1. Obtener el reader del body de la respuesta
2. Leer chunks en un bucle hasta que `done` sea `true`
3. Decodificar cada chunk con `TextDecoder`
4. Procesar/mostrar el texto inmediatamente

---

## Ejemplos de Integración

### cURL

```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: tu-api-key" \
  -d '{
    "messages": [
      {"role": "user", "content": "Escribe un poema corto"}
    ],
    "model": "qwen3:14b",
    "temperature": 0.9
  }'
```

### Python

```python
import requests

url = "http://localhost:8000/chat/stream"
headers = {
    "Content-Type": "application/json",
    "X-API-KEY": "tu-api-key"
}
payload = {
    "messages": [
        {"role": "user", "content": "Explica la fotosíntesis"}
    ],
    "model": "qwen3:14b",
    "temperature": 0.7,
    "use_knowledge_base": False
}

response = requests.post(url, json=payload, headers=headers, stream=True)

# Procesar el stream
for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
    if chunk:
        print(chunk, end="", flush=True)
```

### JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

async function streamChat() {
  const response = await fetch('http://localhost:8000/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-KEY': 'tu-api-key'
    },
    body: JSON.stringify({
      messages: [
        { role: 'user', content: '¿Qué es la inteligencia artificial?' }
      ],
      model: 'qwen3:14b',
      temperature: 0.7
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    process.stdout.write(chunk);
  }
}

streamChat();
```

### JavaScript (Browser)

```javascript
async function chatWithStreaming(message) {
  const response = await fetch('http://localhost:8000/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-KEY': 'tu-api-key'
    },
    body: JSON.stringify({
      messages: [
        { role: 'user', content: message }
      ],
      model: 'qwen3:14b'
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullResponse = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    fullResponse += chunk;

    // Actualizar UI en tiempo real
    document.getElementById('output').textContent = fullResponse;
  }

  return fullResponse;
}
```

### Java

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;

public class StreamingClient {
    public static void main(String[] args) throws Exception {
        String payload = """
            {
                "messages": [
                    {"role": "user", "content": "Hola, ¿cómo estás?"}
                ],
                "model": "qwen3:14b"
            }
            """;

        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("http://localhost:8000/chat/stream"))
            .header("Content-Type", "application/json")
            .header("X-API-KEY", "tu-api-key")
            .POST(HttpRequest.BodyPublishers.ofString(payload))
            .build();

        HttpResponse<Stream<String>> response = client.send(
            request,
            HttpResponse.BodyHandlers.ofLines()
        );

        response.body().forEach(System.out::print);
    }
}
```

### Go

```go
package main

import (
    "bufio"
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

type Message struct {
    Role    string `json:"role"`
    Content string `json:"content"`
}

type ChatRequest struct {
    Messages    []Message `json:"messages"`
    Model       string    `json:"model"`
    Temperature float64   `json:"temperature"`
}

func main() {
    payload := ChatRequest{
        Messages: []Message{
            {Role: "user", Content: "Explica qué es Go"},
        },
        Model:       "qwen3:14b",
        Temperature: 0.7,
    }

    jsonData, _ := json.Marshal(payload)

    req, _ := http.NewRequest("POST", "http://localhost:8000/chat/stream", bytes.NewBuffer(jsonData))
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("X-API-KEY", "tu-api-key")

    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()

    scanner := bufio.NewScanner(resp.Body)
    for scanner.Scan() {
        fmt.Print(scanner.Text())
    }
}
```

---

## Manejo de Errores

### Códigos HTTP

| Código | Descripción | Causa Común |
|--------|-------------|-------------|
| `200` | OK | Petición exitosa |
| `400` | Bad Request | Mensaje demasiado largo o parámetros inválidos |
| `403` | Forbidden | API Key inválida o faltante |
| `500` | Internal Server Error | Error en el servidor o LLM |
| `503` | Service Unavailable | Ollama no está disponible |

### Formato de Error

```json
{
  "detail": "Descripción del error"
}
```

### Ejemplos de Errores

**Mensaje demasiado largo**:
```json
{
  "detail": "Message too long"
}
```

**Autenticación fallida**:
```json
{
  "detail": "Could not validate credentials"
}
```

**Conexión con Ollama fallida**:
```json
{
  "detail": "Could not connect to Ollama at http://localhost:11434"
}
```

---

## Configuración del Servidor

### Variables de Entorno

```bash
# URL de Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Modelo por defecto
MODEL_NAME=qwen3:14b

# Modelo de embeddings (para RAG)
EMBEDDING_MODEL=qwen3-embedding:8b

# Puerto del servidor API
PORT=8000

# Longitud máxima de entrada
MAX_INPUT_LENGTH=4096

# API Key (opcional)
API_KEY=tu-clave-secreta

# MongoDB (para herramientas de DB)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=mi_base_datos
```

---

## Limitaciones y Consideraciones

### Rendimiento

- El streaming es más eficiente para respuestas largas
- La latencia inicial depende del modelo y hardware
- Las peticiones son procesadas de forma asíncrona

### Límites

- Longitud máxima de entrada: configurable vía `MAX_INPUT_LENGTH` (por defecto 4096 caracteres)
- Longitud máxima de salida: configurable por petición vía `max_tokens` (por defecto 2048, máximo 4096)
- No hay rate limiting por defecto (implementar en producción si es necesario)

### Timeouts

Para respuestas largas, configurar timeouts apropiados en el cliente:

**Python**:
```python
response = requests.post(url, json=payload, stream=True, timeout=300)
```

**JavaScript**:
```javascript
const controller = new AbortController();
setTimeout(() => controller.abort(), 300000);

fetch(url, { signal: controller.signal, ... })
```

### Seguridad

- Usar HTTPS en producción
- Configurar API Key para proteger el endpoint
- Validar y sanitizar todas las entradas
- Implementar rate limiting en producción
- Configurar CORS apropiadamente si se accede desde navegadores

---

## Health Check

Para verificar que el servicio está disponible:

**Endpoint**: `GET /`

```bash
curl http://localhost:8000/
```

**Respuesta**:
```json
{
  "status": "ok",
  "service": "ChatGPT Local - Ollama API",
  "ollama_url": "http://ollama:11434",
  "default_model": "qwen3:14b"
}
```

---

## Soporte y Referencia

### Endpoints Relacionados

- `POST /chat` - Chat sin streaming (respuesta completa)
- `GET /models` - Listar modelos disponibles
- `GET /` - Health check

### Archivos de Referencia

- Backend: `app/api_server.py` (líneas 472-622)
- RAG Service: `app/rag_service.py`
- Configuración: `app/config.py`

### Documentación Adicional

- `API_EXAMPLES.md` - Ejemplos adicionales de uso
- `DOCUMENTACION_COMPLETA.md` - Documentación completa del sistema
- `README.md` - Guía de inicio rápido
