#!/bin/bash
# Script para construir la imagen de LangChain API para ARM64 y cargarla en k3s

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
echo "   Build de imagen para k3s (ARM64)"
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

print_info "Directorio del proyecto: $PROJECT_ROOT"
print_info "Construyendo imagen: $FULL_IMAGE"
echo ""

# Construir imagen para ARM64 (Backend)
print_info "1/4 Construyendo imagen Backend (linux/arm64)..."
docker build \
  --platform linux/arm64 \
  -t "$FULL_IMAGE" \
  -f Dockerfile \
  . || {
  print_error "Error al construir la imagen Backend"
  exit 1
}
print_success "Imagen Backend construida: $FULL_IMAGE"

# Construir imagen Frontend
FRONTEND_IMAGE="langchain-frontend:latest"
print_info "2/4 Construyendo imagen Frontend (linux/arm64)..."
docker build \
  --platform linux/arm64 \
  -t "$FRONTEND_IMAGE" \
  -f frontend/Dockerfile \
  frontend/ || {
  print_error "Error al construir la imagen Frontend"
  exit 1
}
print_success "Imagen Frontend construida: $FRONTEND_IMAGE"

# Importar imagenes a k3s
print_info "3/4 Importando imagenes a k3s..."

# Función para importar
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

print_success "Imágenes importadas a k3s"

# Verificar
echo ""
print_info "4/4 Verificando imagenes en k3s..."
sudo ctr -n k8s.io images ls | grep "$IMAGE_NAME"
sudo ctr -n k8s.io images ls | grep "langchain-frontend" || {
  print_warning "No se pudieron verificar todas las imágenes (puede ser solo un error de grep si usas namespaces distintos)"
}

echo ""
echo "======================================================"
print_success "¡Imágenes listas para usar en k3s!"
echo "======================================================"
echo ""
print_info "Para desplegar, ejecuta:"
echo "  cd k8s/scripts"
echo "  ./deploy.sh"
echo ""
