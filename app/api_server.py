"""
API REST con FastAPI para LangChain + Ollama
Expone endpoints para chat y RAG
"""
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

# Configuracion
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2")

app = FastAPI(
    title="LangChain + Ollama API",
    description="API local para interactuar con LLMs sin costes",
    version="1.0.0"
)

# CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Modelos Pydantic
# =============================================================================
class ChatMessage(BaseModel):
    role: str  # "user" o "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    system_prompt: Optional[str] = "Eres un asistente util."
    temperature: Optional[float] = 0.7
    model: Optional[str] = MODEL_NAME


class ChatResponse(BaseModel):
    response: str
    model: str


class AnalysisRequest(BaseModel):
    text: str
    task: str  # "summarize", "sentiment", "extract_keywords"
    model: Optional[str] = MODEL_NAME


# =============================================================================
# Endpoints
# =============================================================================
@app.get("/")
async def root():
    """Health check."""
    return {
        "status": "ok",
        "service": "LangChain + Ollama API",
        "ollama_url": OLLAMA_BASE_URL,
        "default_model": MODEL_NAME
    }


@app.get("/models")
async def list_models():
    """Listar modelos disponibles en Ollama."""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama no disponible: {e}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint de chat simple."""
    try:
        llm = ChatOllama(
            model=request.model,
            base_url=OLLAMA_BASE_URL,
            temperature=request.temperature,
        )

        # Construir historial
        messages = [("system", request.system_prompt)]
        for msg in request.history:
            messages.append((msg.role, msg.content))
        messages.append(("human", request.message))

        prompt = ChatPromptTemplate.from_messages(messages)
        chain = prompt | llm | StrOutputParser()

        response = chain.invoke({})

        return ChatResponse(response=response, model=request.model)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Endpoint de chat con streaming."""
    async def generate():
        try:
            llm = ChatOllama(
                model=request.model,
                base_url=OLLAMA_BASE_URL,
                temperature=request.temperature,
            )

            messages = [("system", request.system_prompt)]
            for msg in request.history:
                messages.append((msg.role, msg.content))
            messages.append(("human", request.message))

            prompt = ChatPromptTemplate.from_messages(messages)
            chain = prompt | llm

            for chunk in chain.stream({}):
                yield chunk.content

        except Exception as e:
            yield f"Error: {e}"

    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/analyze")
async def analyze_text(request: AnalysisRequest):
    """Analizar texto (resumen, sentimiento, keywords)."""
    tasks = {
        "summarize": "Resume el siguiente texto en 2-3 oraciones:\n\n{text}",
        "sentiment": """Analiza el sentimiento del siguiente texto.
Responde con JSON: {{"sentimiento": "positivo|negativo|neutral", "confianza": 0.0-1.0}}

Texto: {text}""",
        "extract_keywords": """Extrae las 5 palabras clave mas importantes del texto.
Responde con JSON: {{"keywords": ["kw1", "kw2", ...]}}

Texto: {text}"""
    }

    if request.task not in tasks:
        raise HTTPException(
            status_code=400,
            detail=f"Tarea no valida. Opciones: {list(tasks.keys())}"
        )

    try:
        llm = ChatOllama(
            model=request.model,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1,
        )

        prompt = ChatPromptTemplate.from_template(tasks[request.task])
        chain = prompt | llm | StrOutputParser()

        result = chain.invoke({"text": request.text})

        return {
            "task": request.task,
            "result": result,
            "model": request.model
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Main
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    print(f"Iniciando servidor API...")
    print(f"Ollama URL: {OLLAMA_BASE_URL}")
    print(f"Modelo por defecto: {MODEL_NAME}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
