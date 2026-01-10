#!/bin/bash
# Script para eliminar el despliegue de k3s

set -e

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }

echo "======================================================"
echo "   Eliminando LangChain + Ollama de k3s"
echo "======================================================"
echo ""

# Confirmar
read -p "¿Estás seguro? Esto eliminará todos los recursos (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Cancelado."
    exit 0
fi

# Preguntar si eliminar PVC (modelos)
echo ""
read -p "¿Eliminar también los modelos descargados (PVC)? (s/n): " -n 1 -r
echo
DELETE_PVC=$REPLY

K8S_BASE="$(cd "$(dirname "$0")/.." && pwd)/base"

# Eliminar recursos en orden inverso
echo ""
echo "Eliminando recursos..."

kubectl delete -f "$K8S_BASE/hpa.yaml" 2>/dev/null || true
print_success "HPA eliminado"

kubectl delete -f "$K8S_BASE/ingress.yaml" 2>/dev/null || true
print_success "Ingress eliminado"

kubectl delete -f "$K8S_BASE/networkpolicy.yaml" 2>/dev/null || true
print_success "NetworkPolicies eliminadas"

kubectl delete -f "$K8S_BASE/langchain-api-deployment.yaml" 2>/dev/null || true
print_success "LangChain API eliminado"

kubectl delete -f "$K8S_BASE/services.yaml" 2>/dev/null || true
print_success "Services eliminados"

kubectl delete -f "$K8S_BASE/ollama-statefulset.yaml" 2>/dev/null || true
print_success "Ollama StatefulSet eliminado"

# PVC (opcional)
if [[ $DELETE_PVC =~ ^[Ss]$ ]]; then
    kubectl delete -f "$K8S_BASE/pvc.yaml" 2>/dev/null || true
    print_success "PVC eliminado (modelos borrados)"
else
    echo "⚠ PVC conservado (modelos intactos)"
fi

kubectl delete -f "$K8S_BASE/configmap.yaml" 2>/dev/null || true
print_success "ConfigMap eliminado"

# Namespace (último)
read -p "¿Eliminar el namespace completo? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    kubectl delete namespace llm-services 2>/dev/null || true
    print_success "Namespace eliminado"
else
    echo "⚠ Namespace conservado"
fi

echo ""
echo "======================================================"
print_success "Limpieza completada"
echo "======================================================"
