import os
import shutil
import asyncio
import json
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from rag_service import RAGService
import nltk

# Import MongoDB MCP
try:
    from mcp_server.mongodb_mcp import create_mongodb_mcp_server
    MONGODB_MCP_AVAILABLE = True
except ImportError:
    MONGODB_MCP_AVAILABLE = False
    print("WARNING: MongoDB MCP not available")

# Ensure NLTK data is available
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

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

# Inicializar MongoDB MCP
mongodb_server = None
mongodb_tools = []
mongodb_context = None

if MONGODB_MCP_AVAILABLE:
    try:
        mongodb_server = create_mongodb_mcp_server()

        # Crear LangChain tools a partir de las herramientas MCP
        @tool
        def mongodb_find(collection: str, filter_json: Any = "{}", limit: Any = 10) -> str:
            """Busca documentos en una colección de MongoDB.

            Args:
                collection: Nombre de la colección
                filter_json: Filtro en formato JSON (ej: {"status": "active"})
                limit: Número máximo de documentos a retornar

            Returns:
                JSON string con los resultados
            """
            # Convertir filter_json a string si es un dict
            if isinstance(filter_json, dict):
                filter_json = json.dumps(filter_json)
            elif filter_json is None or filter_json == "":
                filter_json = "{}"

            # Convertir limit a int si es necesario
            if limit is None:
                limit = 10
            elif isinstance(limit, str):
                limit = int(limit)

            result = mongodb_server.execute_tool("mongodb_find", {
                "collection": collection,
                "filter_json": filter_json,
                "limit": limit
            })
            return result

        @tool
        def mongodb_count(collection: str, filter_json: Any = "{}") -> str:
            """Cuenta documentos en una colección que cumplan un filtro.

            Args:
                collection: Nombre de la colección
                filter_json: Filtro en formato JSON

            Returns:
                JSON string con el conteo
            """
            # Convertir filter_json a string si es un dict
            if isinstance(filter_json, dict):
                filter_json = json.dumps(filter_json)
            elif filter_json is None or filter_json == "":
                filter_json = "{}"

            result = mongodb_server.execute_tool("mongodb_count", {
                "collection": collection,
                "filter_json": filter_json
            })
            return result

        @tool
        def mongodb_aggregate(collection: str, pipeline_json: str) -> str:
            """Ejecuta un pipeline de agregación en MongoDB.

            Args:
                collection: Nombre de la colección
                pipeline_json: Pipeline en formato JSON array

            Returns:
                JSON string con los resultados
            """
            result = mongodb_server.execute_tool("mongodb_aggregate", {
                "collection": collection,
                "pipeline_json": pipeline_json
            })
            return result

        @tool
        def mongodb_list_collections() -> str:
            """Lista todas las colecciones disponibles en la base de datos.

            Returns:
                JSON string con la lista de colecciones
            """
            result = mongodb_server.execute_tool("mongodb_list_collections", {})
            return result

        mongodb_tools = [mongodb_find, mongodb_count, mongodb_aggregate, mongodb_list_collections]

        # Obtener contexto de la base de datos
        try:
            result = mongodb_server.execute_tool("mongodb_list_collections", {})
            result_data = json.loads(result)
            if result_data.get("success"):
                mongodb_context = {
                    "database": result_data.get("database"),
                    "collections": result_data.get("collections", [])
                }
        except Exception as e:
            print(f"Error getting MongoDB context: {e}")

        print(f"✓ MongoDB MCP initialized with {len(mongodb_tools)} tools")
        if mongodb_context:
            print(f"✓ Database: {mongodb_context['database']}, Collections: {len(mongodb_context['collections'])}")
    except Exception as e:
        print(f"Error initializing MongoDB MCP: {e}")
        MONGODB_MCP_AVAILABLE = False

# ... (Models) ...

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Conversation messages")
    model: str = Field(default=MODEL_NAME, description="Model name")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=4096, description="Max tokens")
    system_prompt: Optional[str] = Field(default="Eres un asistente útil.", description="System prompt")
    use_knowledge_base: Optional[bool] = Field(default=False, description="Use RAG context")
    use_mongodb_tools: Optional[bool] = Field(default=False, description="Enable MongoDB database tools")


# ... (Existing endpoints) ...

@app.get("/models/raw")
async def get_models_raw():
    """Endpoint de debug: retorna la respuesta raw de Ollama sin procesar."""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Ollama returned status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

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
                print(f"DEBUG - Raw Ollama response: {data}")

                # Extraer información completa de los modelos con validación robusta
                models = []
                for model in data.get("models", []):
                    # Intentar obtener el nombre desde múltiples campos posibles
                    model_name = model.get("name") or model.get("model") or ""

                    print(f"DEBUG - Processing model: {model}")
                    print(f"DEBUG - Extracted name: '{model_name}'")

                    # Solo agregar modelos con nombre válido
                    if model_name and model_name.strip():
                        models.append({
                            "name": model_name.strip(),
                            "size": model.get("size"),
                            "modified_at": model.get("modified_at")
                        })
                    else:
                        print(f"WARNING - Skipping model with empty name: {model}")

                print(f"DEBUG - Processed models: {models}")
                print(f"DEBUG - Number of models: {len(models)}")

                # Si no hay modelos válidos, usar fallback
                if not models:
                    print("WARNING - No valid models found, using fallback")
                    models = [{"name": MODEL_NAME}]

                return {"models": models}
            else:
                print(f"ERROR - Ollama returned status code: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Error fetching models from Ollama")
    except Exception as e:
         # Fallback si falla la conexión
        print(f"ERROR - Exception fetching models: {e}")
        import traceback
        print(traceback.format_exc())
        return {"models": [{"name": MODEL_NAME}]}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint de chat con soporte RAG opcional y MongoDB tools."""
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

            response_text = await rag_service.ask(
                question=last_message.content,
                model_name=request.model,
                temperature=request.temperature
            )
            return ChatResponse(response=response_text, model=request.model)

        else:
            # Standard Flow (con o sin MongoDB tools)
            llm = ChatOllama(
                model=request.model,
                base_url=OLLAMA_BASE_URL,
                temperature=request.temperature,
                num_predict=request.max_tokens,
            )

            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

            langchain_messages = []

            # Construir system prompt con contexto de MongoDB si está habilitado
            system_prompt = request.system_prompt
            if request.use_mongodb_tools and MONGODB_MCP_AVAILABLE and mongodb_context:
                collections_list = ", ".join(mongodb_context["collections"])
                mongodb_system_prompt = f"""Tienes acceso a una base de datos MongoDB llamada '{mongodb_context["database"]}' con las siguientes colecciones: {collections_list}.

Puedes usar las siguientes herramientas para consultar los datos:
- mongodb_list_collections: Lista todas las colecciones disponibles
- mongodb_find: Busca documentos en una colección
- mongodb_count: Cuenta documentos que cumplan un filtro
- mongodb_aggregate: Ejecuta pipelines de agregación complejos

Cuando el usuario haga preguntas sobre los datos:
1. Usa mongodb_list_collections si necesitas ver qué colecciones hay disponibles
2. Usa mongodb_find para obtener documentos de una colección
3. Usa mongodb_count para contar documentos
4. Interpreta los resultados y responde en lenguaje natural

Ejemplos de uso:
- Para listar usuarios: mongodb_find(collection="users", filter_json="{{}}", limit=10)
- Para contar usuarios activos: mongodb_count(collection="users", filter_json='{{"status": "active"}}')
- Para buscar por nombre: mongodb_find(collection="users", filter_json='{{"name": "Juan"}}', limit=5)

{system_prompt}"""
                system_prompt = mongodb_system_prompt

            # Agregar system prompt si existe y no está en los mensajes
            has_system = any(msg.role == "system" for msg in request.messages)
            if not has_system and system_prompt:
                langchain_messages.append(SystemMessage(content=system_prompt))

            # Agregar resto de mensajes
            for msg in request.messages:
                if msg.role == "user":
                    langchain_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    langchain_messages.append(AIMessage(content=msg.content))
                elif msg.role == "system":
                    langchain_messages.append(SystemMessage(content=msg.content))

            # Si MongoDB tools están habilitados, vincular las herramientas al LLM
            if request.use_mongodb_tools and MONGODB_MCP_AVAILABLE and mongodb_tools:
                llm_with_tools = llm.bind_tools(mongodb_tools)

                # Invocar el LLM con herramientas
                result = await llm_with_tools.ainvoke(langchain_messages)

                # Procesar tool calls si existen
                from langchain_core.messages import AIMessage, ToolMessage
                max_iterations = 5
                iteration = 0

                while hasattr(result, 'tool_calls') and result.tool_calls and iteration < max_iterations:
                    iteration += 1
                    langchain_messages.append(result)

                    # Ejecutar cada tool call
                    for tool_call in result.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]

                        print(f"Executing tool: {tool_name} with args: {tool_args}")

                        # Encontrar y ejecutar la herramienta
                        tool_result = None
                        for tool_func in mongodb_tools:
                            if tool_func.name == tool_name:
                                tool_result = tool_func.invoke(tool_args)
                                break

                        if tool_result:
                            langchain_messages.append(
                                ToolMessage(
                                    content=str(tool_result),
                                    tool_call_id=tool_call["id"]
                                )
                            )

                    # Invocar LLM nuevamente con los resultados de las herramientas
                    result = await llm_with_tools.ainvoke(langchain_messages)

                response = result.content if hasattr(result, 'content') else str(result)
            else:
                # Sin herramientas
                chain = llm | StrOutputParser()
                response = await chain.ainvoke(langchain_messages)

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
            if request.use_knowledge_base:
                # RAG Flow
                last_message = request.messages[-1]
                if last_message.role != "user":
                    yield "Error: Last message must be from user for RAG."
                    return

                # Streaming de RAG
                async for chunk in rag_service.ask_stream(
                    question=last_message.content,
                    model_name=request.model,
                    temperature=request.temperature
                ):
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
                from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

                langchain_messages = []

                # Construir system prompt con contexto de MongoDB si está habilitado
                system_prompt = request.system_prompt
                if request.use_mongodb_tools and MONGODB_MCP_AVAILABLE and mongodb_context:
                    collections_list = ", ".join(mongodb_context["collections"])
                    mongodb_system_prompt = f"""Tienes acceso a una base de datos MongoDB llamada '{mongodb_context["database"]}' con las siguientes colecciones: {collections_list}.

Puedes usar las siguientes herramientas para consultar los datos:
- mongodb_list_collections: Lista todas las colecciones disponibles
- mongodb_find: Busca documentos en una colección
- mongodb_count: Cuenta documentos que cumplan un filtro
- mongodb_aggregate: Ejecuta pipelines de agregación complejos

Cuando el usuario haga preguntas sobre los datos:
1. Usa mongodb_list_collections si necesitas ver qué colecciones hay disponibles
2. Usa mongodb_find para obtener documentos de una colección
3. Usa mongodb_count para contar documentos
4. Interpreta los resultados y responde en lenguaje natural

Ejemplos de uso:
- Para listar usuarios: mongodb_find(collection="users", filter_json="{{}}", limit=10)
- Para contar usuarios activos: mongodb_count(collection="users", filter_json='{{"status": "active"}}')
- Para buscar por nombre: mongodb_find(collection="users", filter_json='{{"name": "Juan"}}', limit=5)

{system_prompt}"""
                    system_prompt = mongodb_system_prompt

                has_system = any(msg.role == "system" for msg in request.messages)
                if not has_system and system_prompt:
                    langchain_messages.append(SystemMessage(content=system_prompt))

                for msg in request.messages:
                    if msg.role == "user":
                        langchain_messages.append(HumanMessage(content=msg.content))
                    elif msg.role == "assistant":
                        langchain_messages.append(AIMessage(content=msg.content))
                    elif msg.role == "system":
                        langchain_messages.append(SystemMessage(content=msg.content))

                # Si MongoDB tools están habilitados
                if request.use_mongodb_tools and MONGODB_MCP_AVAILABLE and mongodb_tools:
                    llm_with_tools = llm.bind_tools(mongodb_tools)
                    
                    # Para tools, necesitamos hacer una primera llamada NO streaming para ver si el modelo quiere usar tools
                    # Esto es una limitación actual de LangChain/Ollama streaming con tools
                    result = await llm_with_tools.ainvoke(langchain_messages)
                    
                    # Procesar tool calls si existen
                    from langchain_core.messages import AIMessage, ToolMessage
                    max_iterations = 5
                    iteration = 0
                    
                    while hasattr(result, 'tool_calls') and result.tool_calls and iteration < max_iterations:
                        iteration += 1
                        
                        # Agregar la respuesta del asistente (la llamada a la herramienta)
                        langchain_messages.append(result)
                        
                        # Ejecutar cada tool call
                        for tool_call in result.tool_calls:
                            tool_name = tool_call["name"]
                            tool_args = tool_call["args"]
                            
                            # Notificar al usuario que estamos usando una herramienta (opcional)
                            yield f"[Utilizando herramienta: {tool_name}]...\n"
                            
                            # Encontrar y ejecutar la herramienta
                            tool_result = None
                            for tool_func in mongodb_tools:
                                if tool_func.name == tool_name:
                                    tool_result = tool_func.invoke(tool_args)
                                    break
                            
                            if tool_result:
                                langchain_messages.append(
                                    ToolMessage(
                                        content=str(tool_result),
                                        tool_call_id=tool_call["id"]
                                    )
                                )
                        
                        # Invocar LLM nuevamente
                        # Si es la última iteración o ya no hay tools, podríamos hacer stream aquí
                        # Por simplicidad, seguimos con invoke hasta que no haya tools, y la respuesta final se streamea
                        if iteration < max_iterations:
                             result = await llm_with_tools.ainvoke(langchain_messages)
                             if not (hasattr(result, 'tool_calls') and result.tool_calls):
                                 # Si ya no hay tools, streameamos la respuesta final
                                 async for chunk in llm.astream(langchain_messages):
                                     if hasattr(chunk, 'content'):
                                         yield chunk.content
                                 return # Terminamos
                    
                    # Si salimos del loop (max iteraciones) y tenemos un resultado final
                    if hasattr(result, 'content'):
                         yield result.content

                else:
                    # Stream normal sin tools
                    async for chunk in llm.astream(langchain_messages):
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

        result = await chain.ainvoke({"text": request.text})

        return {
            "task": request.task,
            "result": result,
            "model": request.model
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/rag")
async def debug_rag(query: str):
    """Endpoint de debug para verificar retrieval."""
    try:
        docs = rag_service.get_related_docs(query)
        return {
            "query": query,
            "count": len(docs),
            "documents": [{"content": d.page_content, "metadata": d.metadata} for d in docs]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/mongodb/status")
async def mongodb_status():
    """Obtener estado de la conexión MongoDB."""
    if not MONGODB_MCP_AVAILABLE:
        return {
            "available": False,
            "error": "MongoDB MCP not available"
        }

    try:
        return {
            "available": True,
            "connected": mongodb_server is not None,
            "database": mongodb_context.get("database") if mongodb_context else None,
            "collections": mongodb_context.get("collections") if mongodb_context else [],
            "tools_count": len(mongodb_tools)
        }
    except Exception as e:
        return {
            "available": True,
            "connected": False,
            "error": str(e)
        }

@app.get("/mongodb/collections")
async def mongodb_collections_info():
    """Obtener información detallada de las colecciones."""
    if not MONGODB_MCP_AVAILABLE or not mongodb_server:
        raise HTTPException(status_code=503, detail="MongoDB MCP not available")

    try:
        result = mongodb_server.execute_tool("mongodb_list_collections", {})
        result_data = json.loads(result)

        if not result_data.get("success"):
            raise HTTPException(status_code=500, detail=result_data.get("error"))

        # Obtener muestra de cada colección
        collections_info = []
        for coll_name in result_data.get("collections", []):
            # Contar documentos
            count_result = mongodb_server.execute_tool("mongodb_count", {
                "collection": coll_name,
                "filter_json": "{}"
            })
            count_data = json.loads(count_result)
            doc_count = count_data.get("count", 0) if count_data.get("success") else 0

            # Obtener documento de ejemplo
            sample_result = mongodb_server.execute_tool("mongodb_find", {
                "collection": coll_name,
                "filter_json": "{}",
                "limit": 1
            })
            sample_data = json.loads(sample_result)

            fields = []
            if sample_data.get("success") and sample_data.get("documents"):
                doc = sample_data["documents"][0]
                fields = list(doc.keys())

            collections_info.append({
                "name": coll_name,
                "document_count": doc_count,
                "fields": fields
            })

        return {
            "database": result_data.get("database"),
            "collections": collections_info
        }
    except Exception as e:
        import traceback
        print(traceback.format_exc())
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
