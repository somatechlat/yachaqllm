# System Architecture

The current YACHAQ-LEX stack is a lightweight prototype focused on data preparation and service health checks. The production-facing RAG workflow is not implemented yet.

- **Data Ingestion:** `rag/ingest/crawl.py` seeds a small JSONL dataset with sample legal records. Additional scrapers exist under `rag/ingest/` but are not wired into an automated pipeline.
- **Indexing:** `rag/ingest/index.py` converts the seed dataset into a Parquet file and optionally publishes it to a local Qdrant instance. The script can skip Qdrant entirely if the service is unavailable.
- **API:** `rag/app/main.py` exposes a single `GET /health` endpoint via FastAPI to report service status. There is no `POST /ask` endpoint or LLM-backed generation flow in this branch.
- **Rule Utilities:** `rag/app/rule_engine.py` contains standalone helpers for deterministic tax and calendar calculations. These utilities are not currently invoked by the API layer.

As new functionality lands (retrieval, generation, orchestration), this document should be updated to reflect the deployed behavior.
