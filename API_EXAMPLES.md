# Ejemplos de Uso de la API

Este documento contiene ejemplos prácticos de cómo usar la API de ChatGPT Local con diferentes herramientas.

## Contenido

- [cURL](#curl)
- [Python](#python)
- [JavaScript/Fetch](#javascriptfetch)
- [PowerShell](#powershell)

---

## cURL

### 1. Health Check

```bash
curl http://localhost:8000/
```

**Respuesta:**
```json
{
  "status": "ok",
  "service": "ChatGPT Local - Ollama API",
  "ollama_url": "http://ollama:11434",
  "default_model": "llama3.2"
}
```

### 2. Listar Modelos

```bash
curl http://localhost:8000/models
```

**Respuesta:**
```json
{
  "models": [
    {
      "name": "llama3.2",
      "size": "2GB",
      "modified_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 3. Chat Simple (Sin Streaming)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "¿Cuál es la capital de Francia?"}
    ],
    "model": "llama3.2",
    "temperature": 0.7,
    "max_tokens": 512
  }'
```

**Respuesta:**
```json
{
  "response": "La capital de Francia es París.",
  "model": "llama3.2"
}
```

### 4. Chat con Historial

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "Eres un asistente experto en geografía."},
      {"role": "user", "content": "¿Cuál es la capital de Francia?"},
      {"role": "assistant", "content": "La capital de Francia es París."},
      {"role": "user", "content": "¿Y cuántos habitantes tiene?"}
    ],
    "model": "llama3.2",
    "temperature": 0.7
  }'
```

### 5. Chat con Streaming

```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Escribe un poema corto sobre la naturaleza"}
    ],
    "model": "llama3.2",
    "temperature": 0.9
  }'
```

**Respuesta (streaming):**
```
Entre árboles verdes
y flores de colores...
(texto continúa llegando token por token)
```

### 6. Parámetros Avanzados

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explica la teoría de la relatividad"}
    ],
    "model": "llama3.2",
    "temperature": 0.3,
    "max_tokens": 1024,
    "system_prompt": "Eres un profesor de física que explica conceptos complejos de forma simple."
  }'
```

---

## Python

### Instalación

```bash
pip install requests
```

### 1. Chat Simple

```python
import requests

url = "http://localhost:8000/chat"

payload = {
    "messages": [
        {"role": "user", "content": "¿Qué es Python?"}
    ],
    "model": "llama3.2",
    "temperature": 0.7,
    "max_tokens": 512
}

response = requests.post(url, json=payload)
result = response.json()

print(result["response"])
```

### 2. Chat con Streaming

```python
import requests
import json

url = "http://localhost:8000/chat/stream"

payload = {
    "messages": [
        {"role": "user", "content": "Cuenta hasta 10"}
    ],
    "model": "llama3.2"
}

response = requests.post(url, json=payload, stream=True)

print("Respuesta: ", end="", flush=True)
for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
    if chunk:
        print(chunk, end="", flush=True)
print()
```

### 3. Gestión de Conversaciones

```python
import requests

class ChatClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.messages = []

    def send_message(self, content, stream=False):
        self.messages.append({"role": "user", "content": content})

        endpoint = "/chat/stream" if stream else "/chat"
        url = f"{self.base_url}{endpoint}"

        payload = {
            "messages": self.messages,
            "model": "llama3.2",
            "temperature": 0.7
        }

        if stream:
            response = requests.post(url, json=payload, stream=True)
            full_response = ""
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    print(chunk, end="", flush=True)
                    full_response += chunk
            print()
            self.messages.append({"role": "assistant", "content": full_response})
            return full_response
        else:
            response = requests.post(url, json=payload)
            result = response.json()
            self.messages.append({"role": "assistant", "content": result["response"]})
            return result["response"]

    def clear_history(self):
        self.messages = []

# Uso
chat = ChatClient()
chat.send_message("Hola, ¿cómo estás?")
chat.send_message("¿Cuál es la capital de España?")
```

### 4. Listar Modelos

```python
import requests

url = "http://localhost:8000/models"
response = requests.get(url)
models = response.json()

print("Modelos disponibles:")
for model in models.get("models", []):
    print(f"- {model['name']}")
```

---

## JavaScript/Fetch

### 1. Chat Simple

```javascript
async function chat(message) {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages: [
        { role: 'user', content: message }
      ],
      model: 'llama3.2',
      temperature: 0.7,
      max_tokens: 512
    })
  });

  const data = await response.json();
  return data.response;
}

// Uso
chat('¿Qué es JavaScript?')
  .then(response => console.log(response))
  .catch(error => console.error('Error:', error));
```

### 2. Chat con Streaming

```javascript
async function chatStream(message) {
  const response = await fetch('http://localhost:8000/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages: [
        { role: 'user', content: message }
      ],
      model: 'llama3.2'
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    console.log(chunk);
  }
}

// Uso
chatStream('Escribe un poema corto');
```

### 3. Clase de Chat Completa

```javascript
class ChatClient {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.messages = [];
  }

  async sendMessage(content, options = {}) {
    const { stream = false, model = 'llama3.2', temperature = 0.7 } = options;

    this.messages.push({ role: 'user', content });

    const endpoint = stream ? '/chat/stream' : '/chat';
    const url = `${this.baseURL}${endpoint}`;

    const payload = {
      messages: this.messages,
      model,
      temperature
    };

    if (stream) {
      return this.handleStream(url, payload);
    } else {
      return this.handleRegular(url, payload);
    }
  }

  async handleRegular(url, payload) {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    this.messages.push({ role: 'assistant', content: data.response });
    return data.response;
  }

  async handleStream(url, payload) {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullResponse = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      fullResponse += chunk;
      console.log(chunk);
    }

    this.messages.push({ role: 'assistant', content: fullResponse });
    return fullResponse;
  }

  clearHistory() {
    this.messages = [];
  }
}

// Uso
const chat = new ChatClient();
await chat.sendMessage('Hola');
await chat.sendMessage('¿Cómo funciona un ordenador?', { stream: true });
```

---

## PowerShell

### 1. Chat Simple

```powershell
$body = @{
    messages = @(
        @{
            role = "user"
            content = "¿Qué es PowerShell?"
        }
    )
    model = "llama3.2"
    temperature = 0.7
    max_tokens = 512
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"

Write-Output $response.response
```

### 2. Listar Modelos

```powershell
$models = Invoke-RestMethod -Uri "http://localhost:8000/models" -Method Get

Write-Output "Modelos disponibles:"
foreach ($model in $models.models) {
    Write-Output "- $($model.name)"
}
```

### 3. Chat con Historial

```powershell
$messages = @(
    @{ role = "user"; content = "Hola" },
    @{ role = "assistant"; content = "Hola, ¿cómo puedo ayudarte?" },
    @{ role = "user"; content = "¿Qué hora es?" }
)

$body = @{
    messages = $messages
    model = "llama3.2"
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"

Write-Output $response.response
```

### 4. Función de Chat Reutilizable

```powershell
function Send-ChatMessage {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,

        [string]$Model = "llama3.2",
        [double]$Temperature = 0.7,
        [int]$MaxTokens = 512,
        [string]$BaseUrl = "http://localhost:8000"
    )

    $body = @{
        messages = @(
            @{
                role = "user"
                content = $Message
            }
        )
        model = $Model
        temperature = $Temperature
        max_tokens = $MaxTokens
    } | ConvertTo-Json -Depth 10

    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/chat" -Method Post -Body $body -ContentType "application/json"
        return $response.response
    }
    catch {
        Write-Error "Error al enviar mensaje: $_"
        return $null
    }
}

# Uso
$respuesta = Send-ChatMessage -Message "¿Qué es la inteligencia artificial?"
Write-Output $respuesta
```

---

## Notas Adicionales

### Manejo de Errores

Todos los endpoints pueden devolver errores. Ejemplo:

```json
{
  "detail": "Message too long"
}
```

Códigos de estado comunes:
- `200`: Éxito
- `400`: Request inválido
- `500`: Error del servidor
- `503`: Ollama no disponible

### Timeouts

Para conversaciones largas, considera aumentar el timeout:

**Python:**
```python
response = requests.post(url, json=payload, timeout=300)  # 5 minutos
```

**JavaScript:**
```javascript
const controller = new AbortController();
setTimeout(() => controller.abort(), 300000);  // 5 minutos

fetch(url, { signal: controller.signal })
```

### Rate Limiting

No hay rate limiting por defecto, pero puedes implementarlo editando `app/api_server.py`.
