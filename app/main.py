"""
LangChain + Ollama: Aplicacion Principal
Ejemplos practicos de uso con LLM local
"""
import os
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Configuracion
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2")


def get_llm(model: str = MODEL_NAME, temperature: float = 0.7):
    """Obtener instancia del LLM configurada."""
    return ChatOllama(
        model=model,
        base_url=OLLAMA_BASE_URL,
        temperature=temperature,
    )


# =============================================================================
# EJEMPLO 1: Chat Simple
# =============================================================================
def ejemplo_chat_simple():
    """Ejemplo basico de chat con el LLM."""
    print("\n" + "="*60)
    print("EJEMPLO 1: Chat Simple")
    print("="*60)

    llm = get_llm()

    # Forma mas simple
    response = llm.invoke("Explica que es LangChain en 2 oraciones.")
    print(f"\nRespuesta: {response.content}")


# =============================================================================
# EJEMPLO 2: Chat con Prompt Template
# =============================================================================
def ejemplo_prompt_template():
    """Ejemplo usando templates de prompts."""
    print("\n" + "="*60)
    print("EJEMPLO 2: Prompt Template")
    print("="*60)

    llm = get_llm()

    # Crear template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un experto en {tema}. Responde de forma concisa y tecnica."),
        ("human", "{pregunta}")
    ])

    # Crear chain
    chain = prompt | llm | StrOutputParser()

    # Ejecutar
    response = chain.invoke({
        "tema": "arquitectura de software",
        "pregunta": "Que es el patron CQRS y cuando usarlo?"
    })

    print(f"\nRespuesta: {response}")


# =============================================================================
# EJEMPLO 3: Conversacion con Memoria
# =============================================================================
def ejemplo_conversacion_con_memoria():
    """Ejemplo de chat con historial de conversacion."""
    print("\n" + "="*60)
    print("EJEMPLO 3: Conversacion con Memoria")
    print("="*60)

    llm = get_llm()

    # Template con historial
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un asistente util. Mantiene el contexto de la conversacion."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    chain = prompt | llm | StrOutputParser()

    # Simular conversacion
    history = []

    # Turno 1
    user_msg1 = "Me llamo Carlos y estoy aprendiendo Python."
    history.append(HumanMessage(content=user_msg1))
    response1 = chain.invoke({"history": history, "input": user_msg1})
    history.append(AIMessage(content=response1))
    print(f"\nUsuario: {user_msg1}")
    print(f"Asistente: {response1}")

    # Turno 2
    user_msg2 = "Que lenguaje estoy aprendiendo? Y como me llamo?"
    history.append(HumanMessage(content=user_msg2))
    response2 = chain.invoke({"history": history, "input": user_msg2})
    print(f"\nUsuario: {user_msg2}")
    print(f"Asistente: {response2}")


# =============================================================================
# EJEMPLO 4: Chain de Multiples Pasos
# =============================================================================
def ejemplo_chain_multiples_pasos():
    """Ejemplo de procesamiento en multiples pasos."""
    print("\n" + "="*60)
    print("EJEMPLO 4: Chain de Multiples Pasos")
    print("="*60)

    llm = get_llm()

    # Paso 1: Generar idea
    prompt_idea = ChatPromptTemplate.from_template(
        "Genera una idea innovadora para una app movil en el sector de {sector}. "
        "Solo da la idea en una oracion."
    )

    # Paso 2: Expandir idea
    prompt_expansion = ChatPromptTemplate.from_template(
        "Dada esta idea de app: {idea}\n\n"
        "Lista 3 caracteristicas principales que deberia tener."
    )

    # Paso 3: Evaluar
    prompt_evaluacion = ChatPromptTemplate.from_template(
        "Evalua esta propuesta de app:\n"
        "Idea: {idea}\n"
        "Caracteristicas: {caracteristicas}\n\n"
        "Da una puntuacion del 1-10 y justifica brevemente."
    )

    # Ejecutar chain
    chain_idea = prompt_idea | llm | StrOutputParser()
    chain_expansion = prompt_expansion | llm | StrOutputParser()
    chain_evaluacion = prompt_evaluacion | llm | StrOutputParser()

    # Paso 1
    idea = chain_idea.invoke({"sector": "salud mental"})
    print(f"\nIdea generada: {idea}")

    # Paso 2
    caracteristicas = chain_expansion.invoke({"idea": idea})
    print(f"\nCaracteristicas: {caracteristicas}")

    # Paso 3
    evaluacion = chain_evaluacion.invoke({
        "idea": idea,
        "caracteristicas": caracteristicas
    })
    print(f"\nEvaluacion: {evaluacion}")


# =============================================================================
# EJEMPLO 5: Streaming de Respuestas
# =============================================================================
def ejemplo_streaming():
    """Ejemplo de streaming para respuestas largas."""
    print("\n" + "="*60)
    print("EJEMPLO 5: Streaming de Respuestas")
    print("="*60)

    llm = get_llm()

    print("\nGenerando respuesta con streaming:")
    print("-" * 40)

    for chunk in llm.stream("Escribe un poema corto sobre programacion."):
        print(chunk.content, end="", flush=True)

    print("\n" + "-" * 40)


# =============================================================================
# EJEMPLO 6: Estructurar Salida (JSON)
# =============================================================================
def ejemplo_salida_estructurada():
    """Ejemplo para obtener respuestas en formato estructurado."""
    print("\n" + "="*60)
    print("EJEMPLO 6: Salida Estructurada (JSON)")
    print("="*60)

    llm = get_llm(temperature=0.1)  # Temperatura baja para precision

    prompt = ChatPromptTemplate.from_template("""
Analiza el siguiente texto y extrae informacion en formato JSON.

Texto: "{texto}"

Responde SOLO con un JSON valido con esta estructura:
{{
    "sentimiento": "positivo|negativo|neutral",
    "temas_principales": ["tema1", "tema2"],
    "resumen": "resumen en una oracion"
}}
""")

    chain = prompt | llm | StrOutputParser()

    texto = """
    El nuevo framework de Python ha revolucionado la forma en que construimos
    aplicaciones web. Aunque tiene una curva de aprendizaje inicial, los
    beneficios en productividad son enormes. El equipo de desarrollo ha
    respondido rapidamente a los bugs reportados.
    """

    response = chain.invoke({"texto": texto})
    print(f"\nAnalisis estructurado:\n{response}")


# =============================================================================
# MAIN
# =============================================================================
def main():
    """Ejecutar todos los ejemplos."""
    print("\n" + "#"*60)
    print("# LangChain + Ollama: Ejemplos Practicos")
    print(f"# Modelo: {MODEL_NAME}")
    print(f"# Servidor: {OLLAMA_BASE_URL}")
    print("#"*60)

    try:
        # Verificar conexion
        llm = get_llm()
        test = llm.invoke("Di 'OK' si funcionas.")
        print(f"\n[OK] Conexion exitosa con Ollama")

        # Ejecutar ejemplos
        ejemplo_chat_simple()
        ejemplo_prompt_template()
        ejemplo_conversacion_con_memoria()
        ejemplo_chain_multiples_pasos()
        ejemplo_streaming()
        ejemplo_salida_estructurada()

        print("\n" + "="*60)
        print("Todos los ejemplos completados!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n[ERROR] No se pudo conectar con Ollama: {e}")
        print("Asegurate de que Ollama esta corriendo y el modelo descargado.")
        print(f"Ejecuta: docker exec ollama-server ollama pull {MODEL_NAME}")


if __name__ == "__main__":
    main()
