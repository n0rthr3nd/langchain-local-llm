# Project Context: LangChain Local LLM

## Overview
This project is a complete local Large Language Model (LLM) environment designed to run offline without API costs. It leverages **LangChain** for orchestration, **Ollama** for model serving, and includes a **React** frontend for a ChatGPT-like experience.

It is highly optimized for **Raspberry Pi 5 (8GB)** but supports Windows, Linux, and macOS. It also features a production-ready **Kubernetes (k3s)** deployment strategy.

## Tech Stack
*   **LLM Engine:** [Ollama](https://ollama.ai/) (Llama 3.2, Mistral, Gemma 2, etc.)
*   **Backend:** Python 3.11+, [LangChain](https://python.langchain.com/), [FastAPI](https://fastapi.tiangolo.com/), ChromaDB (RAG)
*   **Frontend:** React, TypeScript, Vite, Tailwind CSS
*   **Infrastructure:** Docker Compose, Kubernetes (k3s/Helm-ready manifests)

## Key Files & Directories
*   `app/`: Python backend source code.
    *   `api_server.py`: The main REST API entry point (FastAPI).
    *   `main.py`: CLI examples for LangChain usage (Chat, Chains, Memory).
    *   `rag_example.py`: RAG (Retrieval-Augmented Generation) implementation.
*   `frontend/`: React application source code.
    *   `src/`: Components, hooks, and utilities.
    *   `vite.config.ts`: Configuration including API proxy setup.
*   `k8s/`: Kubernetes manifests for deployment.
    *   `base/`: Base configurations.
    *   `overlays/`: Environment-specific overlays (e.g., `rpi`).
    *   `scripts/`: Deployment automation scripts.
*   `scripts/`: Utility scripts.
    *   `setup_rpi.sh`: One-click setup for Raspberry Pi.
*   `docker-compose.yml`: Main orchestration for PC/Mac.
*   `docker-compose.rpi.yml`: Optimized orchestration for Raspberry Pi (ARM64).

## Build & Run Instructions

### Docker (Recommended for Dev)
The easiest way to run the full stack is via Docker Compose.

```bash
# Standard (PC/Mac/Linux x86)
docker-compose up -d

# Raspberry Pi (ARM64)
docker-compose -f docker-compose.rpi.yml up -d
```

**Access Points:**
*   **Web UI:** http://localhost:3000 (or port 80/3001 depending on config)
*   **API:** http://localhost:8000
*   **Ollama:** http://localhost:11434

### Manual Development

**Backend:**
Runs on port **8000**.
```bash
cd app
pip install -r ../requirements.txt
# Run API (Hot Reload)
uvicorn api_server:app --reload
# Run Examples
python main.py
```

**Frontend:**
Runs on port **5173** (by default).
```bash
cd frontend
npm install
npm run dev
```

### Kubernetes (K3s)
Deploy to a cluster using the provided scripts:

```bash
./k8s/scripts/build-and-push.sh  # Build images
./k8s/scripts/deploy.sh          # Deploy to cluster
```

## Development Conventions

### API Structure
The backend (`app/api_server.py`) exposes the following endpoints:
*   `GET /models`: List available Ollama models.
*   `POST /chat`: Standard chat completion (JSON response).
*   `POST /chat/stream`: Streaming chat completion (text/plain stream).
*   `POST /analyze`: Text analysis tools (summarize, sentiment, keywords).

### Frontend-Backend Communication
*   **Proxy:** The Vite development server (`vite.config.ts`) is configured to proxy requests from `/api/*` to `http://localhost:8000/*`.
*   **Rewrite:** The `/api` prefix is stripped before reaching the backend (e.g., Frontend `/api/chat` -> Backend `/chat`).

### Model Management
*   Models are managed via Ollama.
*   To pull a new model: `docker exec ollama-server ollama pull <model_name>`
*   Update `MODEL_NAME` in `.env` to change the default model.