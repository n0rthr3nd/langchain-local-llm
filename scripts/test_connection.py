#!/usr/bin/env python3
"""
Script de prueba rapida para verificar la conexion con Ollama.
Ejecutar desde Windows (sin Docker) o dentro del contenedor.
"""
import sys
import httpx

def test_ollama_connection(base_url: str = "http://localhost:11434"):
    """Verificar conexion con Ollama."""
    print(f"Probando conexion con Ollama en: {base_url}")
    print("-" * 50)

    # Test 1: Health check
    print("\n[1] Health check...")
    try:
        response = httpx.get(f"{base_url}/api/tags", timeout=10)
        if response.status_code == 200:
            print("    OK: Ollama esta respondiendo")
            models = response.json().get("models", [])
            if models:
                print(f"    Modelos instalados: {len(models)}")
                for m in models:
                    print(f"      - {m['name']} ({m.get('size', 'N/A')})")
            else:
                print("    AVISO: No hay modelos instalados")
                print("    Ejecuta: docker exec ollama-server ollama pull llama3.2")
                return False
        else:
            print(f"    ERROR: Status {response.status_code}")
            return False
    except httpx.ConnectError:
        print("    ERROR: No se puede conectar con Ollama")
        print("    Verifica que el contenedor este corriendo:")
        print("    docker-compose up -d ollama")
        return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

    # Test 2: Generacion simple
    print("\n[2] Probando generacion...")
    try:
        model_name = models[0]["name"] if models else "llama3.2"
        response = httpx.post(
            f"{base_url}/api/generate",
            json={
                "model": model_name,
                "prompt": "Di 'hola' en una palabra",
                "stream": False
            },
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            print(f"    OK: Modelo {model_name} respondio")
            print(f"    Respuesta: {result.get('response', 'N/A')[:100]}")
        else:
            print(f"    ERROR: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"    ERROR en generacion: {e}")
        return False

    print("\n" + "=" * 50)
    print("EXITO: Ollama esta funcionando correctamente!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:11434"
    success = test_ollama_connection(url)
    sys.exit(0 if success else 1)
