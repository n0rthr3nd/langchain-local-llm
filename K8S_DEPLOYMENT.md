# Despliegue en Kubernetes (k3s)

Guía completa para desplegar LangChain + Ollama en tu cluster k3s de Raspberry Pi 5.

---

## 📋 Tabla de Contenidos

1. [Arquitectura](#arquitectura)
2. [Requisitos Previos](#requisitos-previos)
3. [Inicio Rápido](#inicio-rápido)
4. [Configuración Detallada](#configuración-detallada)
5. [Acceso a los Servicios](#acceso-a-los-servicios)
6. [Escalado y Recursos](#escalado-y-recursos)
7. [Monitoreo](#monitoreo)
8. [Troubleshooting](#troubleshooting)
9. [Limpieza](#limpieza)

---

## 🏗️ Arquitectura

### Componentes Desplegados

```
┌───────────────────────────────────────────────────────────────┐
│  Namespace: llm-services                                      │
│                                                               │
│  ┌─────────────────┐         ┌────────────────────────┐      │
│  │  Ollama         │◄────────│  LangChain API         │      │
│  │  StatefulSet    │         │  Deployment (2 reps)   │      │
│  │  - 1 réplica    │         │  - Balanceo de carga   │      │
│  │  - 5GB RAM      │         │  - Auto-scaling        │      │
│  │  - Port: 11434  │         │  - Port: 8000          │      │
│  └────────┬────────┘         └───────────┬────────────┘      │
│           │                              │                   │
│    ┌──────▼──────┐              ┌────────▼────────┐          │
│    │ PVC (20GB)  │              │  Service        │          │
│    │ Modelos LLM │              │  ClusterIP      │          │
│    └─────────────┘              └────────┬────────┘          │
│                                          │                   │
│                                  ┌───────▼────────┐          │
│                                  │  Ingress       │          │
│                                  │  (Traefik)     │          │
│                                  └────────────────┘          │
└───────────────────────────────────────────────────────────────┘
```

### Flujo de Peticiones

```
Usuario/Servicio
      │
      ▼
   Ingress (llm-api.local)
      │
      ▼
Service: langchain-api (load balancer)
      │
      ├──► Pod API 1 ──┐
      │                 │
      └──► Pod API 2 ──┤
                        │
                        ▼
              Service: ollama
                        │
                        ▼
                   Ollama Pod
                        │
                        ▼
                  PVC (modelos)
```

---

## ✅ Requisitos Previos

### Hardware
- **Raspberry Pi 5** con 8GB RAM
- **20GB+ de espacio libre** en disco
- **k3s instalado y funcionando**

### Software

```bash
# Verificar k3s
kubectl version --short

# Verificar nodos
kubectl get nodes

# Verificar espacio en disco
df -h

# Verificar RAM disponible
free -h
```

### Docker (para construir imágenes)

```bash
docker --version
```

---

## 🚀 Inicio Rápido

### Opción 1: Despliegue Automático (Recomendado)

```bash
# 1. Construir y cargar imagen en k3s
cd k8s/scripts
./build-and-push.sh

# 2. Desplegar todos los componentes
./deploy.sh

# 3. Descargar modelos LLM
kubectl apply -f ../base/model-download-job.yaml
kubectl logs -n llm-services job/model-download -f

# 4. Verificar estado
kubectl get pods -n llm-services
kubectl get svc -n llm-services
```

### Opción 2: Despliegue Manual

```bash
# 1. Construir imagen
cd /home/ecanals/ws/langchain-local-llm
docker build --platform linux/arm64 -t langchain-app:latest .
docker save langchain-app:latest | sudo k3s ctr images import -

# 2. Aplicar manifiestos en orden
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/configmap.yaml
kubectl apply -f k8s/base/pvc.yaml
kubectl apply -f k8s/base/ollama-statefulset.yaml
kubectl apply -f k8s/base/services.yaml

# Esperar a que Ollama esté ready
kubectl wait --for=condition=ready pod -l app=ollama -n llm-services --timeout=300s

# 3. Desplegar API
kubectl apply -f k8s/base/langchain-api-deployment.yaml

# 4. Aplicar seguridad y networking
kubectl apply -f k8s/base/networkpolicy.yaml
kubectl apply -f k8s/base/ingress.yaml
kubectl apply -f k8s/base/hpa.yaml

# 5. Descargar modelos
kubectl apply -f k8s/base/model-download-job.yaml
```

---

## ⚙️ Configuración Detallada

### Modificar Variables de Entorno

Edita `k8s/base/configmap.yaml`:

```yaml
data:
  MODEL_NAME: "phi3:mini"  # Cambiar modelo por defecto
  MAX_INPUT_LENGTH: "20000"  # Aumentar límite de entrada
  OLLAMA_MAX_LOADED_MODELS: "2"  # Permitir 2 modelos en memoria
```

Aplicar cambios:

```bash
kubectl apply -f k8s/base/configmap.yaml
kubectl rollout restart deployment/langchain-api -n llm-services
kubectl rollout restart statefulset/ollama -n llm-services
```

### Ajustar Recursos (RAM/CPU)

Edita `k8s/base/ollama-statefulset.yaml`:

```yaml
resources:
  limits:
    memory: "6Gi"  # Aumentar si tienes más RAM
    cpu: "4000m"   # Aumentar si tienes más cores
  requests:
    memory: "4Gi"
    cpu: "2000m"
```

Aplicar:

```bash
kubectl apply -f k8s/base/ollama-statefulset.yaml
```

### Cambiar Número de Réplicas de la API

```bash
# Método 1: kubectl scale
kubectl scale deployment/langchain-api --replicas=3 -n llm-services

# Método 2: editar el deployment
kubectl edit deployment/langchain-api -n llm-services
# Cambiar spec.replicas: 3

# Método 3: modificar el archivo YAML
# Editar k8s/base/langchain-api-deployment.yaml
# spec.replicas: 3
kubectl apply -f k8s/base/langchain-api-deployment.yaml
```

### Configurar Ingress con Dominio Personalizado

Edita `k8s/base/ingress.yaml`:

```yaml
spec:
  rules:
  - host: llm.tu-dominio.com  # Cambiar aquí
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: langchain-api
            port:
              number: 8000
```

Añadir entrada DNS o en `/etc/hosts`:

```bash
# En tu máquina local
sudo nano /etc/hosts
# Añadir:
192.168.X.X  llm.tu-dominio.com
```

---

## 🌐 Acceso a los Servicios

### 1. Acceso Interno (desde otros pods)

```bash
# URL del servicio dentro del cluster
http://langchain-api.llm-services.svc.cluster.local:8000

# Probar desde un pod temporal
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://langchain-api.llm-services.svc.cluster.local:8000/

# Ejemplo de chat
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl -X POST http://langchain-api.llm-services.svc.cluster.local:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hola"}]}'
```

### 2. Acceso via Ingress (desde fuera del cluster)

```bash
# 1. Añadir entrada en /etc/hosts
echo "192.168.1.100  llm-api.local" | sudo tee -a /etc/hosts

# 2. Probar acceso
curl http://llm-api.local/

# 3. Endpoint de chat
curl -X POST http://llm-api.local/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "¿Qué es Kubernetes?"}
    ]
  }'

# 4. Streaming
curl -X POST http://llm-api.local/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Cuenta hasta 10"}
    ]
  }'
```

### 3. Acceso via NodePort (alternativa)

Descomenta la sección NodePort en `k8s/base/services.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: langchain-api-nodeport
  namespace: llm-services
spec:
  type: NodePort
  selector:
    app: langchain-api
  ports:
  - port: 8000
    targetPort: 8000
    nodePort: 30800  # Puerto expuesto
```

Aplicar y acceder:

```bash
kubectl apply -f k8s/base/services.yaml

# Acceder directamente por IP del nodo
curl http://<IP-RASPBERRY-PI>:30800/
```

### 4. Port-Forward (desarrollo/debug)

```bash
# Forward puerto 8000 a tu máquina local
kubectl port-forward -n llm-services svc/langchain-api 8000:8000

# En otra terminal
curl http://localhost:8000/
```

---

## 📊 Escalado y Recursos

### Distribución de RAM (8GB total)

| Componente | Límite | Request | Réplicas | Total |
|------------|--------|---------|----------|-------|
| **Ollama** | 5GB | 3GB | 1 | 5GB |
| **LangChain API** | 512MB | 256MB | 2 | 1GB |
| **Sistema k3s** | - | - | - | ~1GB |
| **Sistema OS** | - | - | - | ~1GB |
| **Total** | - | - | - | **8GB** |

### Auto-Scaling (HPA)

El HorizontalPodAutoscaler ajusta automáticamente las réplicas:

```bash
# Ver estado del HPA
kubectl get hpa -n llm-services

# Detalles
kubectl describe hpa langchain-api-hpa -n llm-services

# Modificar límites
kubectl edit hpa langchain-api-hpa -n llm-services
```

Configuración actual:
- **Min replicas:** 2
- **Max replicas:** 4
- **CPU threshold:** 70%
- **Memory threshold:** 80%

### Escalar Manualmente

```bash
# Escalar API a 3 réplicas
kubectl scale deployment/langchain-api --replicas=3 -n llm-services

# Ver estado
kubectl get pods -n llm-services -l app=langchain-api

# ⚠️ NO escalar Ollama (debe ser 1 réplica siempre)
```

---

## 📈 Monitoreo

### Ver Estado de los Pods

```bash
# Listar todos los pods
kubectl get pods -n llm-services

# Detalles de un pod específico
kubectl describe pod <pod-name> -n llm-services

# Logs en tiempo real
kubectl logs -f -n llm-services -l app=ollama
kubectl logs -f -n llm-services -l app=langchain-api

# Ver eventos
kubectl get events -n llm-services --sort-by='.lastTimestamp'
```

### Monitorear Recursos

```bash
# Uso de CPU/RAM por pod (requiere metrics-server)
kubectl top pods -n llm-services

# Uso por nodo
kubectl top nodes

# Espacio del PVC
kubectl get pvc -n llm-services
kubectl describe pvc ollama-models-pvc -n llm-services
```

### Verificar Modelos Instalados

```bash
# Exec en el pod de Ollama
kubectl exec -it -n llm-services ollama-0 -- ollama list

# Ver espacio usado
kubectl exec -it -n llm-services ollama-0 -- du -sh /root/.ollama
```

### Dashboard Web (opcional)

```bash
# Instalar Kubernetes Dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Acceder
kubectl proxy
# Visita: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```

---

## 🔧 Troubleshooting

### Problema: Pods en estado Pending

```bash
# Ver razón
kubectl describe pod <pod-name> -n llm-services

# Causas comunes:
# 1. PVC no bound
kubectl get pvc -n llm-services

# 2. Recursos insuficientes
kubectl top nodes
kubectl describe nodes

# 3. Imagen no disponible
kubectl describe pod <pod-name> -n llm-services | grep -A 5 Events
```

### Problema: Ollama no arranca

```bash
# Ver logs
kubectl logs -n llm-services ollama-0

# Causas comunes:
# 1. RAM insuficiente - reducir límites
kubectl edit statefulset/ollama -n llm-services

# 2. PVC corrupto - recrear
kubectl delete pvc ollama-models-pvc -n llm-services
kubectl apply -f k8s/base/pvc.yaml
```

### Problema: API no conecta con Ollama

```bash
# Verificar conectividad
kubectl exec -n llm-services deployment/langchain-api -- \
  curl http://ollama:11434/api/tags

# Verificar NetworkPolicy
kubectl get networkpolicy -n llm-services
kubectl describe networkpolicy ollama-network-policy -n llm-services

# Deshabilitar temporalmente para debug
kubectl delete networkpolicy -n llm-services --all
```

### Problema: Modelos no se descargan

```bash
# Ver logs del job
kubectl logs -n llm-services job/model-download -f

# Reintentar descarga manual
kubectl delete job model-download -n llm-services
kubectl apply -f k8s/base/model-download-job.yaml

# Descargar manualmente
kubectl exec -it -n llm-services ollama-0 -- ollama pull gemma2:2b
```

### Problema: Out of Memory (OOM)

```bash
# Ver eventos de OOM
kubectl get events -n llm-services | grep OOM

# Reducir límites de Ollama
kubectl edit statefulset/ollama -n llm-services
# Cambiar limits.memory de 5Gi a 4Gi

# Usar modelo más pequeño
kubectl exec -it -n llm-services ollama-0 -- ollama pull tinyllama
kubectl edit configmap langchain-config -n llm-services
# Cambiar MODEL_NAME: "tinyllama"
```

### Reiniciar Servicios

```bash
# Reiniciar Ollama
kubectl rollout restart statefulset/ollama -n llm-services

# Reiniciar API
kubectl rollout restart deployment/langchain-api -n llm-services

# Ver estado del rollout
kubectl rollout status statefulset/ollama -n llm-services
kubectl rollout status deployment/langchain-api -n llm-services
```

---

## 🗑️ Limpieza

### Eliminar Despliegue (conservar modelos)

```bash
cd k8s/scripts
./undeploy.sh
# Seleccionar 'n' cuando pregunte por PVC
```

### Eliminar Todo (incluyendo modelos)

```bash
cd k8s/scripts
./undeploy.sh
# Seleccionar 's' para eliminar PVC
# Seleccionar 's' para eliminar namespace
```

### Limpieza Manual

```bash
# Eliminar en orden inverso
kubectl delete -f k8s/base/hpa.yaml
kubectl delete -f k8s/base/ingress.yaml
kubectl delete -f k8s/base/networkpolicy.yaml
kubectl delete -f k8s/base/langchain-api-deployment.yaml
kubectl delete -f k8s/base/services.yaml
kubectl delete -f k8s/base/ollama-statefulset.yaml
kubectl delete -f k8s/base/pvc.yaml  # Solo si quieres borrar modelos
kubectl delete -f k8s/base/configmap.yaml
kubectl delete namespace llm-services
```

---

## 📚 Recursos Adicionales

### Estructura de Archivos

```
k8s/
├── base/
│   ├── namespace.yaml              # Namespace llm-services
│   ├── configmap.yaml              # Variables de entorno
│   ├── pvc.yaml                    # Volumen persistente para modelos
│   ├── ollama-statefulset.yaml    # Ollama (1 réplica)
│   ├── langchain-api-deployment.yaml  # API (2+ réplicas)
│   ├── services.yaml               # ClusterIP Services
│   ├── ingress.yaml                # Traefik Ingress
│   ├── networkpolicy.yaml          # Políticas de seguridad
│   ├── hpa.yaml                    # Auto-scaling
│   └── model-download-job.yaml    # Job de descarga de modelos
├── scripts/
│   ├── deploy.sh                   # Despliegue automático
│   ├── undeploy.sh                 # Limpieza
│   └── build-and-push.sh          # Build imagen + import a k3s
└── overlays/
    └── rpi/                        # Configuraciones específicas RPI
```

### Comandos Útiles

```bash
# Ver todos los recursos del namespace
kubectl get all -n llm-services

# Ver uso de recursos en tiempo real
watch kubectl top pods -n llm-services

# Abrir shell en pod
kubectl exec -it -n llm-services ollama-0 -- /bin/sh
kubectl exec -it -n llm-services deployment/langchain-api -- /bin/bash

# Port-forward múltiples servicios
kubectl port-forward -n llm-services svc/langchain-api 8000:8000 &
kubectl port-forward -n llm-services svc/ollama 11434:11434 &

# Backup de modelos (copiar PVC)
kubectl cp llm-services/ollama-0:/root/.ollama /tmp/ollama-backup

# Ver configuración completa de un recurso
kubectl get statefulset ollama -n llm-services -o yaml
```

---

## 🎯 Próximos Pasos

1. **Monitoreo avanzado:** Instalar Prometheus + Grafana
2. **Backups automáticos:** Configurar Velero para backup de PVC
3. **Multi-nodo:** Añadir más Raspberry Pi al cluster
4. **GPU:** Si añades GPU, modificar el StatefulSet de Ollama
5. **CI/CD:** Automatizar builds con GitHub Actions

---

**¿Necesitas ayuda?** Revisa los logs y eventos primero:

```bash
kubectl logs -n llm-services -l app=ollama --tail=100
kubectl get events -n llm-services --sort-by='.lastTimestamp' | tail -20
```

**¡Tu LLM local en Kubernetes está listo! 🚀**
