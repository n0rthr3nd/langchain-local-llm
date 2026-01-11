# 🔧 Fix: Dropdown de Modelos Vacío

## 🎯 Problema

El dropdown de modelos muestra elementos vacíos en el frontend.

**Causa**: El backend está ejecutando código antiguo que retorna strings en lugar de objetos ModelInfo.

## ✅ Solución por Entorno

### 🐳 Docker Compose

Si usas `docker-compose`:

```bash
cd /home/user/langchain-local-llm

# Detener, reconstruir y reiniciar
docker compose down
docker compose build --no-cache
docker compose up -d

# Verificar logs
docker compose logs -f langchain-api | grep DEBUG
```

Alternativamente, usa el script rápido:
```bash
./restart-backend.sh
```

---

### ☸️ Kubernetes (k3s)

Si usas k8s (tu caso actual):

```bash
cd /home/user/langchain-local-llm

# Rebuild forzado sin caché + deploy
./k8s/scripts/rebuild-force.sh
```

Ver documentación completa en: [`k8s/DESPLIEGUE-K8S.md`](k8s/DESPLIEGUE-K8S.md)

---

## 🔍 Verificar que funcionó

### 1. Verificar endpoint

Abre en el navegador o usa curl:
```bash
# k8s
curl https://northr3nd.duckdns.org/ia/chat/api/models

# docker-compose
curl http://localhost:3000/ia/chat/api/models
```

**Respuesta correcta (objetos):**
```json
{
  "models": [
    {
      "name": "nomic-embed-text:latest",
      "size": 274290688,
      "modified_at": "2024-..."
    }
  ]
}
```

**Respuesta incorrecta (strings):**
```json
{"models": ["nomic-embed-text:latest", "gemma2:2b"]}
```

### 2. Verificar en el navegador

1. Abre la aplicación
2. Abre DevTools (F12) → Console
3. Haz clic en el botón de configuración
4. Verifica que el dropdown muestra los nombres completos
5. En la consola deberías ver:
```
DEBUG - ModelSelector received models: [{name: "...", ...}]
DEBUG - Valid models after filter: [{name: "...", ...}]
```

---

## 📋 Cambios Realizados

### Backend (`app/api_server.py`)

1. ✅ Cambió endpoint de `/models/v2` a `/models`
2. ✅ Retorna objetos `ModelInfo` completos con `name`, `size`, `modified_at`
3. ✅ Validación robusta de nombres de modelos
4. ✅ Filtrado de modelos con nombres vacíos
5. ✅ Fallback a modelo por defecto si no hay modelos válidos
6. ✅ Endpoint de debug `/models/raw`

### Frontend

1. ✅ Filtrado adicional de modelos vacíos
2. ✅ Logs de debug en consola
3. ✅ Fallback a modelos por defecto

---

## 🐛 Troubleshooting

### Después de rebuild sigue sin funcionar

**Docker Compose:**
```bash
# Forzar eliminación de volúmenes y caché
docker compose down -v
docker system prune -f
docker compose build --no-cache
docker compose up -d
```

**Kubernetes:**
```bash
# Ver si los pods se recrearon
kubectl get pods -n llm-services -o wide

# Eliminar pods manualmente
kubectl delete pods -n llm-services -l app=langchain-api
kubectl delete pods -n llm-services -l app=langchain-frontend

# Ver logs
kubectl logs -n llm-services -l app=langchain-api -f
```

### El navegador muestra datos viejos

1. Limpia la caché del navegador (Ctrl + Shift + Delete)
2. Recarga con Ctrl + Shift + R (hard reload)
3. Prueba en una ventana de incógnito

---

## 📞 Soporte

Si después de seguir estos pasos el problema persiste:

1. Comparte los logs del backend
2. Comparte el resultado de `/models` y `/models/raw`
3. Comparte los logs de la consola del navegador

---

## 🎉 Resultado Esperado

Después de aplicar el fix, el dropdown debería:

- ✅ Mostrar nombres completos de modelos (ej: "nomic-embed-text:latest", "gemma2:2b")
- ✅ NO mostrar elementos vacíos
- ✅ Cargar modelos dinámicamente desde Ollama
- ✅ Tener fallback a modelos por defecto si hay errores

---

**Última actualización**: 2026-01-11
**Branch**: `claude/fix-dropdown-model-display-U8224`
