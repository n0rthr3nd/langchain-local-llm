#!/bin/bash

# Script para escalar el StatefulSet de Ollama
# Uso: ./scale_ollama.sh <numero_de_replicas>

# Namespace donde se encuentra el StatefulSet de Ollama
NAMESPACE="llm-services"
STATEFULSET_NAME="ollama"

# Verificar si se proporcionó un número de réplicas
if [ -z "$1" ]; then
  echo "Uso: $0 <numero_de_replicas>"
  echo "Ejemplo: $0 0   (para escalar a 0 réplicas)"
  echo "Ejemplo: $0 1   (para escalar a 1 réplica)"
  exit 1
fi

REPLICAS=$1

echo "Escalando el StatefulSet '$STATEFULSET_NAME' en el namespace '$NAMESPACE' a $REPLICAS réplicas..."

kubectl scale statefulset "$STATEFULSET_NAME" --replicas="$REPLICAS" -n "$NAMESPACE"

if [ $? -eq 0 ]; then
  echo "Escalado de '$STATEFULSET_NAME' a $REPLICAS réplicas completado."
else
  echo "Error al escalar '$STATEFULSET_NAME'."
  exit 1
fi

# Opcional: Mostrar el estado de los pods de Ollama después de escalar
echo "Estado actual de los pods de Ollama:"
kubectl get pods -l app=ollama -n "$NAMESPACE"