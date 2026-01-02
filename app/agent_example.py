"""
LangChain + Ollama: Ejemplo de Agente con Herramientas
Agente que puede usar herramientas para resolver tareas
"""
import os
from datetime import datetime
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Configuracion
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2")


# =============================================================================
# Definir Herramientas
# =============================================================================
@tool
def calcular(expresion: str) -> str:
    """
    Calcula una expresion matematica.
    Usa esta herramienta para operaciones aritmeticas.
    Ejemplo: calcular("2 + 2") devuelve "4"
    """
    try:
        # Evaluar de forma segura (solo operaciones matematicas)
        allowed_chars = set("0123456789+-*/().% ")
        if not all(c in allowed_chars for c in expresion):
            return "Error: Solo se permiten operaciones matematicas basicas"
        result = eval(expresion)
        return str(result)
    except Exception as e:
        return f"Error en calculo: {e}"


@tool
def obtener_fecha_hora() -> str:
    """
    Obtiene la fecha y hora actual.
    Usa esta herramienta cuando necesites saber la fecha o hora.
    """
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")


@tool
def buscar_en_base_conocimiento(query: str) -> str:
    """
    Busca informacion en la base de conocimiento local.
    Usa esta herramienta para buscar datos sobre productos, precios o politicas.
    """
    # Simular base de conocimiento
    knowledge_base = {
        "precios": {
            "plan_basico": "9.99 USD/mes",
            "plan_pro": "29.99 USD/mes",
            "plan_enterprise": "99.99 USD/mes"
        },
        "horarios": {
            "soporte": "Lunes a Viernes, 9:00 - 18:00",
            "ventas": "Lunes a Sabado, 8:00 - 20:00"
        },
        "politicas": {
            "devolucion": "30 dias para devoluciones con recibo",
            "garantia": "1 anio de garantia en todos los productos"
        }
    }

    query_lower = query.lower()

    # Buscar en categorias
    for categoria, items in knowledge_base.items():
        if categoria in query_lower:
            return f"Informacion de {categoria}: {items}"
        for key, value in items.items():
            if key in query_lower:
                return f"{key}: {value}"

    return "No encontre informacion especifica. Categorias disponibles: precios, horarios, politicas"


@tool
def convertir_unidades(valor: float, de_unidad: str, a_unidad: str) -> str:
    """
    Convierte entre unidades de medida.
    Soporta: km/mi, kg/lb, c/f (celsius/fahrenheit)

    Args:
        valor: El valor numerico a convertir
        de_unidad: Unidad de origen (km, mi, kg, lb, c, f)
        a_unidad: Unidad de destino
    """
    conversiones = {
        ("km", "mi"): lambda x: x * 0.621371,
        ("mi", "km"): lambda x: x * 1.60934,
        ("kg", "lb"): lambda x: x * 2.20462,
        ("lb", "kg"): lambda x: x * 0.453592,
        ("c", "f"): lambda x: (x * 9/5) + 32,
        ("f", "c"): lambda x: (x - 32) * 5/9,
    }

    key = (de_unidad.lower(), a_unidad.lower())
    if key in conversiones:
        resultado = conversiones[key](valor)
        return f"{valor} {de_unidad} = {resultado:.2f} {a_unidad}"
    else:
        return f"Conversion no soportada. Soportadas: km<->mi, kg<->lb, c<->f"


# =============================================================================
# Crear Agente
# =============================================================================
def crear_agente():
    """Crear agente con herramientas."""

    # LLM con soporte para tool calling
    llm = ChatOllama(
        model=MODEL_NAME,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )

    # Lista de herramientas
    tools = [
        calcular,
        obtener_fecha_hora,
        buscar_en_base_conocimiento,
        convertir_unidades
    ]

    # Prompt del agente
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Eres un asistente util con acceso a varias herramientas.
Usa las herramientas cuando sea necesario para responder preguntas.
Si no necesitas herramientas, responde directamente.

Herramientas disponibles:
- calcular: Para operaciones matematicas
- obtener_fecha_hora: Para saber fecha/hora actual
- buscar_en_base_conocimiento: Para info de productos, precios, horarios
- convertir_unidades: Para conversiones de unidades"""),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    # Crear agente
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )

    return agent_executor


# =============================================================================
# Demo
# =============================================================================
def main():
    """Demo del agente."""
    print("\n" + "#"*60)
    print("# Agente LangChain con Herramientas")
    print("#"*60)

    try:
        agent = crear_agente()

        preguntas = [
            "Que hora es?",
            "Cuanto es 15% de 250?",
            "Cuales son los precios de los planes?",
            "Convierte 100 km a millas",
            "Si tengo 3 productos de 45.50 USD cada uno, cuanto pago en total con 10% de descuento?"
        ]

        for pregunta in preguntas:
            print(f"\n{'='*60}")
            print(f"Usuario: {pregunta}")
            print("-"*60)

            resultado = agent.invoke({
                "input": pregunta,
                "chat_history": []
            })

            print(f"\nRespuesta: {resultado['output']}")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nNota: El agente con herramientas requiere un modelo que soporte")
        print("tool calling. Prueba con modelos mas recientes como llama3.2 o mistral.")


if __name__ == "__main__":
    main()
