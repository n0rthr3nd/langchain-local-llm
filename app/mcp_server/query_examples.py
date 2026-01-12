"""
Query Examples for MongoDB MCP Server
======================================

Este script muestra ejemplos de cómo usar el servidor MCP para consultar
una base de datos MongoDB existente y proporcionar contexto al LLM.

Casos de uso principales:
1. Explorar la estructura de la base de datos (colecciones, esquemas)
2. Consultar datos específicos
3. Obtener estadísticas y agregaciones
4. Proporcionar contexto al LLM sobre los datos disponibles
"""

import json
from mongodb_mcp import create_mongodb_mcp_server


def explore_database(server):
    """Explorar la estructura de la base de datos."""
    print("\n" + "=" * 70)
    print("🔍 EXPLORACIÓN DE LA BASE DE DATOS")
    print("=" * 70)

    # 1. Listar todas las colecciones
    print("\n📚 Colecciones disponibles:")
    print("-" * 70)
    result = server.execute_tool("mongodb_list_collections", {})
    result_data = json.loads(result)

    if result_data.get("success"):
        collections = result_data.get("collections", [])
        print(f"Base de datos: {result_data['database']}")
        print(f"Total de colecciones: {len(collections)}\n")

        for i, coll in enumerate(collections, 1):
            print(f"  {i}. {coll}")

            # Obtener conteo de documentos en cada colección
            count_result = server.execute_tool("mongodb_count", {
                "collection": coll,
                "filter_json": "{}"
            })
            count_data = json.loads(count_result)

            if count_data.get("success"):
                count = count_data.get("count", 0)
                print(f"     └─ Documentos: {count:,}")

            # Obtener un documento de ejemplo para ver el esquema
            sample_result = server.execute_tool("mongodb_find", {
                "collection": coll,
                "filter_json": "{}",
                "limit": 1
            })
            sample_data = json.loads(sample_result)

            if sample_data.get("success") and sample_data.get("documents"):
                doc = sample_data["documents"][0]
                fields = list(doc.keys())
                print(f"     └─ Campos: {', '.join(fields[:5])}", end="")
                if len(fields) > 5:
                    print(f" ... (+{len(fields) - 5} más)")
                else:
                    print()

        return collections
    else:
        print(f"❌ Error: {result_data.get('error')}")
        return []


def query_collection_examples(server, collection_name):
    """Ejemplos de consultas a una colección específica."""
    print("\n" + "=" * 70)
    print(f"🔎 EJEMPLOS DE CONSULTAS - Colección: {collection_name}")
    print("=" * 70)

    # 1. Obtener primeros documentos
    print("\n📄 Primeros 5 documentos:")
    print("-" * 70)
    result = server.execute_tool("mongodb_find", {
        "collection": collection_name,
        "filter_json": "{}",
        "limit": 5
    })
    result_data = json.loads(result)

    if result_data.get("success"):
        docs = result_data.get("documents", [])
        for i, doc in enumerate(docs, 1):
            # Remover _id para mejor legibilidad
            doc_copy = {k: v for k, v in doc.items() if k != "_id"}
            print(f"\n{i}. {json.dumps(doc_copy, indent=2, default=str, ensure_ascii=False)[:200]}...")
    else:
        print(f"❌ Error: {result_data.get('error')}")

    # 2. Contar documentos
    print("\n\n📊 Estadísticas:")
    print("-" * 70)
    count_result = server.execute_tool("mongodb_count", {
        "collection": collection_name,
        "filter_json": "{}"
    })
    count_data = json.loads(count_result)

    if count_data.get("success"):
        total = count_data.get("count", 0)
        print(f"Total de documentos: {total:,}")


def aggregation_examples(server, collection_name):
    """Ejemplos de agregaciones para obtener insights."""
    print("\n" + "=" * 70)
    print(f"📈 AGREGACIONES - Colección: {collection_name}")
    print("=" * 70)

    # Intentar obtener un documento para ver campos disponibles
    sample_result = server.execute_tool("mongodb_find", {
        "collection": collection_name,
        "filter_json": "{}",
        "limit": 1
    })
    sample_data = json.loads(sample_result)

    if not sample_data.get("success") or not sample_data.get("documents"):
        print("❌ No se pudo obtener documento de ejemplo")
        return

    doc = sample_data["documents"][0]
    fields = [k for k in doc.keys() if k != "_id"]

    print(f"\nCampos disponibles: {', '.join(fields[:10])}")
    print("\nEjemplos de agregaciones que puedes hacer:")
    print("-" * 70)

    # Ejemplo 1: Agrupar por un campo (si existe un campo categórico)
    categorical_fields = []
    for field in fields[:5]:  # Revisar primeros 5 campos
        value = doc.get(field)
        if isinstance(value, (str, bool)) or (isinstance(value, (int, float)) and value < 100):
            categorical_fields.append(field)

    if categorical_fields:
        field = categorical_fields[0]
        print(f"\n1. Contar documentos agrupados por '{field}':")
        print(f"""
        pipeline = [
            {{"$group": {{
                "_id": "${field}",
                "count": {{"$sum": 1}}
            }}}},
            {{"$sort": {{"count": -1}}}},
            {{"$limit": 10}}
        ]
        """)

    # Ejemplo 2: Estadísticas de campos numéricos
    numeric_fields = []
    for field in fields[:10]:
        value = doc.get(field)
        if isinstance(value, (int, float)) and field != "_id":
            numeric_fields.append(field)

    if numeric_fields:
        field = numeric_fields[0]
        print(f"\n2. Estadísticas de '{field}':")
        print(f"""
        pipeline = [
            {{"$group": {{
                "_id": null,
                "promedio": {{"$avg": "${field}"}},
                "minimo": {{"$min": "${field}"}},
                "maximo": {{"$max": "${field}"}},
                "total": {{"$sum": "${field}"}}
            }}}}
        ]
        """)


def provide_context_for_llm(server):
    """
    Proporcionar contexto estructurado para el LLM.

    Este es el caso de uso principal: explorar la base de datos y
    proporcionar un resumen estructurado que el LLM puede usar para
    responder preguntas del usuario.
    """
    print("\n" + "=" * 70)
    print("🤖 CONTEXTO PARA LLM")
    print("=" * 70)

    context = {
        "database": {},
        "collections": []
    }

    # Obtener colecciones
    result = server.execute_tool("mongodb_list_collections", {})
    result_data = json.loads(result)

    if not result_data.get("success"):
        print(f"❌ Error: {result_data.get('error')}")
        return None

    context["database"]["name"] = result_data.get("database")
    context["database"]["total_collections"] = result_data.get("count")

    # Para cada colección, obtener metadata
    for coll_name in result_data.get("collections", []):
        coll_info = {"name": coll_name}

        # Contar documentos
        count_result = server.execute_tool("mongodb_count", {
            "collection": coll_name,
            "filter_json": "{}"
        })
        count_data = json.loads(count_result)
        coll_info["document_count"] = count_data.get("count", 0) if count_data.get("success") else 0

        # Obtener documento de ejemplo para schema
        sample_result = server.execute_tool("mongodb_find", {
            "collection": coll_name,
            "filter_json": "{}",
            "limit": 1
        })
        sample_data = json.loads(sample_result)

        if sample_data.get("success") and sample_data.get("documents"):
            doc = sample_data["documents"][0]

            # Analizar tipos de campos
            fields_info = []
            for field, value in doc.items():
                if field == "_id":
                    continue

                field_type = type(value).__name__
                field_info = {
                    "name": field,
                    "type": field_type,
                    "sample_value": str(value)[:50] if value else None
                }
                fields_info.append(field_info)

            coll_info["fields"] = fields_info
            coll_info["sample_document"] = {k: v for k, v in list(doc.items())[:5] if k != "_id"}

        context["collections"].append(coll_info)

    # Imprimir contexto formateado
    print("\n📋 Contexto estructurado de la base de datos:")
    print("-" * 70)
    print(json.dumps(context, indent=2, default=str, ensure_ascii=False))

    print("\n\n💡 Cómo usar este contexto:")
    print("-" * 70)
    print("""
Este contexto puede proporcionarse al LLM para que pueda:

1. Responder preguntas sobre qué datos están disponibles
2. Sugerir consultas relevantes basadas en los campos
3. Ejecutar consultas específicas usando las herramientas MCP
4. Proporcionar insights sobre los datos

Ejemplo de prompt para el LLM:
\"\"\"
Tienes acceso a una base de datos MongoDB con el siguiente contexto:
[INSERTAR CONTEXTO JSON AQUÍ]

El usuario puede preguntarte sobre estos datos y tú puedes usar las
herramientas mongodb_find, mongodb_aggregate, etc. para responder.
\"\"\"
    """)

    return context


def main():
    """Ejecutar todos los ejemplos."""
    print("=" * 70)
    print("MongoDB MCP Server - Ejemplos de Consulta")
    print("=" * 70)
    print("\nConectando a MongoDB...")

    try:
        server = create_mongodb_mcp_server()

        # 1. Explorar base de datos
        collections = explore_database(server)

        if not collections:
            print("\n⚠️  No se encontraron colecciones o no se pudo conectar.")
            print("    Verifica tu configuración en .env")
            return

        # 2. Si hay colecciones, mostrar ejemplos con la primera
        if collections:
            first_collection = collections[0]

            # Ejemplos de consultas
            query_collection_examples(server, first_collection)

            # Ejemplos de agregaciones
            aggregation_examples(server, first_collection)

        # 3. Generar contexto para LLM
        provide_context_for_llm(server)

        print("\n" + "=" * 70)
        print("✅ Ejemplos completados")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nVerifica:")
        print("1. MongoDB está accesible")
        print("2. Variables de entorno en .env están configuradas")
        print("3. URI de conexión es correcta")

    finally:
        try:
            server.close()
        except:
            pass


if __name__ == "__main__":
    main()
