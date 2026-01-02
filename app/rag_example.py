"""
LangChain + Ollama: Ejemplo de RAG (Retrieval Augmented Generation)
Sistema de preguntas y respuestas sobre documentos locales
"""
import os
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Configuracion
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
CHROMA_PERSIST_DIR = "./chroma_db"


class RAGSystem:
    """Sistema RAG con LangChain y Ollama."""

    def __init__(self):
        self.llm = ChatOllama(
            model=MODEL_NAME,
            base_url=OLLAMA_BASE_URL,
            temperature=0.3,
        )

        # Embeddings locales con Ollama
        self.embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL,
        )

        self.vectorstore = None
        self.retriever = None

    def cargar_documentos(self, ruta: str):
        """Cargar documentos desde una ruta."""
        print(f"Cargando documentos desde: {ruta}")

        # Cargar archivos .txt
        if os.path.isdir(ruta):
            loader = DirectoryLoader(ruta, glob="**/*.txt", loader_cls=TextLoader)
        else:
            loader = TextLoader(ruta)

        documents = loader.load()
        print(f"Documentos cargados: {len(documents)}")

        # Dividir en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Chunks creados: {len(chunks)}")

        # Crear vectorstore
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )

        # Crear retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}  # Top 3 documentos
        )

        print("Vectorstore creado exitosamente!")
        return len(chunks)

    def cargar_vectorstore_existente(self):
        """Cargar vectorstore desde disco."""
        if os.path.exists(CHROMA_PERSIST_DIR):
            self.vectorstore = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings,
            )
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            print("Vectorstore cargado desde disco.")
            return True
        return False

    def preguntar(self, pregunta: str) -> str:
        """Hacer una pregunta sobre los documentos."""
        if not self.retriever:
            return "Error: No hay documentos cargados."

        # Template para RAG
        template = """Responde la pregunta basandote SOLO en el siguiente contexto.
Si no encuentras la respuesta en el contexto, di "No tengo informacion sobre eso."

Contexto:
{context}

Pregunta: {question}

Respuesta:"""

        prompt = ChatPromptTemplate.from_template(template)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # RAG Chain
        rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return rag_chain.invoke(pregunta)

    def buscar_similares(self, query: str, k: int = 3):
        """Buscar documentos similares sin generar respuesta."""
        if not self.vectorstore:
            return []
        return self.vectorstore.similarity_search(query, k=k)


# =============================================================================
# Demo
# =============================================================================
def crear_documentos_ejemplo():
    """Crear documentos de ejemplo para la demo."""
    docs_dir = "./documentos_ejemplo"
    os.makedirs(docs_dir, exist_ok=True)

    doc1 = """
    Guia de Python para Principiantes

    Python es un lenguaje de programacion interpretado de alto nivel.
    Fue creado por Guido van Rossum y lanzado en 1991.

    Caracteristicas principales:
    - Sintaxis clara y legible
    - Tipado dinamico
    - Gestion automatica de memoria
    - Gran biblioteca estandar

    Python se usa en:
    - Desarrollo web (Django, Flask)
    - Ciencia de datos (Pandas, NumPy)
    - Inteligencia artificial (TensorFlow, PyTorch)
    - Automatizacion y scripting
    """

    doc2 = """
    Introduccion a Docker

    Docker es una plataforma de contenedores que permite empaquetar
    aplicaciones con todas sus dependencias.

    Conceptos clave:
    - Imagen: Template de solo lectura con instrucciones
    - Contenedor: Instancia ejecutable de una imagen
    - Dockerfile: Archivo de texto con instrucciones para construir imagenes
    - Docker Compose: Herramienta para definir aplicaciones multi-contenedor

    Ventajas de Docker:
    - Portabilidad entre entornos
    - Aislamiento de aplicaciones
    - Despliegue consistente
    - Eficiencia de recursos vs VMs
    """

    doc3 = """
    LangChain: Framework para LLMs

    LangChain es un framework para desarrollar aplicaciones con LLMs.

    Componentes principales:
    - Models: Integracion con diversos LLMs (OpenAI, Anthropic, Ollama)
    - Prompts: Templates y gestion de prompts
    - Chains: Secuencias de llamadas a LLMs
    - Memory: Persistencia de estado entre llamadas
    - Agents: LLMs que toman decisiones sobre acciones

    Casos de uso:
    - Chatbots con contexto
    - RAG (Retrieval Augmented Generation)
    - Agentes autonomos
    - Analisis de documentos
    """

    with open(f"{docs_dir}/python_guide.txt", "w", encoding="utf-8") as f:
        f.write(doc1)
    with open(f"{docs_dir}/docker_intro.txt", "w", encoding="utf-8") as f:
        f.write(doc2)
    with open(f"{docs_dir}/langchain_info.txt", "w", encoding="utf-8") as f:
        f.write(doc3)

    print(f"Documentos de ejemplo creados en: {docs_dir}")
    return docs_dir


def main():
    """Demo del sistema RAG."""
    print("\n" + "#"*60)
    print("# Sistema RAG con LangChain + Ollama")
    print("#"*60)

    # Crear documentos de ejemplo
    docs_dir = crear_documentos_ejemplo()

    # Inicializar RAG
    rag = RAGSystem()

    # Cargar documentos
    print("\n[1] Cargando documentos...")
    rag.cargar_documentos(docs_dir)

    # Hacer preguntas
    preguntas = [
        "Quien creo Python y en que anio?",
        "Que es un contenedor en Docker?",
        "Cuales son los componentes principales de LangChain?",
        "Cual es la capital de Francia?",  # No esta en los docs
    ]

    print("\n[2] Haciendo preguntas...")
    for pregunta in preguntas:
        print(f"\n{'='*50}")
        print(f"Pregunta: {pregunta}")
        print("-"*50)
        respuesta = rag.preguntar(pregunta)
        print(f"Respuesta: {respuesta}")

    # Busqueda de similitud
    print("\n[3] Busqueda de documentos similares...")
    docs = rag.buscar_similares("inteligencia artificial", k=2)
    print(f"\nDocumentos relacionados con 'inteligencia artificial':")
    for i, doc in enumerate(docs, 1):
        print(f"\n--- Documento {i} ---")
        print(doc.page_content[:200] + "...")


if __name__ == "__main__":
    main()
