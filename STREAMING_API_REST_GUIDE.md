# Guía Técnica - API REST de Streaming

Documentación completa para integrar servicios externos con los endpoints de streaming del sistema LangChain Local LLM.

---

## 📋 Tabla de Contenidos

- [Información General](#información-general)
- [Endpoint de Streaming](#endpoint-de-streaming)
- [Parámetros de la Petición](#parámetros-de-la-petición)
- [Formato de Respuesta](#formato-de-respuesta)
- [Ejemplos de Código](#ejemplos-de-código)
- [Casos de Uso](#casos-de-uso)
- [Manejo de Errores](#manejo-de-errores)
- [Mejores Prácticas](#mejores-prácticas)

---

## 🌐 Información General

### URL Base
```
http://localhost:8000
```
_(Configurable mediante la variable de entorno `PORT`)_

### Autenticación

El API puede requerir autenticación mediante API Key:

**Header requerido:**
```http
X-API-KEY: tu_api_key_aqui
```

**Configuración:**
- Si `API_KEY` está configurada en `.env`, todas las peticiones deben incluir el header
- Si no está configurada, el acceso es libre (útil para desarrollo)

**Respuesta sin autenticación (cuando es requerida):**
```json
{
  "detail": "Could not validate credentials"
}
```
**Código HTTP:** `403 Forbidden`

---

## 🚀 Endpoint de Streaming

### `POST /chat/stream`

Endpoint principal para conversaciones con streaming en tiempo real.

| Propiedad | Valor |
|-----------|-------|
| **URL** | `http://localhost:8000/chat/stream` |
| **Método** | `POST` |
| **Content-Type** | `application/json` |
| **Response Type** | `text/plain` (streaming) |

---

## 📝 Parámetros de la Petición

### Estructura Completa

```json
{
  "messages": [
    {
      "role": "system|user|assistant",
      "content": "texto del mensaje"
    }
  ],
  "model": "llama3.2",
  "temperature": 0.7,
  "max_tokens": 2048,
  "system_prompt": "Eres un asistente útil.",
  "use_knowledge_base": false,
  "embedding_model": "nomic-embed-text",
  "use_mongodb_tools": false
}
```

### Descripción de Parámetros

| Parámetro | Tipo | Requerido | Rango/Valores | Por Defecto | Descripción |
|-----------|------|-----------|---------------|-------------|-------------|
| `messages` | Array | ✅ **Sí** | - | - | Lista de mensajes de la conversación |
| `model` | String | ❌ No | Cualquier modelo Ollama | `llama3.2` | Nombre del modelo LLM a utilizar |
| `temperature` | Float | ❌ No | 0.0 - 2.0 | 0.7 | Controla la creatividad (bajo=preciso, alto=creativo) |
| `max_tokens` | Integer | ❌ No | 1 - 4096 | 2048 | Longitud máxima de la respuesta |
| `system_prompt` | String | ❌ No | - | "Eres un asistente útil." | Instrucciones del sistema para el LLM |
| `use_knowledge_base` | Boolean | ❌ No | `true`/`false` | `false` | Activar RAG (búsqueda en documentos) |
| `embedding_model` | String | ❌ No | - | `nomic-embed-text` | Modelo de embeddings (solo si RAG activo) |
| `use_mongodb_tools` | Boolean | ❌ No | `true`/`false` | `false` | Activar herramientas de consulta MongoDB |

### Estructura del Array `messages`

Cada mensaje debe tener:

```json
{
  "role": "user|assistant|system",
  "content": "texto del mensaje"
}
```

**Roles disponibles:**
- `system`: Instrucciones para el asistente (opcional, al inicio)
- `user`: Mensaje del usuario
- `assistant`: Respuesta previa del asistente (para contexto)

**Ejemplo de conversación:**
```json
{
  "messages": [
    {
      "role": "system",
      "content": "Eres un experto en sandwiches. Responde siempre en español."
    },
    {
      "role": "user",
      "content": "¿Qué ingredientes necesito para un sandwich vegetariano?"
    },
    {
      "role": "assistant",
      "content": "Para un sandwich vegetariano básico necesitas: pan integral, lechuga, tomate, queso y mayonesa."
    },
    {
      "role": "user",
      "content": "¿Y si quiero algo más contundente?"
    }
  ]
}
```

---

## 📤 Formato de Respuesta

### Tipo de Respuesta

**Content-Type:** `text/plain`

**Formato:** Streaming de texto (Server-Sent Events compatible)

### Características del Stream

1. **Texto incremental**: Los chunks se envían conforme se generan
2. **Sin delimitadores**: El texto viene sin formato JSON
3. **Conexión persistente**: La respuesta se va escribiendo en tiempo real

### Ejemplo de Respuesta (conceptual)

```
Para
 un
 sandwich
 vegetariano
 contundente
,
 puedes
 agregar
...
```

_(Los espacios y saltos son representación visual; el stream real es continuo)_

### Indicadores Especiales

Cuando `use_mongodb_tools: true`, puedes recibir indicadores:

```
[Utilizando herramienta: mongodb_find]...
Encontré 5 pedidos en tu historial...
```

---

## 💻 Ejemplos de Código

### 1. Python (requests + streaming)

```python
import requests
import json

url = "http://localhost:8000/chat/stream"
headers = {
    "Content-Type": "application/json",
    "X-API-KEY": "tu_api_key"  # Opcional
}

payload = {
    "messages": [
        {
            "role": "user",
            "content": "Dame una receta rápida de pasta"
        }
    ],
    "model": "llama3.2",
    "temperature": 0.7,
    "max_tokens": 512
}

# Streaming de la respuesta
response = requests.post(url, headers=headers, json=payload, stream=True)

if response.status_code == 200:
    print("Respuesta del LLM:")
    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        if chunk:
            print(chunk, end='', flush=True)
    print()  # Nueva línea al final
else:
    print(f"Error {response.status_code}: {response.text}")
```

### 2. JavaScript/Node.js (fetch)

```javascript
const url = "http://localhost:8000/chat/stream";

const payload = {
  messages: [
    {
      role: "user",
      content: "¿Qué tiempo hará mañana?"
    }
  ],
  model: "llama3.2",
  temperature: 0.5
};

const headers = {
  "Content-Type": "application/json",
  "X-API-KEY": "tu_api_key"  // Opcional
};

async function streamChat() {
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: headers,
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      process.stdout.write(chunk);  // Imprime incrementalmente
    }

    console.log('\n');
  } catch (error) {
    console.error("Error:", error.message);
  }
}

streamChat();
```

### 3. cURL (Línea de comandos)

```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: tu_api_key" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Explica qué es Docker en 3 frases"
      }
    ],
    "model": "llama3.2",
    "temperature": 0.3,
    "max_tokens": 200
  }' \
  --no-buffer
```

**Nota:** `--no-buffer` es crucial para ver el streaming en tiempo real.

### 4. JavaScript/Browser (React)

```jsx
import { useState } from 'react';

function ChatComponent() {
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async (userMessage) => {
    setLoading(true);
    setResponse('');

    try {
      const res = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-KEY': 'tu_api_key'
        },
        body: JSON.stringify({
          messages: [
            { role: 'user', content: userMessage }
          ],
          model: 'llama3.2',
          temperature: 0.7
        })
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        setResponse(prev => prev + chunk);  // Actualiza incrementalmente
      }
    } catch (error) {
      console.error('Error:', error);
      setResponse('Error al comunicarse con el API');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={() => sendMessage('Hola')}>
        Enviar mensaje
      </button>
      <div className="response">
        {loading && !response && <span>Pensando...</span>}
        <pre>{response}</pre>
      </div>
    </div>
  );
}
```

---

## 🎯 Casos de Uso

### 1. Chat Simple (sin RAG, sin Tools)

**Caso:** Conversación general con el LLM

```json
{
  "messages": [
    {
      "role": "user",
      "content": "¿Cuál es la capital de Francia?"
    }
  ],
  "model": "llama3.2",
  "temperature": 0.3
}
```

**Respuesta esperada:**
```
La capital de Francia es París.
```

---

### 2. Chat con System Prompt Personalizado

**Caso:** Asistente especializado (ej: recomendador de sandwiches)

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Sorpréndeme con algo ligero"
    }
  ],
  "model": "llama3.2",
  "temperature": 0.7,
  "system_prompt": "Actúa como un asistente inteligente de recomendaciones de sandwiches. Eres conversacional, cercano y breve. Solo recomiendas ingredientes disponibles en el catálogo: pollo, jamón, queso, lechuga, tomate, atún. Máximo 2-3 frases por respuesta."
}
```

**Respuesta esperada:**
```
Te sugiero un sandwich de atún con lechuga y tomate. Es fresco, saludable y muy sabroso. ¿Te animas?
```

---

### 3. Chat con RAG (Base de Conocimiento)

**Caso:** Consultas sobre documentos ingresados

**Requisito previo:** Ingerir documentos usando `POST /ingest`

```json
{
  "messages": [
    {
      "role": "user",
      "content": "¿Qué ingredientes picantes tenemos disponibles?"
    }
  ],
  "model": "llama3.2",
  "use_knowledge_base": true,
  "embedding_model": "nomic-embed-text"
}
```

**Respuesta esperada:**
```
Según el catálogo disponible, los ingredientes picantes son:
- Jalapeños
- Salsa picante
- Pimientos rojos

¿Te gustaría alguno en tu sandwich?
```

---

### 4. Chat con MongoDB Tools

**Caso:** Consultas sobre datos en MongoDB

**Requisito previo:** Configurar MongoDB en `.env`

```json
{
  "messages": [
    {
      "role": "user",
      "content": "¿Cuántos pedidos hice este mes?"
    }
  ],
  "model": "llama3.2",
  "use_mongodb_tools": true
}
```

**Respuesta esperada:**
```
[Utilizando herramienta: mongodb_count]...
Has realizado 12 pedidos este mes.
```

---

### 5. Conversación Multi-turno

**Caso:** Mantener contexto entre mensajes

```json
{
  "messages": [
    {
      "role": "user",
      "content": "¿Qué es Python?"
    },
    {
      "role": "assistant",
      "content": "Python es un lenguaje de programación interpretado, de alto nivel y uso general."
    },
    {
      "role": "user",
      "content": "¿Para qué se usa principalmente?"
    }
  ],
  "model": "llama3.2"
}
```

**Respuesta esperada:**
```
Python se usa principalmente para desarrollo web, ciencia de datos, automatización, inteligencia artificial y scripting.
```

---

## ⚠️ Manejo de Errores

### Códigos de Estado HTTP

| Código | Significado | Causa Común |
|--------|-------------|-------------|
| `200` | OK | Petición exitosa |
| `400` | Bad Request | Parámetros inválidos, mensaje demasiado largo |
| `403` | Forbidden | API Key incorrecta o faltante |
| `500` | Internal Server Error | Error del LLM o servidor |

### Ejemplo de Error (400 Bad Request)

**Petición:**
```json
{
  "messages": [
    {
      "role": "invalid_role",
      "content": "Test"
    }
  ]
}
```

**Respuesta:**
```json
{
  "detail": "Invalid role. Must be 'user', 'assistant', or 'system'"
}
```

### Ejemplo de Error (500 Internal Server Error)

**Causa:** Modelo no disponible en Ollama

**Respuesta:**
```
Error: Model 'gpt-4' not found. Available models: llama3.2, qwen3
```

### Validaciones Automáticas

1. **Longitud de mensaje**: Máximo `MAX_INPUT_LENGTH` caracteres (configurable)
   ```json
   {
     "detail": "Message too long"
   }
   ```

2. **RAG con mensaje no-user**: Si `use_knowledge_base: true`, el último mensaje debe ser `role: user`
   ```
   Error: Last message must be from user for RAG.
   ```

---

## ✅ Mejores Prácticas

### 1. Manejo de Streaming

- **Procesa chunks incrementalmente**: No esperes a que termine toda la respuesta
- **Usa decodificadores apropiados**: UTF-8 para español/caracteres especiales
- **Implementa timeout**: Conexiones largas pueden perderse

### 2. Optimización de Parámetros

| Caso de Uso | `temperature` | `max_tokens` |
|-------------|---------------|--------------|
| Respuestas precisas (ej: datos) | 0.1 - 0.3 | 256 - 512 |
| Conversación natural | 0.5 - 0.8 | 512 - 1024 |
| Creatividad (ej: recetas) | 0.8 - 1.2 | 1024 - 2048 |

### 3. Gestión de Contexto

- **Limita el historial**: Envía solo los últimos 5-10 mensajes para evitar timeouts
- **Usa system prompt**: Define el comportamiento global del asistente
- **Formato de mensajes**: Siempre incluye `role` y `content`

### 4. Seguridad

- **Nunca expongas API Keys**: Usa variables de entorno o secretos
- **Valida input del usuario**: Sanitiza antes de enviar al LLM
- **Limita max_tokens**: Evita respuestas excesivamente largas

### 5. Rendimiento

- **Cache de modelos**: Los modelos Ollama se cargan en memoria (1er request lento)
- **Usa embedding model adecuado**: `nomic-embed-text` es rápido y preciso
- **Conexiones persistentes**: Reutiliza conexiones HTTP cuando sea posible

---

## 🔍 Endpoints Auxiliares

### Listar Modelos Disponibles

```bash
GET /models
```

**Respuesta:**
```json
{
  "models": [
    {
      "name": "llama3.2",
      "size": 4700000000,
      "modified_at": "2024-01-15T10:30:00Z"
    },
    {
      "name": "qwen3:14b",
      "size": 14000000000,
      "modified_at": "2024-01-10T15:20:00Z"
    }
  ]
}
```

### Verificar Estado de MongoDB

```bash
GET /mongodb/status
```

**Respuesta:**
```json
{
  "available": true,
  "connected": true,
  "database": "sandwiches_db",
  "collections": ["pedidos", "usuarios"],
  "tools_count": 4
}
```

---

## 📚 Recursos Adicionales

- **Ollama Models**: https://ollama.com/library
- **LangChain Docs**: https://python.langchain.com/docs/
- **FastAPI Streaming**: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse

---

## 📞 Soporte

Para reportar problemas o solicitar features:
- **Issues**: https://github.com/tu-repo/issues
- **Documentación Backend**: Ver `/app/api_server.py`

---

## 📄 Licencia

Este documento es parte del proyecto LangChain Local LLM.

---

**Última actualización:** 2026-01-17
**Versión del API:** 1.0.0
