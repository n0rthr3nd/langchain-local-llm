# 🚀 Despliegue en Kubernetes (k3s)

## Problema: Dropdown de modelos vacío

Si el dropdown de modelos muestra elementos vacíos después de desplegar, es porque el código del backend no se actualizó correctamente.

## ✅ Solución Rápida

### Opción 1: Rebuild Forzado (Recomendado) ⚡

Usa el script que **fuerza reconstrucción sin caché** y **elimina los pods** para garantizar que se usen las nuevas imágenes:

```bash
cd /home/user/langchain-local-llm
./k8s/scripts/rebuild-force.sh
```

Este script:
1. ✅ Elimina imágenes viejas localmente
2. ✅ Reconstruye Backend SIN CACHE
3. ✅ Reconstruye Frontend SIN CACHE
4. ✅ Elimina imágenes viejas de k3s
5. ✅ Importa imágenes nuevas a k3s
6. ✅ Elimina los pods para forzar recreación con nuevas imágenes
7. ✅ Espera a que los nuevos pods estén listos

**Tiempo estimado: 5-10 minutos** (por la reconstrucción sin caché)

---

### Opción 2: Build + Deploy Normal

Si prefieres usar los scripts normales:

```bash
cd /home/user/langchain-local-llm/k8s/scripts

# 1. Construir e importar imágenes
./build-and-push.sh

# 2. Desplegar (incluye rollout restart)
./deploy.sh
```

⚠️ **Problema**: Si Docker usa caché, los cambios pueden no aplicarse.

---

### Opción 3: Reinicio Manual de Pods

Si ya ejecutaste build-and-push.sh pero los cambios no se ven:

```bash
# Eliminar pods para forzar recreación
kubectl delete pods -n llm-services -l app=langchain-api
kubectl delete pods -n llm-services -l app=langchain-frontend

# Verificar que se recrearon
kubectl get pods -n llm-services -w
```

---

## 🔍 Verificar que funcionó

### 1. Ver los logs del backend

```bash
kubectl logs -n llm-services -l app=langchain-api -f
```

Deberías ver líneas como:
```
DEBUG - Raw Ollama response: ...
DEBUG - Processing model: ...
DEBUG - Extracted name: 'nomic-embed-text:latest'
DEBUG - Processed models: [{'name': 'nomic-embed-text:latest', ...}]
```

### 2. Probar el endpoint desde el navegador

Abre:
```
https://northr3nd.duckdns.org/ia/chat/api/models
```

Deberías ver **objetos**, NO strings:
```json
{
  "models": [
    {
      "name": "nomic-embed-text:latest",
      "size": 274290688,
      "modified_at": "2024-..."
    },
    {
      "name": "gemma2:2b",
      "size": 1628553088,
      "modified_at": "2024-..."
    }
  ]
}
```

❌ **Si ves esto, el backend NO se actualizó:**
```json
{"models": ["nomic-embed-text:latest", "gemma2:2b"]}
```

### 3. Probar el dropdown

1. Abre `https://northr3nd.duckdns.org/ia/chat`
2. Haz clic en el botón de configuración (⚙️)
3. El dropdown de "Modelo" debería mostrar los nombres completos
4. Abre DevTools (F12) → Console
5. Deberías ver:
```
DEBUG - ModelSelector received models: [{name: "nomic-embed-text:latest", ...}, ...]
DEBUG - Valid models after filter: [{name: "nomic-embed-text:latest", ...}, ...]
```

---

## 🐛 Troubleshooting

### Los cambios aún no se ven después de rebuild-force.sh

1. **Verificar que las imágenes se importaron a k3s:**
```bash
sudo ctr -n k8s.io images ls | grep langchain
```

Deberías ver:
```
docker.io/library/langchain-app:latest
docker.io/library/langchain-frontend:latest
```

2. **Verificar que los pods se recrearon:**
```bash
kubectl get pods -n llm-services -o wide
```

Los pods deben tener un AGE reciente (menos de 5 minutos)

3. **Ver logs de errores:**
```bash
# Backend
kubectl logs -n llm-services -l app=langchain-api --tail=100

# Frontend
kubectl logs -n llm-services -l app=langchain-frontend --tail=100
```

### El endpoint /models/raw no funciona

Verifica que el proxy de nginx esté configurado correctamente:

```bash
kubectl describe ingress -n llm-services
```

---

## 📊 Monitoreo

### Ver estado de todos los pods
```bash
kubectl get pods -n llm-services
```

### Ver logs en tiempo real
```bash
# Backend
kubectl logs -n llm-services -l app=langchain-api -f

# Frontend
kubectl logs -n llm-services -l app=langchain-frontend -f

# Ollama
kubectl logs -n llm-services -l app=ollama -f
```

### Ver uso de recursos
```bash
kubectl top pods -n llm-services
```

---

## 🧹 Limpieza (Opcional)

Si quieres eliminar todo y volver a empezar:

```bash
cd /home/user/langchain-local-llm/k8s/scripts
./undeploy.sh
```

Luego vuelve a desplegar con `./rebuild-force.sh`

---

## 📝 Notas Importantes

- **Siempre usa `rebuild-force.sh`** cuando hagas cambios en el código de backend o frontend
- El script normal `build-and-push.sh` + `deploy.sh` puede usar caché de Docker y no aplicar los cambios
- Los logs de debug se agregaron específicamente para diagnosticar este problema
- Una vez confirmado que funciona, puedes eliminar los logs de debug si quieres reducir el ruido en los logs

---

## 🎯 Resumen

**Para aplicar cambios de código:**
```bash
./k8s/scripts/rebuild-force.sh
```

**Para verificar:**
```bash
# 1. Ver logs
kubectl logs -n llm-services -l app=langchain-api -f | grep DEBUG

# 2. Probar endpoint
curl https://northr3nd.duckdns.org/ia/chat/api/models

# 3. Abrir navegador y verificar dropdown
```

✅ **El dropdown debería mostrar los nombres de los modelos correctamente**
