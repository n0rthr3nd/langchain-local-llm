#!/bin/bash
# Script para reconstruir las imágenes SIN CACHE y forzar actualización en k3s
# Útil cuando los cambios en el código no se reflejan después de deploy

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
echo "   Rebuild FORZADO sin caché + Deploy"
echo "======================================================"
echo ""

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker no encontrado"
    exit 1
fi

# Directorio raíz del proyecto
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

IMAGE_NAME="langchain-app"
IMAGE_TAG="latest"
FULL_IMAGE="$IMAGE_NAME:$IMAGE_TAG"
FRONTEND_IMAGE="langchain-frontend:latest"

print_info "Directorio del proyecto: $PROJECT_ROOT"
echo ""

# 1. Limpiar imágenes viejas localmente
print_warning "1/6 Eliminando imágenes viejas localmente..."
docker rmi "$FULL_IMAGE" 2>/dev/null || true
docker rmi "$FRONTEND_IMAGE" 2>/dev/null || true
print_success "Imágenes locales eliminadas"

# 2. Construir Backend SIN CACHE
print_info "2/6 Construyendo Backend SIN CACHE (puede tardar más)..."
docker build \
  --platform linux/arm64 \
  --no-cache \
  -t "$FULL_IMAGE" \
  -f Dockerfile \
  . || {
  print_error "Error al construir Backend"
  exit 1
}
print_success "Backend construido: $FULL_IMAGE"

# 3. Construir Frontend SIN CACHE
print_info "3/6 Construyendo Frontend SIN CACHE..."
docker build \
  --platform linux/arm64 \
  --no-cache \
  -t "$FRONTEND_IMAGE" \
  -f frontend/Dockerfile \
  frontend/ || {
  print_error "Error al construir Frontend"
  exit 1
}
print_success "Frontend construido: $FRONTEND_IMAGE"

# 4. Eliminar imágenes viejas de k3s
print_warning "4/6 Eliminando imágenes viejas de k3s..."
sudo ctr -n k8s.io images rm docker.io/library/$FULL_IMAGE 2>/dev/null || true
sudo ctr -n k8s.io images rm docker.io/library/$FRONTEND_IMAGE 2>/dev/null || true
print_success "Imágenes viejas eliminadas de k3s"

# 5. Importar imágenes nuevas a k3s
print_info "5/6 Importando imágenes NUEVAS a k3s..."

import_image() {
  local img=$1
  if command -v k3s &> /dev/null; then
    docker save "$img" | sudo k3s ctr images import - || {
      print_warning "Fallo pipe k3s ctr, usando archivo temporal..."
      TMP_TAR="/tmp/img_$(date +%s).tar"
      docker save "$img" -o "$TMP_TAR"
      sudo ctr -n k8s.io images import "$TMP_TAR"
      rm "$TMP_TAR"
    }
  else
    TMP_TAR="/tmp/img_$(date +%s).tar"
    docker save "$img" -o "$TMP_TAR"
    sudo ctr -n k8s.io images import "$TMP_TAR"
    rm "$TMP_TAR"
  fi
}

print_info "Importando $FULL_IMAGE..."
import_image "$FULL_IMAGE"

print_info "Importando $FRONTEND_IMAGE..."
import_image "$FRONTEND_IMAGE"

print_success "Imágenes NUEVAS importadas a k3s"

# 6. Forzar recreación de pods en k8s
print_info "6/6 Forzando recreación de pods en k8s..."

if command -v kubectl &> /dev/null; then
  # Eliminar pods para forzar recreación con nuevas imágenes
  kubectl delete pods -n llm-services -l app=langchain-api 2>/dev/null || print_warning "No se encontraron pods de langchain-api"
  kubectl delete pods -n llm-services -l app=langchain-frontend 2>/dev/null || print_warning "No se encontraron pods de frontend"

  print_success "Pods eliminados, Kubernetes los recreará automáticamente"

  echo ""
  print_info "Esperando a que los nuevos pods estén listos (30s)..."
  sleep 5

  kubectl wait --for=condition=ready pod -l app=langchain-api -n llm-services --timeout=120s || {
    print_warning "Backend aún no está ready, verifica los logs"
  }

  kubectl wait --for=condition=ready pod -l app=langchain-frontend -n llm-services --timeout=120s || {
    print_warning "Frontend aún no está ready, verifica los logs"
  }
else
  print_warning "kubectl no encontrado, no se pueden reiniciar pods automáticamente"
  print_info "Reinicia manualmente con: kubectl delete pods -n llm-services -l app=langchain-api"
fi

echo ""
echo "======================================================"
print_success "¡Rebuild forzado completado!"
echo "======================================================"
echo ""

print_info "Verificar imágenes en k3s:"
sudo ctr -n k8s.io images ls | grep -E "langchain-(app|frontend)" || true

echo ""
print_info "Ver estado de los pods:"
kubectl get pods -n llm-services 2>/dev/null || print_warning "kubectl no disponible"

echo ""
print_info "Ver logs del backend:"
echo "  kubectl logs -n llm-services -l app=langchain-api -f"
echo ""
print_info "Ver logs del frontend:"
echo "  kubectl logs -n llm-services -l app=langchain-frontend -f"
echo ""

print_success "¡Todo listo! Los cambios deberían estar activos ahora 🚀"
echo ""
