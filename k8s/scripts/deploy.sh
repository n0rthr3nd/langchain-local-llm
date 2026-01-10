#!/bin/bash
# Script de despliegue para k3s
# Despliega LangChain + Ollama en Kubernetes

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${NC}ℹ $1${NC}"; }

echo "======================================================"
echo "   Despliegue de LangChain + Ollama en k3s"
echo "======================================================"
echo ""

# Verificar kubectl
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl no encontrado. Instálalo primero."
    exit 1
fi
print_success "kubectl encontrado"

# Verificar conexión al cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "No se puede conectar al cluster k3s"
    exit 1
fi
print_success "Conectado al cluster k3s"

# Directorio base
K8S_BASE="$(cd "$(dirname "$0")/.." && pwd)/base"
cd "$K8S_BASE"

echo ""
print_info "Aplicando manifiestos desde: $K8S_BASE"
echo ""

# 1. Namespace
print_info "1/9 Creando namespace..."
kubectl apply -f namespace.yaml
print_success "Namespace creado"

# 2. ConfigMap
print_info "2/9 Creando ConfigMap..."
kubectl apply -f configmap.yaml
print_success "ConfigMap creado"

# 3. PVC
print_info "3/9 Creando PersistentVolumeClaim..."
kubectl apply -f pvc.yaml
print_success "PVC creado"

# 3.5. Chroma PVC
print_info "3.5/9 Creando ChromaDB PVC..."
kubectl apply -f chroma-pvc.yaml
print_success "ChromaDB PVC creado"

# Esperar a que PVC esté bound
print_info "Esperando a que PVC esté bound..."
kubectl wait --for=jsonpath='{.status.phase}'=Bound \
  -n llm-services pvc/ollama-models-pvc --timeout=60s || {
  print_warning "PVC no está bound aún, continuando..."
}

# 4. Ollama StatefulSet
print_info "4/9 Desplegando Ollama StatefulSet..."
kubectl apply -f ollama-statefulset.yaml
print_success "Ollama StatefulSet creado"

# 5. Services
print_info "5/9 Creando Services..."
kubectl apply -f services.yaml
print_success "Services creados"

# Esperar a que Ollama esté listo
print_info "Esperando a que Ollama esté ready (esto puede tardar 1-2 minutos)..."
kubectl wait --for=condition=ready pod -l app=ollama \
  -n llm-services --timeout=300s || {
  print_error "Ollama no está ready después de 5 minutos"
  print_info "Verifica los logs: kubectl logs -n llm-services -l app=ollama"
  exit 1
}
print_success "Ollama está ready"

# 6. LangChain API Deployment
print_info "6/9 Desplegando LangChain API..."
kubectl apply -f langchain-api-deployment.yaml
print_success "LangChain API Deployment creado"

# Esperar a que al menos 1 réplica esté ready
print_info "Esperando a que LangChain API esté ready..."
kubectl wait --for=condition=ready pod -l app=langchain-api \
  -n llm-services --timeout=120s || {
  print_warning "LangChain API no está ready todavía"
  print_info "Verifica los logs: kubectl logs -n llm-services -l app=langchain-api"
}
print_success "LangChain API está ready"

# 6.5. Frontend Deployment
print_info "6.5 Desplegando Frontend..."
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
print_success "Frontend resources creados"

# Reiniciar despliegues para tomar nuevas imágenes
print_info "Reiniciando despliegues para actualizar imágenes..."
kubectl rollout restart deployment/langchain-api -n llm-services
kubectl rollout restart deployment/langchain-frontend -n llm-services
print_success "Rollout restart solicitado"

# 7. NetworkPolicy
print_info "7/9 Aplicando NetworkPolicies..."
kubectl apply -f networkpolicy.yaml
print_success "NetworkPolicies aplicadas"

# 8. Ingress
print_info "8/9 Creando Ingress..."
kubectl apply -f ingress.yaml
print_success "Ingress creado"

# 9. HPA (opcional)
print_info "9/9 Creando HorizontalPodAutoscaler..."
if kubectl apply -f hpa.yaml 2>/dev/null; then
  print_success "HPA creado"
else
  print_warning "HPA no pudo crearse (¿metrics-server instalado?)"
  print_info "El HPA es opcional. Si lo necesitas, instala metrics-server primero."
fi

echo ""
echo "======================================================"
print_success "Despliegue completado!"
echo "======================================================"
echo ""

# Mostrar estado
print_info "Estado de los pods:"
kubectl get pods -n llm-services

echo ""
print_info "Servicios disponibles:"
kubectl get svc -n llm-services

echo ""
print_info "Ingress configurado:"
kubectl get ingress -n llm-services

echo ""
echo "======================================================"
echo "Próximos pasos:"
echo "======================================================"
echo ""
echo "1. Descargar modelos LLM:"
echo "   kubectl apply -f $K8S_BASE/model-download-job.yaml"
echo "   kubectl logs -n llm-services job/model-download -f"
echo ""
echo "2. Probar la API:"
echo "   # Desde dentro del cluster:"
echo "   kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \\"
echo "     curl http://langchain-api.llm-services.svc.cluster.local:8000/"
echo ""
echo "3. Acceso desde fuera (Ingress):"
echo "   # Configurado para: https://northr3nd.duckdns.org/ia/chat"
echo "   # API directa (via frontend proxy): https://northr3nd.duckdns.org/ia/chat/api/"
echo ""
echo "4. Ver logs:"
echo "   kubectl logs -n llm-services -l app=ollama -f"
echo "   kubectl logs -n llm-services -l app=langchain-api -f"
echo "   kubectl logs -n llm-services -l app=langchain-frontend -f"
echo ""
echo "5. Monitorear recursos:"
echo "   kubectl top pods -n llm-services"
echo ""

print_success "¡Todo listo! 🚀"
