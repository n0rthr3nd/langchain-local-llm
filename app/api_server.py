import os
import shutil
import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rag_service import RAGService

# Load environment variables
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2")
PORT = int(os.getenv("PORT", 8000))
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", 4096))

# Initialize FastAPI
app = FastAPI(title="LangChain Local LLM API")

# Models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatResponse(BaseModel):
    response: str
    model: str

class AnalysisRequest(BaseModel):
    text: str
    task: str
    model: str = MODEL_NAME

# Configuration
UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"status": "ok", "service": "LangChain Local API"}

# Inicializar RAG Service
rag_service = RAGService(
    ollama_base_url=OLLAMA_BASE_URL,
    model_name=MODEL_NAME
)

# ... (Models) ...

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Conversation messages")
    model: str = Field(default=MODEL_NAME, description="Model name")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=4096, description="Max tokens")
    system_prompt: Optional[str] = Field(default="Eres un asistente útil.", description="System prompt")
    use_knowledge_base: Optional[bool] = Field(default=False, description="Use RAG context")


# ... (Existing endpoints) ...

@app.get("/models")
async def get_models():
    """Obtener lista de modelos disponibles en Ollama."""
    try:
        # Usamos httpx para consultar directamente a Ollama
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                data = response.json()
                # Extraer solo los nombres de los modelos
                models = [model["name"] for model in data.get("models", [])]
                return {"models": models}
            else:
                raise HTTPException(status_code=response.status_code, detail="Error fetching models from Ollama")
    except Exception as e:
         # Fallback si falla la conexión
        print(f"Error fetching models: {e}")
        return {"models": [MODEL_NAME]}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint de chat con soporte RAG opcional."""
    # Validar longitud
    for msg in request.messages:
        if len(msg.content) > MAX_INPUT_LENGTH:
            raise HTTPException(status_code=400, detail="Message too long")

    try:
        if request.use_knowledge_base:
            # RAG Flow
            last_message = request.messages[-1]
            if last_message.role != "user":
                 raise HTTPException(status_code=400, detail="Last message must be from user for RAG")
            
            response_text = rag_service.ask(last_message.content)
            return ChatResponse(response=response_text, model=request.model)
        
        else:
            # Standard Flow
            llm = ChatOllama(
                model=request.model,
                base_url=OLLAMA_BASE_URL,
                temperature=request.temperature,
                num_predict=request.max_tokens,
            )

            # ... (Existing message construction logic) ...
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

            chain = llm | StrOutputParser()
            response = chain.invoke(langchain_messages)

            return ChatResponse(response=response, model=request.model)

    except Exception as e:
        import traceback
        print(f"Error in chat endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Upload and ingest a document into the Knowledge Base."""
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        num_chunks = rag_service.ingest_file(file_path)
        
        return {
            "filename": file.filename,
            "status": "success", 
            "chunks_added": num_chunks,
            "message": f"Successfully ingested {file.filename}"
        }
    except Exception as e:
        import traceback
        print(f"Error ingesting file: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")



@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Endpoint de chat con streaming via texto plano."""
    # Validar longitud de mensajes
    for msg in request.messages:
        if len(msg.content) > MAX_INPUT_LENGTH:
            raise HTTPException(status_code=400, detail="Message too long")

    async def generate():
        try:
        try:
            if request.use_knowledge_base:
                # RAG Flow
                last_message = request.messages[-1]
                if last_message.role != "user":
                    yield "Error: Last message must be from user for RAG."
                    return

                # Streaming de RAG
                for chunk in rag_service.ask_stream(last_message.content):
                    yield chunk
            
            else:
                # Standard Flow
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
