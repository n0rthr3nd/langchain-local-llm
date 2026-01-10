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

# Construir imagen para ARM64
print_info "1/2 Construyendo imagen Docker para linux/arm64..."
docker build \
  --platform linux/arm64 \
  -t "$FULL_IMAGE" \
  -f Dockerfile \
  . || {
  print_error "Error al construir la imagen"
  exit 1
}
print_success "Imagen construida: $FULL_IMAGE"

# Importar imagen a k3s
print_info "2/2 Importando imagen a k3s..."

# k3s usa containerd, podemos importar la imagen directamente
if command -v k3s &> /dev/null; then
  # Método 1: Guardar y cargar en k3s (si k3s está disponible)
  docker save "$FULL_IMAGE" | sudo k3s ctr images import - || {
    print_warning "No se pudo importar con k3s ctr, probando método alternativo..."

    # Método 2: Usar docker save/ctr load
    TMP_TAR="/tmp/${IMAGE_NAME}.tar"
    docker save "$FULL_IMAGE" -o "$TMP_TAR"
    sudo ctr -n k8s.io images import "$TMP_TAR"
    rm "$TMP_TAR"
  }
else
  # Si no tenemos k3s cli, usar ctr directamente
  TMP_TAR="/tmp/${IMAGE_NAME}.tar"
  docker save "$FULL_IMAGE" -o "$TMP_TAR"
  sudo ctr -n k8s.io images import "$TMP_TAR"
  rm "$TMP_TAR"
fi

print_success "Imagen importada a k3s"

# Verificar
echo ""
print_info "Verificando imagen en k3s..."
sudo ctr -n k8s.io images ls | grep "$IMAGE_NAME" || {
  print_error "No se pudo verificar la imagen en k3s"
  exit 1
}

echo ""
echo "======================================================"
print_success "Imagen lista para usar en k3s!"
echo "======================================================"
echo ""
print_info "Para desplegar, ejecuta:"
echo "  cd k8s/scripts"
echo "  ./deploy.sh"
echo ""
