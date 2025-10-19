# Local Environment Setup

1. **Clone the repository:**
    ```bash
    git clone <your_repository_url>
    cd YACHAQ-LEX_full
    ```
2. **Install dependencies for local execution:**
    ```bash
    pip install -r rag/app/requirements.txt
    ```
3. **Start the FastAPI app (health check only):**
    ```bash
    uvicorn rag.app.main:app --host 0.0.0.0 --port 8000
    ```
    Alternatively, you can run the provided Docker Compose stack to launch FastAPI alongside a local Qdrant instance:
    ```bash
    docker compose -f docker/compose.rag.yaml up -d
    ```
4. **Verify the service:**
    ```bash
    curl http://localhost:8000/health
    ```
    A running instance returns `{"status": "ok"}`.
