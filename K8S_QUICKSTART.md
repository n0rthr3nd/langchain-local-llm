# 🚀 Quick Start - Despliegue en k3s

Guía rápida de 5 minutos para desplegar LangChain + Ollama en tu cluster k3s.

---

## ✅ Pre-requisitos

```bash
# Verificar que tienes k3s funcionando
kubectl get nodes

# Verificar espacio disponible (necesitas ~20GB)
df -h

# Verificar RAM disponible (recomendado 8GB)
free -h
```

---

## 📦 Instalación en 4 Pasos

### 1. Construir e Importar Imagen

```bash
cd /home/ecanals/ws/langchain-local-llm
./k8s/scripts/build-and-push.sh
```

**Tiempo:** ~3-5 minutos (depende de la conexión para descargar dependencias)

---

### 2. Desplegar Servicios

```bash
./k8s/scripts/deploy.sh
```

**Tiempo:** ~1-2 minutos

**Qué hace:**
- ✅ Crea namespace `llm-services`
- ✅ Despliega Ollama (StatefulSet)
- ✅ Despliega LangChain API (Deployment con 2 réplicas)
- ✅ Configura Services, Ingress y NetworkPolicies
- ✅ Configura auto-scaling (HPA)

---

### 3. Descargar Modelos LLM

```bash
kubectl apply -f k8s/base/model-download-job.yaml
kubectl logs -n llm-services job/model-download -f
```

**Tiempo:** ~5-10 minutos (depende de tu conexión)

**Modelos descargados:**
- `gemma2:2b` (2.7GB) - Modelo principal
- `nomic-embed-text` (274MB) - Para embeddings/RAG

---

### 4. Verificar y Probar

```bash
# Ver estado de los pods
kubectl get pods -n llm-services

# Deberías ver:
# - ollama-0 (Running)
# - langchain-api-xxx (Running, 2 réplicas)

# Probar la API
kubectl run -it --rm test --image=curlimages/curl --restart=Never -- \
  curl -X POST http://langchain-api.llm-services.svc.cluster.local:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hola"}]}'
```

**¡Listo! ✅**

---

## 🌐 Acceso a la API

### Opción A: Desde Otros Pods (recomendado)

```bash
# URL del servicio
http://langchain-api.llm-services.svc.cluster.local:8000
```

Ver ejemplos completos en: [k8s/EXAMPLES.md](k8s/EXAMPLES.md)

### Opción B: Via Ingress (acceso externo)

```bash
# 1. Añadir a /etc/hosts
echo "192.168.1.X  llm-api.local" | sudo tee -a /etc/hosts

# 2. Probar
curl http://llm-api.local/
```

### Opción C: Port-Forward (desarrollo)

```bash
kubectl port-forward -n llm-services svc/langchain-api 8000:8000

# En otra terminal
curl http://localhost:8000/
```

---

## 📊 Monitoreo Básico

```bash
# Ver pods y su estado
kubectl get pods -n llm-services

# Ver uso de recursos
kubectl top pods -n llm-services

# Ver logs en tiempo real
kubectl logs -f -n llm-services -l app=langchain-api

# Ver todos los servicios
kubectl get all -n llm-services
```

---

## 🔧 Comandos Útiles

### Gestión de Modelos

```bash
# Listar modelos instalados
kubectl exec -n llm-services ollama-0 -- ollama list

# Descargar modelo adicional
kubectl exec -n llm-services ollama-0 -- ollama pull phi3:mini

# Ver espacio usado
kubectl exec -n llm-services ollama-0 -- du -sh /root/.ollama
```

### Escalar API

```bash
# Escalar a 3 réplicas
kubectl scale deployment/langchain-api --replicas=3 -n llm-services

# Ver estado
kubectl get pods -n llm-services -l app=langchain-api
```

### Reiniciar Servicios

```bash
# Reiniciar Ollama
kubectl rollout restart statefulset/ollama -n llm-services

# Reiniciar API
kubectl rollout restart deployment/langchain-api -n llm-services
```

### Ver Logs

```bash
# Logs de Ollama
kubectl logs -n llm-services ollama-0 -f

# Logs de la API (todas las réplicas)
kubectl logs -n llm-services -l app=langchain-api -f --max-log-requests=10

# Logs de un pod específico
kubectl logs -n llm-services <nombre-pod> -f
```

---

## 🧹 Desinstalar

```bash
# Opción 1: Conservar modelos descargados
./k8s/scripts/undeploy.sh
# Responder 'n' cuando pregunte por PVC

# Opción 2: Eliminar todo (incluyendo modelos)
./k8s/scripts/undeploy.sh
# Responder 's' a todas las preguntas
```

---

## 🐛 Troubleshooting Rápido

### Pods en Pending

```bash
# Ver razón
kubectl describe pod <pod-name> -n llm-services

# Causa común: RAM insuficiente
kubectl top nodes
```

**Solución:** Reducir límites de memoria en `k8s/base/ollama-statefulset.yaml`

### API no responde

```bash
# Verificar conectividad a Ollama
kubectl exec -n llm-services deployment/langchain-api -- \
  curl http://ollama:11434/api/tags
```

**Solución:** Verificar que Ollama esté Running

### Out of Memory

```bash
# Ver eventos de OOM
kubectl get events -n llm-services | grep OOM

# Usar modelo más ligero
kubectl exec -n llm-services ollama-0 -- ollama pull tinyllama
```

---

## 📚 Documentación Completa

- **Guía detallada:** [K8S_DEPLOYMENT.md](K8S_DEPLOYMENT.md)
- **Ejemplos de código:** [k8s/EXAMPLES.md](k8s/EXAMPLES.md)
- **Guía Raspberry Pi:** [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md)

---

## 🎯 Endpoints de la API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/models` | GET | Lista modelos disponibles |
| `/chat` | POST | Chat sin streaming |
| `/chat/stream` | POST | Chat con streaming (SSE) |
| `/analyze` | POST | Análisis de texto |

### Ejemplo de Petición

```bash
curl -X POST http://langchain-api.llm-services.svc.cluster.local:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "¿Qué es Docker?"}
    ],
    "model": "gemma2:2b",
    "temperature": 0.7,
    "max_tokens": 512
  }'
```

---

## ⚙️ Configuración Avanzada

### Cambiar Modelo por Defecto

```bash
kubectl edit configmap langchain-config -n llm-services
# Cambiar MODEL_NAME: "phi3:mini"

# Reiniciar API para aplicar cambios
kubectl rollout restart deployment/langchain-api -n llm-services
```

### Ajustar Recursos

```bash
# Editar límites de Ollama
kubectl edit statefulset/ollama -n llm-services

# Editar límites de API
kubectl edit deployment/langchain-api -n llm-services
```

### Exponer con NodePort

```bash
# Descomentar sección NodePort en k8s/base/services.yaml
kubectl apply -f k8s/base/services.yaml

# Acceder en: http://<IP-NODO>:30800/
```

---

## 🚀 Próximos Pasos

1. ✅ **Despliegue básico completo**
2. 📝 Integrar desde tus servicios (ver [EXAMPLES.md](k8s/EXAMPLES.md))
3. 📊 Instalar Prometheus/Grafana para monitoreo
4. 🔐 Configurar autenticación (API keys)
5. 🌍 Configurar dominio real en Ingress
6. 💾 Configurar backups automáticos de PVC

---

## 💡 Tips

- **RAM limitada?** Usa `tinyllama` (600MB) en lugar de `gemma2:2b`
- **Respuestas lentas?** Verifica temperatura del RPI con `vcgencmd measure_temp`
- **Múltiples modelos?** Cambia `OLLAMA_MAX_LOADED_MODELS` a 2 en ConfigMap
- **Desarrollo local?** Usa port-forward para acceder desde tu laptop

---

**¿Problemas?** Revisa logs:

```bash
kubectl logs -n llm-services -l app=ollama --tail=50
kubectl logs -n llm-services -l app=langchain-api --tail=50
kubectl get events -n llm-services --sort-by='.lastTimestamp' | tail -20
```

---

**¡Tu LLM local en Kubernetes está listo! 🎉**

Para integrar desde tus servicios, consulta los ejemplos en:
- Python: [k8s/EXAMPLES.md#desde-python](k8s/EXAMPLES.md#desde-python)
- Node.js: [k8s/EXAMPLES.md#desde-nodejs](k8s/EXAMPLES.md#desde-nodejs)
- Go: [k8s/EXAMPLES.md#desde-go](k8s/EXAMPLES.md#desde-go)
