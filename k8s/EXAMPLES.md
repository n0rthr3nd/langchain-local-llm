# Ejemplos de Uso desde Otros Servicios

Esta guía muestra cómo otros servicios en tu cluster k3s pueden consumir la API de LangChain + Ollama.

---

## 📋 Tabla de Contenidos

1. [Acceso Básico](#acceso-básico)
2. [Desde Python](#desde-python)
3. [Desde Node.js](#desde-nodejs)
4. [Desde Go](#desde-go)
5. [Desde un Pod Genérico](#desde-un-pod-genérico)
6. [Integración con Otros Servicios](#integración-con-otros-servicios)

---

## 🔗 Acceso Básico

### URL del Servicio

Todos los servicios dentro del cluster pueden acceder a:

```
http://langchain-api.llm-services.svc.cluster.local:8000
```

O la forma corta (desde el mismo namespace):

```
http://langchain-api:8000
```

### Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/models` | GET | Lista modelos disponibles |
| `/chat` | POST | Chat sin streaming |
| `/chat/stream` | POST | Chat con streaming |
| `/analyze` | POST | Análisis de texto |

---

## 🐍 Desde Python

### Deployment de Ejemplo

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mi-app-python
  namespace: mi-namespace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mi-app-python
  template:
    metadata:
      labels:
        app: mi-app-python
    spec:
      containers:
      - name: app
        image: python:3.11-slim
        env:
        - name: LLM_API_URL
          value: "http://langchain-api.llm-services.svc.cluster.local:8000"
        command: ["python", "app.py"]
```

### Código Python

```python
#!/usr/bin/env python3
"""
Ejemplo de cliente Python para LangChain API en k8s
"""
import os
import httpx
import asyncio
from typing import List, Dict

# URL del servicio en k8s
LLM_API_URL = os.getenv(
    "LLM_API_URL",
    "http://langchain-api.llm-services.svc.cluster.local:8000"
)


async def chat(messages: List[Dict[str, str]], model: str = "gemma2:2b"):
    """Enviar mensaje al LLM (sin streaming)"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{LLM_API_URL}/chat",
            json={
                "messages": messages,
                "model": model,
                "temperature": 0.7,
                "max_tokens": 512
            }
        )
        response.raise_for_status()
        return response.json()


async def chat_stream(messages: List[Dict[str, str]], model: str = "gemma2:2b"):
    """Enviar mensaje al LLM (con streaming)"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{LLM_API_URL}/chat/stream",
            json={
                "messages": messages,
                "model": model,
                "temperature": 0.7
            }
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_text():
                yield chunk


async def list_models():
    """Listar modelos disponibles"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{LLM_API_URL}/models")
        response.raise_for_status()
        return response.json()


async def main():
    # Ejemplo 1: Chat simple
    print("=== Chat Simple ===")
    result = await chat([
        {"role": "user", "content": "¿Qué es Kubernetes en 2 oraciones?"}
    ])
    print(f"Respuesta: {result['response']}\n")

    # Ejemplo 2: Chat con contexto
    print("=== Chat con Contexto ===")
    conversation = [
        {"role": "user", "content": "Mi nombre es Carlos"},
        {"role": "assistant", "content": "Hola Carlos, ¿en qué puedo ayudarte?"},
        {"role": "user", "content": "¿Recuerdas mi nombre?"}
    ]
    result = await chat(conversation)
    print(f"Respuesta: {result['response']}\n")

    # Ejemplo 3: Streaming
    print("=== Chat con Streaming ===")
    messages = [{"role": "user", "content": "Cuenta del 1 al 5"}]
    async for chunk in chat_stream(messages):
        print(chunk, end="", flush=True)
    print("\n")

    # Ejemplo 4: Listar modelos
    print("=== Modelos Disponibles ===")
    models = await list_models()
    for model in models.get("models", []):
        print(f"  - {model.get('name')}")


if __name__ == "__main__":
    asyncio.run(main())
```

### requirements.txt

```txt
httpx>=0.26.0
asyncio
```

---

## 🟢 Desde Node.js

### Deployment de Ejemplo

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mi-app-nodejs
  namespace: mi-namespace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mi-app-nodejs
  template:
    metadata:
      labels:
        app: mi-app-nodejs
    spec:
      containers:
      - name: app
        image: node:20-alpine
        env:
        - name: LLM_API_URL
          value: "http://langchain-api.llm-services.svc.cluster.local:8000"
        command: ["node", "app.js"]
```

### Código Node.js

```javascript
/**
 * Ejemplo de cliente Node.js para LangChain API en k8s
 */
const axios = require('axios');

const LLM_API_URL = process.env.LLM_API_URL ||
  'http://langchain-api.llm-services.svc.cluster.local:8000';

/**
 * Enviar mensaje al LLM (sin streaming)
 */
async function chat(messages, model = 'gemma2:2b') {
  try {
    const response = await axios.post(`${LLM_API_URL}/chat`, {
      messages,
      model,
      temperature: 0.7,
      max_tokens: 512
    }, {
      timeout: 120000 // 2 minutos
    });

    return response.data;
  } catch (error) {
    console.error('Error en chat:', error.message);
    throw error;
  }
}

/**
 * Chat con streaming
 */
async function chatStream(messages, model = 'gemma2:2b') {
  try {
    const response = await axios.post(
      `${LLM_API_URL}/chat/stream`,
      {
        messages,
        model,
        temperature: 0.7
      },
      {
        responseType: 'stream',
        timeout: 120000
      }
    );

    return response.data;
  } catch (error) {
    console.error('Error en chat stream:', error.message);
    throw error;
  }
}

/**
 * Listar modelos disponibles
 */
async function listModels() {
  try {
    const response = await axios.get(`${LLM_API_URL}/models`);
    return response.data;
  } catch (error) {
    console.error('Error listando modelos:', error.message);
    throw error;
  }
}

// Ejemplos de uso
async function main() {
  // Ejemplo 1: Chat simple
  console.log('=== Chat Simple ===');
  const result1 = await chat([
    { role: 'user', content: '¿Qué es Kubernetes en 2 oraciones?' }
  ]);
  console.log('Respuesta:', result1.response);
  console.log();

  // Ejemplo 2: Chat con contexto
  console.log('=== Chat con Contexto ===');
  const conversation = [
    { role: 'user', content: 'Mi nombre es Carlos' },
    { role: 'assistant', content: 'Hola Carlos, ¿en qué puedo ayudarte?' },
    { role: 'user', content: '¿Recuerdas mi nombre?' }
  ];
  const result2 = await chat(conversation);
  console.log('Respuesta:', result2.response);
  console.log();

  // Ejemplo 3: Streaming
  console.log('=== Chat con Streaming ===');
  const stream = await chatStream([
    { role: 'user', content: 'Cuenta del 1 al 5' }
  ]);

  stream.on('data', (chunk) => {
    process.stdout.write(chunk.toString());
  });

  stream.on('end', async () => {
    console.log('\n');

    // Ejemplo 4: Listar modelos
    console.log('=== Modelos Disponibles ===');
    const models = await listModels();
    models.models?.forEach(model => {
      console.log(`  - ${model.name}`);
    });
  });
}

main().catch(console.error);
```

### package.json

```json
{
  "dependencies": {
    "axios": "^1.6.0"
  }
}
```

---

## 🔵 Desde Go

### Deployment de Ejemplo

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mi-app-go
  namespace: mi-namespace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mi-app-go
  template:
    metadata:
      labels:
        app: mi-app-go
    spec:
      containers:
      - name: app
        image: golang:1.21-alpine
        env:
        - name: LLM_API_URL
          value: "http://langchain-api.llm-services.svc.cluster.local:8000"
        command: ["go", "run", "main.go"]
```

### Código Go

```go
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

const defaultAPIURL = "http://langchain-api.llm-services.svc.cluster.local:8000"

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatRequest struct {
	Messages    []Message `json:"messages"`
	Model       string    `json:"model,omitempty"`
	Temperature float64   `json:"temperature,omitempty"`
	MaxTokens   int       `json:"max_tokens,omitempty"`
}

type ChatResponse struct {
	Response string `json:"response"`
	Model    string `json:"model"`
}

type LLMClient struct {
	BaseURL string
	Client  *http.Client
}

func NewLLMClient() *LLMClient {
	baseURL := os.Getenv("LLM_API_URL")
	if baseURL == "" {
		baseURL = defaultAPIURL
	}

	return &LLMClient{
		BaseURL: baseURL,
		Client: &http.Client{
			Timeout: 120 * time.Second,
		},
	}
}

func (c *LLMClient) Chat(messages []Message, model string) (*ChatResponse, error) {
	if model == "" {
		model = "gemma2:2b"
	}

	reqBody := ChatRequest{
		Messages:    messages,
		Model:       model,
		Temperature: 0.7,
		MaxTokens:   512,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("error marshaling request: %w", err)
	}

	resp, err := c.Client.Post(
		c.BaseURL+"/chat",
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return nil, fmt.Errorf("error making request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(body))
	}

	var chatResp ChatResponse
	if err := json.NewDecoder(resp.Body).Decode(&chatResp); err != nil {
		return nil, fmt.Errorf("error decoding response: %w", err)
	}

	return &chatResp, nil
}

func (c *LLMClient) ListModels() (map[string]interface{}, error) {
	resp, err := c.Client.Get(c.BaseURL + "/models")
	if err != nil {
		return nil, fmt.Errorf("error making request: %w", err)
	}
	defer resp.Body.Close()

	var models map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&models); err != nil {
		return nil, fmt.Errorf("error decoding response: %w", err)
	}

	return models, nil
}

func main() {
	client := NewLLMClient()

	// Ejemplo 1: Chat simple
	fmt.Println("=== Chat Simple ===")
	messages := []Message{
		{Role: "user", Content: "¿Qué es Kubernetes en 2 oraciones?"},
	}

	result, err := client.Chat(messages, "gemma2:2b")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}

	fmt.Printf("Respuesta: %s\n\n", result.Response)

	// Ejemplo 2: Listar modelos
	fmt.Println("=== Modelos Disponibles ===")
	models, err := client.ListModels()
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}

	fmt.Printf("Modelos: %+v\n", models)
}
```

---

## 🐳 Desde un Pod Genérico

### Pod de Debug

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: llm-client-debug
  namespace: mi-namespace
spec:
  containers:
  - name: curl
    image: curlimages/curl:latest
    command: ["/bin/sh", "-c", "sleep 3600"]
    env:
    - name: LLM_API
      value: "http://langchain-api.llm-services.svc.cluster.local:8000"
```

### Comandos desde el Pod

```bash
# Entrar al pod
kubectl exec -it llm-client-debug -n mi-namespace -- sh

# Health check
curl $LLM_API/

# Listar modelos
curl $LLM_API/models

# Chat simple
curl -X POST $LLM_API/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hola, ¿cómo estás?"}
    ],
    "model": "gemma2:2b"
  }'

# Chat con streaming
curl -X POST $LLM_API/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Cuenta del 1 al 10"}
    ]
  }'
```

---

## 🔗 Integración con Otros Servicios

### 1. Como Sidecar Container

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mi-app-con-llm
spec:
  template:
    spec:
      containers:
      # Contenedor principal
      - name: app
        image: mi-app:latest
        env:
        - name: LLM_API_URL
          value: "http://localhost:8080"  # Proxy local

      # Sidecar proxy para LLM
      - name: llm-proxy
        image: nginx:alpine
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/nginx.conf
          subPath: nginx.conf

      volumes:
      - name: nginx-config
        configMap:
          name: llm-proxy-config

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: llm-proxy-config
data:
  nginx.conf: |
    events {}
    http {
      server {
        listen 8080;
        location / {
          proxy_pass http://langchain-api.llm-services.svc.cluster.local:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
        }
      }
    }
```

### 2. Con Service Mesh (Istio/Linkerd)

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: llm-api-route
spec:
  hosts:
  - langchain-api.llm-services.svc.cluster.local
  http:
  - timeout: 120s
    retries:
      attempts: 3
      perTryTimeout: 40s
    route:
    - destination:
        host: langchain-api.llm-services.svc.cluster.local
        port:
          number: 8000
```

### 3. Con ConfigMap de Configuración

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: mi-namespace
data:
  config.yaml: |
    llm:
      api_url: http://langchain-api.llm-services.svc.cluster.local:8000
      default_model: gemma2:2b
      timeout: 120
      max_retries: 3
```

---

## 🔐 Autenticación y Seguridad

### Opción 1: NetworkPolicy (Ya incluida)

```yaml
# La NetworkPolicy ya permite tráfico desde cualquier namespace
# Si quieres restringir, modifica k8s/base/networkpolicy.yaml
```

### Opción 2: API Key (implementación futura)

```python
# En tu servicio cliente
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.post(
    f"{LLM_API_URL}/chat",
    json=payload,
    headers=headers
)
```

---

## 📊 Métricas y Logging

### Instrumentar tu Cliente

```python
import logging
from prometheus_client import Counter, Histogram

# Métricas
llm_requests = Counter('llm_requests_total', 'Total LLM requests')
llm_latency = Histogram('llm_request_duration_seconds', 'LLM request latency')

async def chat_with_metrics(messages):
    llm_requests.inc()

    with llm_latency.time():
        result = await chat(messages)

    logging.info(f"LLM request completed: {len(result['response'])} chars")
    return result
```

---

## ✅ Checklist de Integración

- [ ] Servicio desplegado en k3s
- [ ] Variable de entorno `LLM_API_URL` configurada
- [ ] NetworkPolicy permite tráfico desde tu namespace
- [ ] Timeout configurado (>60s para streaming)
- [ ] Manejo de errores implementado
- [ ] Logging configurado
- [ ] Métricas (opcional pero recomendado)

---

**¿Necesitas más ejemplos?** Crea un issue en el repositorio.
