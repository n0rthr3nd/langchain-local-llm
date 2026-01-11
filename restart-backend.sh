#!/bin/bash
# Script para reiniciar solo el backend y ver los logs

echo "🔄 Reiniciando el backend..."
docker compose restart langchain-api

echo "⏳ Esperando 5 segundos..."
sleep 5

echo "📋 Mostrando logs del backend (Ctrl+C para salir):"
docker compose logs -f langchain-api
