"""
LLM Integration Example
=======================

Ejemplo de cómo integrar el servidor MCP de MongoDB con un LLM para que
pueda responder preguntas sobre los datos en tu base de datos.

Este script muestra cómo:
1. Proporcionar contexto de la base de datos al LLM
2. Permitir que el LLM ejecute consultas usando las herramientas MCP
3. Interpretar los resultados y responder preguntas del usuario
"""

import json
from mongodb_mcp import create_mongodb_mcp_server


class MongoDBContextProvider:
    """
    Proporciona contexto de MongoDB al LLM y ejecuta herramientas.
    """

    def __init__(self):
        """Initialize the context provider."""
        self.server = create_mongodb_mcp_server()
        self.context = None

    def get_database_context(self):
        """
        Obtiene un contexto resumido de la base de datos para el LLM.

        Retorna un diccionario con:
        - Nombre de la base de datos
        - Lista de colecciones con sus esquemas
        - Conteo de documentos
        - Campos disponibles
        """
        if self.context:
            return self.context

        context = {
            "database_name": "",
            "collections": []
        }

        # Listar colecciones
        result = self.server.execute_tool("mongodb_list_collections", {})
        result_data = json.loads(result)

        if not result_data.get("success"):
            return {"error": result_data.get("error")}

        context["database_name"] = result_data.get("database")

        # Para cada colección, obtener metadata
        for coll_name in result_data.get("collections", [])[:10]:  # Limitar a 10
            # Contar documentos
            count_result = self.server.execute_tool("mongodb_count", {
                "collection": coll_name,
                "filter_json": "{}"
            })
            count_data = json.loads(count_result)
            doc_count = count_data.get("count", 0) if count_data.get("success") else 0

            # Obtener documento de ejemplo
            sample_result = self.server.execute_tool("mongodb_find", {
                "collection": coll_name,
                "filter_json": "{}",
                "limit": 1
            })
            sample_data = json.loads(sample_result)

            fields = []
            sample_doc = None
            if sample_data.get("success") and sample_data.get("documents"):
                doc = sample_data["documents"][0]
                fields = [k for k in doc.keys() if k != "_id"]
                # Muestra simplificada (sin _id)
                sample_doc = {k: type(v).__name__ for k, v in doc.items() if k != "_id"}

            coll_info = {
                "name": coll_name,
                "document_count": doc_count,
                "fields": fields,
                "field_types": sample_doc
            }

            context["collections"].append(coll_info)

        self.context = context
        return context

    def get_system_prompt(self):
        """
        Genera un system prompt para el LLM con el contexto de MongoDB.
        """
        context = self.get_database_context()

        if "error" in context:
            return f"Error connecting to MongoDB: {context['error']}"

        prompt = f"""Tienes acceso a una base de datos MongoDB llamada '{context['database_name']}' con las siguientes colecciones:

"""

        for coll in context["collections"]:
            prompt += f"- **{coll['name']}** ({coll['document_count']:,} documentos)\n"
            prompt += f"  Campos: {', '.join(coll['fields'][:10])}\n"
            if len(coll['fields']) > 10:
                prompt += f"  ... (+{len(coll['fields']) - 10} campos más)\n"
            prompt += "\n"

        prompt += """
Puedes usar las siguientes herramientas para consultar los datos:

1. **mongodb_find**: Buscar documentos con filtros y paginación
2. **mongodb_count**: Contar documentos que cumplan un filtro
3. **mongodb_aggregate**: Ejecutar pipelines de agregación complejos
4. **mongodb_find_one**: Buscar un documento específico

Cuando el usuario haga preguntas sobre los datos:
1. Identifica qué colección(es) necesitas consultar
2. Construye la consulta apropiada en formato JSON
3. Ejecuta la herramienta correspondiente
4. Interpreta los resultados y responde en lenguaje natural

Ejemplos de consultas:

```json
// Buscar todos los documentos de una colección
{"collection": "usuarios", "filter_json": "{}", "limit": 10}

// Buscar con filtro
{"collection": "productos", "filter_json": "{\\"categoria\\": \\"electronics\\"}", "limit": 5}

// Contar documentos
{"collection": "ordenes", "filter_json": "{\\"status\\": \\"completed\\"}"}

// Agregación para estadísticas
{
  "collection": "ventas",
  "pipeline_json": "[{\\"$group\\": {\\"_id\\": \\"$categoria\\", \\"total\\": {\\"$sum\\": \\"$monto\\"}}}]"
}
```
"""

        return prompt

    def execute_tool(self, tool_name, parameters):
        """
        Ejecuta una herramienta MCP y retorna los resultados.

        Args:
            tool_name: Nombre de la herramienta (e.g., "mongodb_find")
            parameters: Diccionario con los parámetros de la herramienta

        Returns:
            Diccionario con los resultados parseados
        """
        result_json = self.server.execute_tool(tool_name, parameters)
        return json.loads(result_json)

    def close(self):
        """Cerrar conexiones."""
        self.server.close()


def example_conversation():
    """
    Simula una conversación donde el usuario hace preguntas sobre los datos.
    """
    print("=" * 70)
    print("Ejemplo de Conversación con LLM + MongoDB Context")
    print("=" * 70)

    provider = MongoDBContextProvider()

    # 1. Obtener contexto
    print("\n📋 Obteniendo contexto de la base de datos...")
    print("-" * 70)
    context = provider.get_database_context()

    if "error" in context:
        print(f"❌ Error: {context['error']}")
        return

    print(f"\n✅ Conectado a: {context['database_name']}")
    print(f"   Colecciones encontradas: {len(context['collections'])}")

    # 2. Mostrar system prompt
    print("\n\n🤖 System Prompt para el LLM:")
    print("-" * 70)
    system_prompt = provider.get_system_prompt()
    print(system_prompt[:500] + "...\n[truncado]")

    # 3. Ejemplo de preguntas del usuario y cómo el LLM respondería
    print("\n\n💬 Ejemplos de Conversación:")
    print("=" * 70)

    examples = [
        {
            "question": "¿Qué colecciones tienes disponibles?",
            "response": f"Tengo acceso a {len(context['collections'])} colecciones: {', '.join([c['name'] for c in context['collections'][:5]])}.",
            "tool_call": None
        },
        {
            "question": f"¿Cuántos documentos hay en '{context['collections'][0]['name']}'?" if context['collections'] else "¿Cuántos documentos hay?",
            "response": f"Hay {context['collections'][0]['document_count']:,} documentos en la colección '{context['collections'][0]['name']}'." if context['collections'] else "No hay colecciones.",
            "tool_call": {
                "tool": "mongodb_count",
                "params": {
                    "collection": context['collections'][0]['name'] if context['collections'] else "",
                    "filter_json": "{}"
                }
            } if context['collections'] else None
        }
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n{i}. Usuario: {example['question']}")

        if example['tool_call']:
            print(f"   → LLM ejecuta: {example['tool_call']['tool']}")
            print(f"     Parámetros: {json.dumps(example['tool_call']['params'], indent=6)}")

            # Ejecutar herramienta real
            result = provider.execute_tool(
                example['tool_call']['tool'],
                example['tool_call']['params']
            )

            if result.get("success"):
                print(f"   ← Resultado: {json.dumps(result, indent=6, default=str)[:200]}...")

        print(f"   💬 LLM: {example['response']}")

    # 4. Ejemplo avanzado: consulta con filtros
    if context['collections']:
        first_coll = context['collections'][0]
        print("\n\n📊 Ejemplo Avanzado: Consulta con Datos Reales")
        print("-" * 70)
        print(f"Usuario: Muéstrame 3 documentos de ejemplo de '{first_coll['name']}'")
        print(f"\n→ LLM ejecuta: mongodb_find")

        result = provider.execute_tool("mongodb_find", {
            "collection": first_coll['name'],
            "filter_json": "{}",
            "limit": 3
        })

        if result.get("success"):
            docs = result.get("documents", [])
            print(f"\n← Obtuvo {len(docs)} documentos")
            print(f"\n💬 LLM: Encontré {len(docs)} documentos en '{first_coll['name']}':")

            for i, doc in enumerate(docs, 1):
                # Remover _id para mejor visualización
                doc_display = {k: v for k, v in doc.items() if k != "_id"}
                print(f"\n   {i}. {json.dumps(doc_display, indent=6, default=str, ensure_ascii=False)[:150]}...")

    print("\n\n" + "=" * 70)
    print("✅ Ejemplo completado")
    print("=" * 70)

    # Cerrar
    provider.close()


def integration_guide():
    """
    Guía de integración con api_server.py
    """
    print("\n\n" + "=" * 70)
    print("📖 GUÍA DE INTEGRACIÓN")
    print("=" * 70)

    print("""
Para integrar este contexto MongoDB con tu API server existente:

1. **Modificar api_server.py** para incluir el contexto:

```python
from mcp_server.llm_integration_example import MongoDBContextProvider

# Al inicio
mongo_context = MongoDBContextProvider()
system_prompt = mongo_context.get_system_prompt()

# En el endpoint /chat
@app.post("/chat")
async def chat(request: ChatRequest):
    # Agregar system prompt con contexto MongoDB
    messages = [
        {"role": "system", "content": system_prompt},
        *request.messages
    ]

    # ... resto del código
```

2. **Permitir que el LLM use las herramientas**:

```python
# Definir herramientas disponibles
tools = [
    {
        "type": "function",
        "function": {
            "name": "mongodb_find",
            "description": "Buscar documentos en MongoDB",
            "parameters": {
                "type": "object",
                "properties": {
                    "collection": {"type": "string"},
                    "filter_json": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        }
    },
    # ... más herramientas
]

# Si el LLM llama una herramienta
if tool_call:
    result = mongo_context.execute_tool(
        tool_call.name,
        tool_call.parameters
    )
```

3. **Agregar endpoint específico para MongoDB**:

```python
@app.get("/mongodb/context")
async def get_mongodb_context():
    \"\"\"Obtener contexto de la base de datos.\"\"\"
    return mongo_context.get_database_context()

@app.post("/mongodb/query")
async def mongodb_query(collection: str, filter: dict, limit: int = 10):
    \"\"\"Consultar MongoDB directamente.\"\"\"
    result = mongo_context.execute_tool("mongodb_find", {
        "collection": collection,
        "filter_json": json.dumps(filter),
        "limit": limit
    })
    return result
```

4. **Ejemplo completo en el chat**:

El usuario pregunta: "¿Cuántos usuarios tengo?"

→ El LLM ve el contexto y sabe que hay una colección 'usuarios'
→ El LLM decide usar la herramienta mongodb_count
→ Ejecuta: mongodb_count(collection="usuarios", filter_json="{}")
→ Obtiene el resultado: {"success": true, "count": 1523}
→ Responde: "Tienes 1,523 usuarios en la base de datos."
""")


if __name__ == "__main__":
    # Ejecutar ejemplo
    example_conversation()

    # Mostrar guía de integración
    integration_guide()
