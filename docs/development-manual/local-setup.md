# Local Environment Setup

1.  **Clone the repository:**
    ```bash
    git clone <your_repository_url>
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r rag/app/requirements.txt
    ```
3.  **Set up AWS credentials:**
    Create a `.env` file in the project root with your AWS credentials.
4.  **Run the application:**
    ```bash
    docker compose -f docker/compose.rag.yaml up -d
    ```
