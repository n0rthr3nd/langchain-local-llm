# 🔧 Instrucciones para Reiniciar el Backend

## Problema
El dropdown de modelos muestra elementos vacíos porque el backend está ejecutando código antiguo.

## Solución Rápida

### Opción 1: Usar el script (Recomendado)
```bash
./restart-backend.sh
```

### Opción 2: Comando manual
```bash
docker compose restart langchain-api
```

## Verificar que funcionó

1. **Ver los logs** para confirmar que el nuevo código se ejecuta:
```bash
docker compose logs langchain-api | grep "DEBUG"
```

Deberías ver líneas como:
```
DEBUG - Raw Ollama response: ...
DEBUG - Processing model: ...
DEBUG - Extracted name: 'nomic-embed-text:latest'
DEBUG - Processed models: ...
```

2. **Verificar el endpoint** desde el navegador o curl:
```
http://localhost:3000/ia/chat/api/models
```

Deberías ver objetos, NO strings:
```json
{
  "models": [
    {
      "name": "nomic-embed-text:latest",
      "size": 12345,
      "modified_at": "2024-..."
    },
    {
      "name": "gemma2:2b",
      "size": 67890,
      "modified_at": "2024-..."
    }
  ]
}
```

## Si aún no funciona

Reiniciar todo:
```bash
docker compose down
docker compose up -d
```

## Verificar en el navegador

1. Abre las DevTools (F12)
2. Ve a Console
3. Recarga la página
4. Deberías ver:
```
DEBUG - ModelSelector received models: [{name: "nomic-embed-text:latest", ...}, ...]
DEBUG - Valid models after filter: [{name: "nomic-embed-text:latest", ...}, ...]
```

5. El dropdown ahora debería mostrar los nombres de los modelos correctamente
