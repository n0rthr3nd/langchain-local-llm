#!/bin/bash

###############################################################################
# Build and Deploy to K3S
#
# Script para construir imágenes Docker y desplegarlas en K3S
###############################################################################

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detectar directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Configuración
REGISTRY="${REGISTRY:-}"  # Dejar vacío para K3S local, o especificar tu registry
IMAGE_NAME="langchain-app"
FRONTEND_IMAGE_NAME="langchain-frontend"
VERSION_TAG="${VERSION_TAG:-$(date +v%Y%m%d-%H%M%S)}"
NAMESPACE="llm-services"

###############################################################################
# Funciones
###############################################################################

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_prerequisites() {
    print_header "Verificando Requisitos"

    # Verificar docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado"
        exit 1
    fi
    print_success "Docker encontrado: $(docker --version)"

    # Verificar kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl no está instalado"
        exit 1
    fi
    print_success "kubectl encontrado"

    # Verificar k3s (opcional)
    if command -v k3s &> /dev/null; then
        print_success "K3S encontrado: $(k3s --version | head -1)"
    else
        print_info "K3S no encontrado en PATH (esto es normal si usas kubectl remoto)"
    fi
}

detect_architecture() {
    print_header "Detectando Arquitectura"

    ARCH=$(uname -m)
    case "$ARCH" in
        aarch64|arm64)
            PLATFORM="linux/arm64"
            print_success "Arquitectura detectada: ARM64 (Raspberry Pi)"
            ;;
        x86_64|amd64)
            PLATFORM="linux/amd64"
            print_success "Arquitectura detectada: AMD64 (x86)"
            ;;
        *)
            print_warning "Arquitectura desconocida: $ARCH"
            PLATFORM="linux/arm64"
            print_info "Usando ARM64 por defecto"
            ;;
    esac
}

build_backend_image() {
    print_header "Construyendo Imagen Backend (langchain-app)"

    local full_image_name="${IMAGE_NAME}:${VERSION_TAG}"
    if [ -n "$REGISTRY" ]; then
        full_image_name="${REGISTRY}/${full_image_name}"
    fi

    print_info "Imagen: $full_image_name"
    print_info "Plataforma: $PLATFORM"
    print_info "Build context: $PROJECT_ROOT"

    # Construir imagen desde el directorio raíz del proyecto
    cd "$PROJECT_ROOT"

    if docker buildx build \
        --platform "$PLATFORM" \
        -t "$full_image_name" \
        -t "${IMAGE_NAME}:latest" \
        --load \
        .; then
        print_success "Imagen backend construida: $full_image_name"
    else
        print_error "Error construyendo imagen backend"
        exit 1
    fi

    # Verificar que el código MCP está en la imagen
    print_info "Verificando código MCP en la imagen..."
    if docker run --rm "$full_image_name" ls /app/mcp_server/mongodb_mcp.py &> /dev/null; then
        print_success "Código MCP verificado en la imagen"
    else
        print_error "El código MCP NO está en la imagen"
        print_warning "Verifica que app/mcp_server/ existe en el contexto de build"
        exit 1
    fi
}

build_frontend_image() {
    print_header "Construyendo Imagen Frontend (Opcional)"

    local frontend_dir="$PROJECT_ROOT/frontend"

    if [ ! -d "$frontend_dir" ]; then
        print_warning "Directorio frontend no encontrado, saltando..."
        return 0
    fi

    local full_image_name="${FRONTEND_IMAGE_NAME}:${VERSION_TAG}"
    if [ -n "$REGISTRY" ]; then
        full_image_name="${REGISTRY}/${full_image_name}"
    fi

    print_info "Imagen: $full_image_name"
    print_info "Build context: $frontend_dir"

    cd "$frontend_dir"
    if docker buildx build \
        --platform "$PLATFORM" \
        -t "$full_image_name" \
        -t "${FRONTEND_IMAGE_NAME}:latest" \
        --load \
        .; then
        print_success "Imagen frontend construida: $full_image_name"
    else
        print_warning "Error construyendo imagen frontend (continuando...)"
    fi
}

import_to_k3s() {
    print_header "Importando Imágenes a K3S"

    # Verificar si k3s está disponible
    if ! command -v k3s &> /dev/null; then
        print_warning "k3s no encontrado, saltando importación local"
        print_info "Si usas un registry remoto, las imágenes ya están disponibles"
        return 0
    fi

    # Importar imagen backend con tag versionado
    local backend_full_image="${IMAGE_NAME}:${VERSION_TAG}"
    if [ -n "$REGISTRY" ]; then
        backend_full_image="${REGISTRY}/${backend_full_image}"
    else
        backend_full_image="${IMAGE_NAME}:${VERSION_TAG}"
    fi

    print_info "Importando ${backend_full_image} a K3S..."
    if docker save "${backend_full_image}" | sudo k3s ctr images import -; then
        print_success "Imagen backend ${VERSION_TAG} importada a K3S"
    else
        print_warning "No se pudo importar ${backend_full_image} a K3S"
    fi

    # También importar :latest como backup
    print_info "Importando ${IMAGE_NAME}:latest a K3S..."
    if docker save "${IMAGE_NAME}:latest" | sudo k3s ctr images import -; then
        print_success "Imagen backend :latest importada a K3S"
    else
        print_warning "No se pudo importar ${IMAGE_NAME}:latest a K3S"
    fi

    # Importar imagen frontend con tag versionado (si existe)
    if docker image inspect "${FRONTEND_IMAGE_NAME}:${VERSION_TAG}" &> /dev/null; then
        local frontend_full_image="${FRONTEND_IMAGE_NAME}:${VERSION_TAG}"
        if [ -n "$REGISTRY" ]; then
            frontend_full_image="${REGISTRY}/${frontend_full_image}"
        fi

        print_info "Importando ${frontend_full_image} a K3S..."
        if docker save "${frontend_full_image}" | sudo k3s ctr images import -; then
            print_success "Imagen frontend ${VERSION_TAG} importada a K3S"
        fi

        # También importar :latest
        print_info "Importando ${FRONTEND_IMAGE_NAME}:latest a K3S..."
        if docker save "${FRONTEND_IMAGE_NAME}:latest" | sudo k3s ctr images import -; then
            print_success "Imagen frontend :latest importada a K3S"
        fi
    fi
}

update_kustomization() {
    print_header "Actualizando Kustomization"

    local kustomization_file="$PROJECT_ROOT/k8s/base/kustomization.yaml"

    if [ ! -f "$kustomization_file" ]; then
        print_error "Archivo $kustomization_file no encontrado"
        exit 1
    fi

    print_info "Actualizando tags de imágenes a: $VERSION_TAG"

    # Backup
    cp "$kustomization_file" "${kustomization_file}.backup"

    # Actualizar tags solo para langchain-app y langchain-frontend
    # NO actualizar ollama (usa imagen pública oficial)
    sed -i.tmp "/name: langchain-app/{n;s|newTag: .*|newTag: ${VERSION_TAG}|;}" "$kustomization_file"
    sed -i.tmp "/name: langchain-frontend/{n;s|newTag: .*|newTag: ${VERSION_TAG}|;}" "$kustomization_file"
    rm -f "${kustomization_file}.tmp"

    print_success "Kustomization actualizado"
    print_info "Backup guardado en: ${kustomization_file}.backup"
}

deploy_to_k3s() {
    print_header "Desplegando a K3S"

    print_info "Namespace: $NAMESPACE"

    # Verificar si el secret de MongoDB existe
    if ! kubectl get secret mongodb-secret -n "$NAMESPACE" &> /dev/null; then
        print_warning "Secret mongodb-secret no encontrado"
        print_info "Asegúrate de configurar k8s/base/mongodb-secret.yaml primero"

        read -p "¿Continuar de todas formas? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Abortando. Edita k8s/base/mongodb-secret.yaml y vuelve a ejecutar"
            exit 1
        fi
    fi

    # Aplicar manifiestos
    print_info "Aplicando manifiestos desde: $PROJECT_ROOT/k8s/base/"
    if kubectl apply -k "$PROJECT_ROOT/k8s/base/"; then
        print_success "Manifiestos aplicados"
    else
        print_error "Error aplicando manifiestos"
        exit 1
    fi

    # Reiniciar deployment para forzar pull de nueva imagen
    print_info "Reiniciando deployment para usar nueva imagen..."
    kubectl rollout restart deployment/langchain-api -n "$NAMESPACE" || true

    # Esperar a que esté listo
    print_info "Esperando a que los pods estén listos..."
    if kubectl rollout status deployment/langchain-api -n "$NAMESPACE" --timeout=300s; then
        print_success "Deployment actualizado y listo"
    else
        print_warning "Timeout esperando a deployment"
    fi
}

verify_deployment() {
    print_header "Verificando Despliegue"

    # Ver pods
    print_info "Pods en namespace $NAMESPACE:"
    kubectl get pods -n "$NAMESPACE"

    echo ""

    # Verificar variables de entorno
    print_info "Variables de entorno de MongoDB:"
    kubectl exec -n "$NAMESPACE" deployment/langchain-api -- env | grep MONGODB || true

    echo ""

    # Verificar que el código MCP existe
    print_info "Verificando código MCP en el pod..."
    if kubectl exec -n "$NAMESPACE" deployment/langchain-api -- ls /app/mcp_server/mongodb_mcp.py &> /dev/null; then
        print_success "Código MCP encontrado en el pod"
    else
        print_error "Código MCP NO encontrado en el pod"
        print_warning "La imagen puede no haberse actualizado correctamente"
    fi
}

test_mongodb_connection() {
    print_header "Probando Conexión a MongoDB"

    print_info "Ejecutando test de conexión..."
    if kubectl exec -n "$NAMESPACE" deployment/langchain-api -- \
        python /app/mcp_server/mongodb_mcp.py 2>&1 | tail -20; then
        print_success "Test ejecutado"
    else
        print_warning "Error en el test. Revisa los logs"
    fi
}

show_summary() {
    print_header "Resumen del Build"

    echo -e "${GREEN}"
    cat << EOF
✓ Imágenes construidas:
  - ${IMAGE_NAME}:${VERSION_TAG}
  - ${IMAGE_NAME}:latest

✓ Desplegado en K3S namespace: $NAMESPACE

Próximos pasos:

1. Ver logs:
   kubectl logs -n $NAMESPACE -l app=langchain-api -f

2. Probar MongoDB MCP:
   kubectl exec -n $NAMESPACE -it deployment/langchain-api -- \\
     python /app/mcp_server/query_examples.py

3. Acceder a la API:
   kubectl port-forward -n $NAMESPACE svc/langchain-api 8000:8000

4. Ver recursos:
   kubectl get all -n $NAMESPACE

Version: $VERSION_TAG
EOF
    echo -e "${NC}"
}

###############################################################################
# Función principal
###############################################################################

main() {
    print_header "Build y Deploy a K3S - MongoDB MCP"

    check_prerequisites
    detect_architecture
    build_backend_image
    build_frontend_image
    import_to_k3s
    update_kustomization
    deploy_to_k3s
    verify_deployment
    test_mongodb_connection
    show_summary

    print_success "¡Proceso completado!"
}

###############################################################################
# Manejo de opciones
###############################################################################

show_help() {
    cat << EOF
Uso: $0 [OPCIÓN]

Construye imágenes Docker con el código MCP y las despliega en K3S.

Opciones:
    -h, --help              Mostrar esta ayuda
    -b, --build-only        Solo construir imágenes (no desplegar)
    -d, --deploy-only       Solo desplegar (asumir imágenes ya construidas)
    -v, --version TAG       Especificar tag de versión (default: timestamp)
    -r, --registry URL      Usar registry remoto (ej: docker.io/usuario)
    --skip-frontend         No construir imagen frontend
    --no-import             No importar imágenes a K3S local

Variables de entorno:
    VERSION_TAG             Tag de versión para las imágenes
    REGISTRY                URL del registry (vacío para local)

Ejemplos:
    $0                                  # Build completo y deploy
    $0 --build-only                     # Solo construir imágenes
    $0 --deploy-only                    # Solo desplegar
    VERSION_TAG=v1.0.0 $0               # Usar tag específico
    REGISTRY=docker.io/usuario $0       # Usar registry remoto

EOF
}

BUILD_ONLY=false
DEPLOY_ONLY=false
SKIP_FRONTEND=false
NO_IMPORT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -b|--build-only)
            BUILD_ONLY=true
            shift
            ;;
        -d|--deploy-only)
            DEPLOY_ONLY=true
            shift
            ;;
        -v|--version)
            VERSION_TAG="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        --no-import)
            NO_IMPORT=true
            shift
            ;;
        *)
            print_error "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Ejecutar según opciones
if [ "$BUILD_ONLY" = true ]; then
    check_prerequisites
    detect_architecture
    build_backend_image
    [ "$SKIP_FRONTEND" = false ] && build_frontend_image
    [ "$NO_IMPORT" = false ] && import_to_k3s
    show_summary
elif [ "$DEPLOY_ONLY" = true ]; then
    check_prerequisites
    update_kustomization
    deploy_to_k3s
    verify_deployment
    test_mongodb_connection
    show_summary
else
    main
fi
