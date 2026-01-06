"""
API REST con FastAPI para LangChain + Ollama
Expone endpoints para chat con soporte de streaming SSE
"""
import os
import asyncio
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

# Configuracion
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2")
PORT = int(os.getenv("PORT", "8000"))
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "10000"))

app = FastAPI(
    title="ChatGPT Local - Ollama API",
    description="API local estilo ChatGPT usando Ollama",
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
    role: str = Field(..., description="Role: user, assistant, or system")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Conversation messages")
    model: str = Field(default=MODEL_NAME, description="Model name")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=4096, description="Max tokens")
    system_prompt: Optional[str] = Field(default="Eres un asistente útil.", description="System prompt")


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
    """Endpoint de chat simple sin streaming."""
    # Validar longitud de mensajes
    for msg in request.messages:
        if len(msg.content) > MAX_INPUT_LENGTH:
            raise HTTPException(status_code=400, detail="Message too long")

    try:
        llm = ChatOllama(
            model=request.model,
            base_url=OLLAMA_BASE_URL,
            temperature=request.temperature,
            num_predict=request.max_tokens,
        )

        # Construir mensajes en formato LangChain usando objetos Message directamente
        # para evitar problemas con caracteres especiales en plantillas
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

        langchain_messages = []

        # Agregar system prompt si existe y no está en los mensajes
        has_system = any(msg.role == "system" for msg in request.messages)
        if not has_system and request.system_prompt:
            langchain_messages.append(SystemMessage(content=request.system_prompt))

        # Agregar resto de mensajes
        for msg in request.messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))

        # Invocar directamente sin usar plantillas que puedan malinterpretar caracteres especiales
        chain = llm | StrOutputParser()
        response = chain.invoke(langchain_messages)

        return ChatResponse(response=response, model=request.model)

    except Exception as e:
        import traceback
        print(f"Error in chat endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Endpoint de chat con streaming via texto plano."""
    # Validar longitud de mensajes
    for msg in request.messages:
        if len(msg.content) > MAX_INPUT_LENGTH:
            raise HTTPException(status_code=400, detail="Message too long")

    async def generate():
        try:
            llm = ChatOllama(
                model=request.model,
                base_url=OLLAMA_BASE_URL,
                temperature=request.temperature,
                num_predict=request.max_tokens,
            )

            # Construir mensajes usando objetos Message directamente
            # para evitar problemas con caracteres especiales en plantillas
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

            langchain_messages = []

            has_system = any(msg.role == "system" for msg in request.messages)
            if not has_system and request.system_prompt:
                langchain_messages.append(SystemMessage(content=request.system_prompt))

            for msg in request.messages:
                if msg.role == "user":
                    langchain_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    langchain_messages.append(AIMessage(content=msg.content))
                elif msg.role == "system":
                    langchain_messages.append(SystemMessage(content=msg.content))

            # Stream de chunks directamente sin plantillas
            for chunk in llm.stream(langchain_messages):
                if hasattr(chunk, 'content'):
                    yield chunk.content
                await asyncio.sleep(0)  # Permitir que otros procesos se ejecuten

        except Exception as e:
            import traceback
            print(f"Error in chat stream endpoint: {str(e)}")
            print(traceback.format_exc())
            yield f"\n\nError: {str(e)}"

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
    print("=" * 60)
    print("ChatGPT Local - Ollama API Server")
    print("=" * 60)
    print(f"Ollama URL: {OLLAMA_BASE_URL}")
    print(f"Modelo por defecto: {MODEL_NAME}")
    print(f"Puerto: {PORT}")
    print(f"Max input length: {MAX_INPUT_LENGTH} caracteres")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=PORT)
