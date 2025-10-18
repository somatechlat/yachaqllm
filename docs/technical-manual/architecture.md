# System Architecture

YACHAQ-LEX is a Retrieval-Augmented Generation (RAG) system with a hybrid architecture.

- **Data Ingestion:** A Python-based crawler and parser fetches data from official sources, processes it, and stores it in an S3 bucket.
- **Indexing:** The processed data is chunked, vectorized, and stored in a Qdrant vector database.
- **API:** A FastAPI application provides the `/ask` endpoint to receive user queries.
- **Retrieval:** The API retrieves relevant documents from Qdrant based on the user's query.
- **Generation:** The retrieved documents are passed to a Large Language Model (LLM) to generate a final answer.
- **Rule Engine:** A symbolic rule engine is used for verifiable calculations.
