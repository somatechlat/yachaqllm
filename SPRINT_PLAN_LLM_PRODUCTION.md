# YACHAQ-LEX LLM PRODUCTION SPRINT PLAN
**Date:** October 18, 2025  
**Project:** Sovereign Ecuador LLM for Legal, Tax, Customs & Education  
**Model:** Qwen2.5-7B-Instruct  
**Data:** 1,513+ datasets (datosabiertos.gob.ec)  
**Target:** Production-ready by Month 2, 95% citation accuracy  

---

## SPRINT STRUCTURE (10 Phases)

### ✅ **Phase 0: Architecture & Planning** (COMPLETE)
- [x] Verified 25+ government portals (all working Oct 18, 2025)
- [x] Identified 1,513+ open datasets across 98 institutions
- [x] Confirmed 10 core data sources with Scrapy spiders
- [x] Designed Neuro-Symbolic-RAG pipeline (NeSy-RAVe)
- [x] Governo Abierto framework legitimacy established

**Status:** Ready for execution

---

## PHASE 1: DATA COLLECTION (Week 1-2)
**Goal:** Catalog 1,513+ datasets, extract URLs, verify freshness

### Tasks:
1. **API Enumeration** (High Priority)
   - Endpoint: `https://www.datosabiertos.gob.ec/api/3/action/package_search`
   - Pagination: rows=1000, start from 0 → 1513
   - Extract: dataset_id, title, description, tags, organization, resources[], update_frequency
   - Storage: JSONL format (1 per line)
   - Estimated time: 30 min API pulls (respects rate limits)

2. **Resource Discovery** (High Priority)
   - For each dataset: Extract all resources (CSV, XLS, JSON, PDF)
   - Build download URLs for each format
   - Filter by update_frequency (prioritize Monthly/Weekly/Real-time)
   - Test sample downloads (5 per organization)
   - Estimated time: 2 hours distributed crawling

3. **Metadata Aggregation** (Medium Priority)
   - License verification (all should be CC-BY or public domain)
   - Organization mapping (SRI → tax, SENAE → customs, etc.)
   - Size estimation (total GB to download)
   - Freshness check (last_modified vs today)
   - Estimated time: 1 hour

4. **Content Sampling** (Medium Priority)
   - Download 1-3 files per organization
   - Parse CSV headers / XLS sheets / JSON structure
   - Store schema catalog in JSONL
   - Quality check (null handling, encoding)
   - Estimated time: 3 hours

### Deliverables:
```
rag/data/datasets_catalog.jsonl          # All 1,513 datasets with metadata
rag/data/organizations_mapping.json      # 98 institutions → domain labels
rag/data/sample_files/                   # 50-100 sample files tested
rag/ingest/DATA_COLLECTION_REPORT.md     # Summary + quality metrics
```

---

## PHASE 2: DATA PROCESSING & NORMALIZATION (Week 2-3)
**Goal:** Convert 1,513+ datasets to standardized JSONL training corpus

### Implementation:

**2.1 Create Scrapy Pipelines** (`rag/ingest/pipelines.py`)
```python
class ValidationPipeline:
    # Enforce metadata schema
    # Required fields: source, url, domain, content, date, authority
    # Check: no null values, proper encoding, valid dates
    
class DeduplicationPipeline:
    # SHA-256 hash on (content + source + date)
    # Keep: first occurrence (or highest quality by size/completeness)
    # Track: duplicate count by organization

class NormalizationPipeline:
    # Date: DD-MM-YYYY → YYYY-MM-DD
    # RO#: "R.O. No. 142, Sexto Suplemento, de 13-10-2025" → structured
    # Articles: Extract article numbers from legal text
    # Currency: Preserve USD amounts, normalize naming

class JSONLWriterPipeline:
    # Output: train.jsonl (verified records)
    # Output: holdout.jsonl (10% for validation)
    # Output: metadata.jsonl (source attribution)
    # Compress: gzip for storage efficiency
```

**2.2 Data Transformation Strategy**
- Input formats: CSV, XLS, JSON, PDF (via pdfminer.six)
- Output format: Instruction-Response JSONL pairs
- Domain-specific templates:
  ```json
  {
    "instruction": "¿Cuál es la tarifa arancelaria para...",
    "response": "La tarifa arancelaria según SENAE...",
    "source": "SENAE",
    "ro_number": "R.O. 142",
    "ro_date": "2025-10-13",
    "domain": "customs",
    "verified": true
  }
  ```

**2.3 Quality Gates**
- Schema validation: 100% coverage
- Deduplication: < 5% false positives
- Encoding: All UTF-8 valid
- Size: Final corpus 50-100GB (compressed 5-10GB)

### Deliverables:
```
rag/ingest/pipelines.py                  # 4 pipeline classes
rag/data/training/train.jsonl.gz         # Training corpus (90% of verified data)
rag/data/training/validate.jsonl.gz      # Validation set (10%)
rag/data/metadata/sources.jsonl          # Source tracking + citations
rag/DATA_PROCESSING_REPORT.md            # Quality metrics
```

**Metrics to track:**
- Input records: 1,513 datasets
- Output records: X instruction-response pairs
- Deduplication rate: X%
- Average tokens per sample: Y
- Storage efficiency: Z GB → W GB compressed

---

## PHASE 3: QLoRA TRAINING (Week 3-4)
**Goal:** Train Qwen2.5-7B-Instruct on Ecuador verified data

### Architecture:

**3.1 Training Script** (`rag/train/qlora_train.py`)
```python
# Config
model_name = "Qwen/Qwen2.5-7B-Instruct"
dataset_file = "rag/data/training/train.jsonl.gz"
output_dir = "rag/models/yachaq-lex-qwen"

# QLoRA Config
qlora_config = {
    "load_in_4bit": True,
    "bnb_4bit_compute_dtype": torch.bfloat16,
    "bnb_4bit_quant_type": "nf4",
    "bnb_4bit_use_double_quant": True,
}

# LoRA Config
lora_config = LoraConfig(
    r=32,
    lora_alpha=64,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

# Training Config
training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    max_seq_length=4096,
    save_strategy="steps",
    save_steps=500,
    warmup_steps=100,
    bf16=True,
    logging_steps=50,
    report_to="wandb",
)

# Time-boxed execution (45-60 min bursts on free GPU)
trainer = SFTTrainer(...)
trainer.train()
```

**3.2 Checkpoint & Resume Logic**
- Save every 500 steps
- Resume from latest checkpoint if interrupted
- Log to Weights & Biases (free tier)
- Hardware: Google Colab (free GPU 40GB VRAM) or AWS SageMaker Training

**3.3 Post-Training**
- Merge LoRA weights into base model
- Export as: FP16, AWQ 4-bit, GPTQ 4-bit, GGUF Q4_K_M
- Version tagging: `yachaq-lex-qwen-v0.1`
- Size: 7B base → 3.5GB FP16 → 2GB INT4

### Deliverables:
```
rag/train/qlora_train.py                 # Training script
rag/models/yachaq-lex-qwen/              # Trained weights
rag/models/yachaq-lex-qwen-awq-4bit/     # Quantized (GPU)
rag/models/yachaq-lex-qwen-gguf-q4/      # Quantized (CPU)
rag/TRAINING_LOG.md                      # Metrics + loss curves
```

**Metrics:**
- Training loss: < 1.5
- Validation perplexity: < 20
- Throughput: X tokens/sec
- Duration: Y hours on free tier

---

## PHASE 4: RAG SYSTEM (Week 4-5)
**Goal:** Implement hybrid retrieval (vector + BM25) with Qdrant

### Architecture:

**4.1 Embedding Model** (`rag/retrieval/embedder.py`)
```python
# Use: e5-small-v2 (384-dim, multilingual, 33M params)
# Quantization: INT8 (99% efficiency, 0.1% accuracy loss)
# Batch processing: 128 samples at a time
# GPU inference: 50ms/batch (free tier compatible)

embedder = SentenceTransformer('intfloat/e5-small-v2')
embedder.to('cuda')  # or 'cpu' fallback

# Chunking strategy
chunk_size = 512      # tokens
overlap = 50          # tokens
```

**4.2 Qdrant Setup** (`rag/retrieval/vector_store.py`)
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(":memory:")  # or Docker container

# Create collection for legal documents
client.create_collection(
    collection_name="legal_documents",
    vectors_config=VectorParams(
        size=384,  # e5-small embedding dim
        distance=Distance.COSINE,
    ),
)

# Index all chunks with metadata
# metadata: source, ro_number, ro_date, article, authority, domain
```

**4.3 BM25 Full-Text** (`rag/retrieval/bm25_search.py`)
```python
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in

# Whoosh index on disk
schema = Schema(
    content=TEXT(stored=True),
    source=TEXT(stored=True),
    ro_number=TEXT(stored=True),
    date=TEXT(stored=True),
)

# Index all documents
# Search: keyword queries → top-k documents
```

**4.4 Hybrid Retrieval** (`rag/retrieval/hybrid_retriever.py`)
```python
def hybrid_retrieve(query: str, k: int = 5):
    # 1. Vector search (Qdrant)
    query_emb = embedder.encode(query)
    vector_results = client.search(
        collection_name="legal_documents",
        query_vector=query_emb,
        limit=k,
    )
    
    # 2. BM25 search (Whoosh)
    bm25_results = bm25_searcher.search(query, k)
    
    # 3. Merge & re-rank
    combined = merge_and_rerank(vector_results, bm25_results)
    
    # 4. Return top-k with scores
    return combined[:k]
```

**4.5 Benchmark**
- Query set: 100 legal/tax/customs/education questions
- Metrics:
  - MRR@5: Mean Reciprocal Rank (>0.7 = good)
  - NDCG@10: Normalized DCG (>0.8 = excellent)
  - Recall@10: (>0.9 = target)
  - Latency p95: < 100ms

### Deliverables:
```
rag/retrieval/embedder.py                # Embedding model wrapper
rag/retrieval/vector_store.py            # Qdrant integration
rag/retrieval/bm25_search.py             # Whoosh BM25 indexing
rag/retrieval/hybrid_retriever.py        # Combined search logic
rag/data/rag_benchmark.json              # Test queries + ground truth
rag/RAG_EVALUATION_REPORT.md             # Performance metrics
```

---

## PHASE 5: NEURO-SYMBOLIC VERIFICATION (Week 5-6)
**Goal:** Implement verifier reward system for citation accuracy + legal consistency

### Architecture:

**5.1 Citation Verifier** (`rag/verification/citation_verifier.py`)
```python
class CitationVerifier:
    def verify_citation(self, claim: str, source_text: str) -> bool:
        """
        Extract cited span from source_text that supports claim.
        Match accuracy ≥ 95% using fuzzy string matching.
        Return: (is_valid, confidence_score, span_location)
        """
        pass
    
    def exact_match_score(self, claim: str, source: str) -> float:
        # TF-IDF cosine similarity
        # Threshold: 0.85 = valid citation
        pass
```

**5.2 Math/Numeric Verifier** (`rag/verification/numeric_verifier.py`)
```python
class NumericVerifier:
    def verify_number(self, claim_number: float, source_number: float) -> bool:
        """
        Check if claim number matches source number or computed value.
        Support: +/- 5% tolerance, compound calculations.
        Return: (is_valid, error_rate)
        """
        pass
    
    # Examples:
    # Claim: "Tarifa arancelaria: 5.5%"
    # Source: "ARANCEL_2025 = 5.5%"
    # Result: VALID
    
    # Claim: "IVA total: $1,500"
    # Source: "Base: $1,000, Tasa: 15% = $150 + $1,000 = $1,150"
    # Result: INVALID (mismatch in calculation)
```

**5.3 Legal Consistency Checker** (`rag/verification/legal_checker.py`)
```python
class LegalConsistencyChecker:
    def check_ro_validity(self, ro_number: str, ro_date: str) -> bool:
        """
        Validate Registro Oficial number + date combination.
        Example: "R.O. No. 142, Sexto Suplemento, de 13-10-2025"
        Query: Is this RO# published on this date?
        Return: (is_valid, publication_date)
        """
        pass
    
    def check_article_validity(self, law_title: str, article_num: int) -> bool:
        """
        Verify article exists in law and matches cited section.
        """
        pass
```

**5.4 GRPO Preference Tuning** (`rag/train/grpo_train.py`)
```python
# Post-SFT refinement using verifier rewards
# Process:
# 1. Generate 2-3 responses per query (diverse sampling)
# 2. Score each response with verifier (citation + math + consistency)
# 3. Use GRPO to bias LLM toward high-scoring responses
# 4. Run for 1-2 epochs on validation set

grpo_config = {
    "model_name": "yachaq-lex-qwen-v0.1",
    "reward_fn": combined_verifier_score,
    "num_epochs": 1,
    "learning_rate": 1e-5,
}
```

### Deliverables:
```
rag/verification/citation_verifier.py    # Citation accuracy checker
rag/verification/numeric_verifier.py     # Math/number validator
rag/verification/legal_checker.py        # RO#/article validator
rag/train/grpo_train.py                  # GRPO preference tuning
rag/VERIFICATION_REPORT.md               # Verification accuracy metrics
```

**Metrics:**
- Citation accuracy: ≥ 95%
- Math consistency: ≥ 98%
- Legal validity: 100% (RO numbers exist)
- Average reward: > 0.8 (post-GRPO)

---

## PHASE 6: EVALUATION FRAMEWORK (Week 6-7)
**Goal:** Automated daily benchmarking

### Metrics Dashboard:

**6.1 Citation Accuracy** (Target: ≥95%)
- Test set: 50 queries across all 4 domains
- Metric: % of claims with valid source support
- Test: Citation span matches source text (TF-IDF ≥ 0.85)

**6.2 Concordance** (Target: ≥90%)
- Metric: LLM response matches expected answer exactly
- Test set: 25 queries per domain
- Scoring: Exact match OR semantic similarity (BERT ≥ 0.9)

**6.3 Hallucination Rate** (Target: <2%)
- Metric: % of claims NOT in any source
- Detection: Citation verifier returns "NOT_FOUND"
- Test: 100 diverse queries

**6.4 Numeric Reproducibility** (Target: 100%)
- Metric: All numbers in response match source data
- Test: 20 tax/customs queries with numbers
- Scoring: Exact match OR tolerance band (±5%)

**6.5 Freshness Lag** (Target: <7 days)
- Metric: Age of most recent data in response
- Monitor: Last modified timestamp in metadata
- Alert: If lag > 7 days

**6.6 Latency** (Target: p95 <1s GPU, <3s CPU)
- Measure: End-to-end query → response time
- Break down: Retrieval (100ms) + LLM inference (800ms) + Verification (50ms)
- Test: 100 concurrent requests

### Implementation:

**6.1 Test Dataset** (`rag/eval/test_queries.jsonl`)
```json
{
  "query": "¿Cuál es la tarifa arancelaria para importación de cacao?",
  "expected_answer": "5%",
  "domain": "customs",
  "sources": ["SENAE", "Arancel 2025"],
  "difficulty": "easy"
}
```

**6.2 Automated Evaluation** (`rag/eval/evaluate.py`)
```python
from rag.verification import CitationVerifier, NumericVerifier

def evaluate_response(query: str, response: str, ground_truth: dict) -> dict:
    metrics = {
        "citation_accuracy": citation_verifier.score(response),
        "concordance": semantic_similarity(response, ground_truth["answer"]),
        "hallucination_rate": check_hallucination(response),
        "numeric_reproducibility": numeric_verifier.score(response),
        "latency": measure_latency(query),
    }
    return metrics

# Daily benchmark
def daily_evaluation():
    test_queries = load_test_queries("rag/eval/test_queries.jsonl")
    results = []
    for query in test_queries:
        response = llm_pipeline(query)
        metrics = evaluate_response(query, response, query)
        results.append(metrics)
    
    # Log to Prometheus
    average_citation_accuracy = mean([r["citation_accuracy"] for r in results])
    prometheus_metrics["citation_accuracy"].set(average_citation_accuracy)
    
    # Alert if below threshold
    if average_citation_accuracy < 0.95:
        send_alert("Citation accuracy below 95%")
```

**6.3 Grafana Dashboard**
- Query: `(citation_accuracy + concordance + (1-hallucination_rate) + numeric_reproducibility) / 4`
- Displays: Real-time metrics + historical trend
- Alerts: Auto-triggered if metric < threshold

### Deliverables:
```
rag/eval/test_queries.jsonl              # 100+ benchmark queries
rag/eval/evaluate.py                     # Evaluation framework
rag/eval/metrics.py                      # Metric definitions
prometheus/yachaq.rules.yml              # Alert rules
grafana/dashboard.json                   # Monitoring dashboard
rag/DAILY_EVAL_REPORT.md                 # Yesterday's metrics
```

---

## PHASE 7: MODEL QUANTIZATION & SERVING (Week 7-8)
**Goal:** Deploy optimized models for GPU + CPU inference

### 7.1 Quantization Pipeline

**AWQ Quantization (GPU - vLLM)**
```bash
# Command:
python -m awq.entry --model Qwen/Qwen2.5-7B-Instruct \
  --w_bit 4 --q_group_size 128 \
  --output_dir ./models/yachaq-awq-4bit

# Result: 2.2GB (vLLM compatible)
# Latency: < 50ms per token
# Accuracy: 99.5% vs FP16
```

**GPTQ Quantization (GPU - Fallback)**
```bash
# Command:
python -m gptq_entry --model yachaq-lex-qwen-v0.1 \
  --bits 4 --group_size 128 --desc_act False

# Result: 2.1GB
# Latency: < 60ms per token
```

**GGUF Quantization (CPU - llama.cpp)**
```bash
# Command:
python -m llama.cpp.convert \
  --model-dir ./models/yachaq-lex-qwen-v0.1 \
  --outfile ./models/yachaq-q4_k_m.gguf \
  --outtype q4_k_m

# Result: 2.0GB
# Latency (CPU): < 200ms per token
# Memory: 4GB RAM (MacBook compatible)
```

### 7.2 Serving Stack

**vLLM Server** (GPU - Primary)
```python
# rag/serving/vllm_server.py
from vllm import LLM, SamplingParams

llm = LLM(
    model="./models/yachaq-awq-4bit",
    tensor_parallel_size=1,
    max_model_len=4096,
)

# OpenAI API compatible endpoint
# Supports: streaming, batching, long context
```

**llama.cpp Server** (CPU - Fallback)
```bash
# rag/serving/llamacpp_server.py
./bin/server -m ./models/yachaq-q4_k_m.gguf \
  --port 8001 \
  --n-gpu-layers 0 \
  --threads 4
```

### 7.3 Inference Pipeline

**FastAPI Wrapper** (`rag/serving/api.py`)
```python
@app.post("/chat")
async def chat(query: str, use_rag: bool = True):
    # 1. Retrieve (Qdrant + BM25)
    if use_rag:
        docs = retriever.retrieve(query, k=5)
        context = "\n".join([d.content for d in docs])
    else:
        context = ""
    
    # 2. Generate (vLLM or llama.cpp)
    prompt = format_prompt(query, context)
    response = llm.generate(prompt)
    
    # 3. Verify
    verification = verifier.verify(response, docs)
    
    # 4. Return
    return {
        "response": response,
        "sources": docs,
        "verification": verification,
        "latency_ms": latency,
    }

@app.post("/retrieve")
async def retrieve(query: str, k: int = 5):
    docs = retriever.retrieve(query, k)
    return docs

@app.post("/verify")
async def verify(claim: str, sources: list):
    results = verifier.verify_all(claim, sources)
    return results
```

### Deliverables:
```
rag/models/yachaq-awq-4bit/              # AWQ 4-bit (2.2GB)
rag/models/yachaq-gptq-4bit/             # GPTQ 4-bit (2.1GB)
rag/models/yachaq-q4_k_m.gguf            # GGUF (2.0GB)
rag/serving/vllm_server.py               # GPU server
rag/serving/llamacpp_server.py           # CPU server
rag/serving/api.py                       # FastAPI wrapper
```

---

## PHASE 8: FULL SYSTEM INTEGRATION (Week 8-9)
**Goal:** Docker stack + local deployment test

### 8.1 Docker Compose (`docker/compose.rag.yaml`)
```yaml
version: '3.9'

services:
  # Qdrant Vector DB
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage

  # vLLM GPU Server
  vllm:
    build: ./rag/serving
    environment:
      - MODEL_PATH=./models/yachaq-awq-4bit
      - GPU_MEMORY_UTILIZATION=0.9
    ports:
      - "8000:8000"
    volumes:
      - ./rag/models:/models
    gpus:
      - all

  # RAG API Gateway
  api:
    build: ./rag/serving
    environment:
      - VLLM_HOST=vllm:8000
      - QDRANT_HOST=qdrant:6333
      - LOG_LEVEL=info
    ports:
      - "8080:8080"
    depends_on:
      - vllm
      - qdrant

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
```

### 8.2 End-to-End Test
```python
# tests/test_e2e.py

def test_full_pipeline():
    # 1. Query → API
    response = requests.post("http://localhost:8080/chat", 
        json={"query": "¿Cuál es la tarifa arancelaria para cacao?"})
    
    # 2. Verify response structure
    assert "response" in response.json()
    assert "sources" in response.json()
    assert "verification" in response.json()
    
    # 3. Verify citation accuracy
    assert response.json()["verification"]["citation_accuracy"] > 0.95
    
    # 4. Check latency
    assert response.json()["latency_ms"] < 1000
    
    print("✓ End-to-end test passed")
```

### Deliverables:
```
docker/compose.rag.yaml                  # Docker stack
docker/Dockerfile.vllm                   # vLLM image
docker/Dockerfile.api                    # API image
tests/test_e2e.py                        # Integration tests
docker/README.md                         # Deployment guide
```

---

## PHASE 9: TERRAFORM & PRODUCTION DEPLOYMENT (Week 9-10)
**Goal:** AWS/GCP IaC + Go-Live

### 9.1 AWS Terraform (`infra/aws/main.tf`)
```hcl
# EC2 instances
resource "aws_instance" "rag_gpu" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "g4dn.xlarge"  # GPU instance
  
  ebs_block_device {
    device_name = "/dev/xvda"
    volume_size = 100  # 100GB for models + data
  }
  
  tags = { Name = "yachaq-lex-gpu" }
}

resource "aws_instance" "rag_cpu" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"  # Free tier eligible
  
  tags = { Name = "yachaq-lex-cpu" }
}

# RDS for audit logs + metadata
resource "aws_db_instance" "yachaq_metadata" {
  allocated_storage = 20
  engine            = "postgres"
  instance_class    = "db.t3.micro"  # Free tier
}

# S3 for models + backups
resource "aws_s3_bucket" "models" {
  bucket = "yachaq-lex-models"
  
  versioning {
    enabled = true
  }
}
```

### 9.2 GCP Terraform (`infra/gcp/main.tf`)
```hcl
# Compute Engine instance
resource "google_compute_instance" "rag_server" {
  name         = "yachaq-lex-server"
  machine_type = "e2-medium"  # Free tier eligible
  zone         = "us-central1-a"
  
  boot_disk {
    initialize_params {
      image = "ubuntu-2204-lts"
      size  = 50
    }
  }
  
  metadata_startup_script = file("${path.module}/startup.sh")
}

# Cloud SQL for PostgreSQL
resource "google_sql_database_instance" "metadata" {
  name             = "yachaq-metadata"
  database_version = "POSTGRES_15"
  
  settings {
    tier = "db-f1-micro"  # Free tier
  }
}
```

### 9.3 CI/CD Pipeline (`.github/workflows/deploy.yml`)
```yaml
name: Deploy YACHAQ-LEX

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      # 1. Build Docker images
      - name: Build images
        run: docker-compose build
      
      # 2. Run tests
      - name: Test
        run: pytest tests/
      
      # 3. Push to ECR
      - name: Push to ECR
        run: aws ecr push yachaq-lex:latest
      
      # 4. Apply Terraform
      - name: Deploy AWS
        run: |
          cd infra/aws
          terraform apply -auto-approve
      
      # 5. Deploy GCP
      - name: Deploy GCP
        run: |
          cd infra/gcp
          terraform apply -auto-approve
      
      # 6. Run smoke tests
      - name: Smoke test
        run: curl -s http://localhost:8080/health
```

### Deliverables:
```
infra/aws/main.tf                        # AWS infrastructure
infra/gcp/main.tf                        # GCP infrastructure
.github/workflows/deploy.yml             # CI/CD pipeline
infra/startup.sh                         # Instance initialization
DEPLOYMENT_GUIDE.md                      # Step-by-step guide
```

---

## PHASE 10: DOCUMENTATION & GO-LIVE (Week 10+)
**Goal:** Production handoff + knowledge transfer

### 10.1 Documentation

**API Reference** (`docs/API_REFERENCE.md`)
```
POST /chat
  Input: { query: string, use_rag: bool }
  Output: { response, sources, verification, latency_ms }
  Example: {"query": "¿Tarifa de cacao?", "use_rag": true}

POST /retrieve
  Input: { query: string, k: int }
  Output: [{ content, source, ro_number, date }]

POST /verify
  Input: { claim: string, sources: list }
  Output: { citation_accuracy, numeric_valid, legal_valid }
```

**Architecture Diagram** (ASCII)
```
┌─────────────┐
│   User      │
└──────┬──────┘
       │ HTTP Request
       ▼
┌──────────────────────┐
│   FastAPI Server     │
│   (Port 8080)        │
└────────┬─────────────┘
         │
    ┌────┴─────────────────────────┐
    │                              │
    ▼                              ▼
┌─────────────┐           ┌────────────────┐
│ Retriever   │           │   vLLM GPU     │
│ (Hybrid)    │           │   Server       │
└──────┬──────┘           │   (Port 8000)  │
       │                  └────────────────┘
   ┌───┴────────────┐
   │                │
   ▼                ▼
┌─────────┐   ┌──────────┐
│ Qdrant  │   │ Whoosh   │
│ (6333)  │   │ (BM25)   │
└─────────┘   └──────────┘
   │                │
   └────┬───────────┘
        │
        ▼
┌──────────────────────┐
│  Verification Engine │
│  - Citation Check    │
│  - Math Validation   │
│  - Legal Consistency │
└──────────────────────┘
        │
        ▼
┌──────────────────────┐
│  Response + Sources  │
│  + Verification      │
│  + Metadata          │
└──────────────────────┘
```

**Troubleshooting Guide** (`docs/TROUBLESHOOTING.md`)
- Common issues + fixes
- Performance optimization tips
- Model retraining procedures
- Data update procedures

**Quick Start** (`README.md`)
```bash
# 1. Clone & setup
git clone https://github.com/yachaq/yachaq-lex
cd yachaq-lex
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Download models
bash scripts/download_models.sh

# 3. Start services
docker-compose up -d

# 4. Test
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Tarifa arancelaria para cacao?"}'

# Expected response:
# {
#   "response": "La tarifa arancelaria...",
#   "sources": [...],
#   "verification": {"citation_accuracy": 0.98, ...}
# }
```

### 10.2 Knowledge Transfer

**Runbooks** (`docs/runbooks/`)
- `rag-service.md`: Daily operations
- `data-update.md`: Add new datasets
- `model-retrain.md`: Monthly retraining
- `incident-response.md`: Troubleshooting

**Team Handoff Session**
- Demo: Live system queries
- Architecture walkthrough
- Operations procedures
- Support escalation matrix

### Deliverables:
```
docs/API_REFERENCE.md                    # Complete API docs
docs/ARCHITECTURE.md                     # System design
docs/TROUBLESHOOTING.md                  # Common issues
docs/runbooks/                           # Operations guides
README.md                                # Quick start
DEPLOYMENT_CHECKLIST.md                  # Go-live validation
```

---

## SPRINT TIMELINE

| Phase | Duration | Dates | Deliverables | Status |
|-------|----------|-------|--------------|--------|
| 0 | 1 week | Oct 18-25 | Architecture + Planning | ✅ COMPLETE |
| 1 | 2 weeks | Oct 25 - Nov 8 | Data catalog (1,513 datasets) | 🟡 READY |
| 2 | 1 week | Nov 8-15 | Scrapy pipelines + JSONL (50GB) | 🔴 PENDING |
| 3 | 1 week | Nov 15-22 | QLoRA trained model | 🔴 PENDING |
| 4 | 1 week | Nov 22-29 | RAG system (Qdrant + Whoosh) | 🔴 PENDING |
| 5 | 1 week | Nov 29 - Dec 6 | Neuro-symbolic verifier | 🔴 PENDING |
| 6 | 1 week | Dec 6-13 | Evaluation framework | 🔴 PENDING |
| 7 | 1 week | Dec 13-20 | Quantization + serving | 🔴 PENDING |
| 8 | 1 week | Dec 20-27 | Docker + integration tests | 🔴 PENDING |
| 9 | 1 week | Dec 27 - Jan 3 | AWS/GCP deployment | 🔴 PENDING |
| 10 | 1+ weeks | Jan 3+ | Documentation + go-live | 🔴 PENDING |

**Total Duration:** 10-11 weeks to production

---

## SUCCESS CRITERIA

✅ **Data:** 1,513+ datasets fully ingested, deduplicated, validated  
✅ **Model:** Qwen2.5-7B fine-tuned on Ecuador legal/tax/customs/education data  
✅ **RAG:** Hybrid retrieval (Qdrant + BM25) with <100ms latency  
✅ **Quality:** Citation accuracy ≥95%, hallucination rate <2%  
✅ **Verification:** All claims traceable to sources with confidence scores  
✅ **Deployment:** Production-ready on AWS/GCP with auto-scaling  
✅ **Documentation:** Complete API + runbooks + architecture docs  

---

## KEY ASSUMPTIONS

1. **Data Availability:** All 1,513 datasets remain accessible via datosabiertos.gob.ec API (verified Oct 18, 2025)
2. **Model Performance:** Qwen2.5-7B-Instruct achieves >90% accuracy on domain-specific fine-tuning
3. **Hardware:** Free GPU tier (Colab/SageMaker) sufficient for training; production GPU for inference
4. **Legal/Compliance:** All dataset use covered by Gobierno Abierto CC-BY licenses + academic research exemptions
5. **Maintenance:** Monthly data refresh + quarterly model retraining sufficient for production quality

---

## RISK MITIGATION

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Data source unavailability | Low | High | Daily health checks, fallback to cache |
| Model performance degradation | Medium | High | A/B testing, rollback procedure |
| GPU quota exhaustion | Medium | Medium | Multi-region deployment, CPU fallback |
| Citation accuracy drift | Medium | High | Continuous evaluation, alert thresholds |
| Data licensing disputes | Low | High | Legal review of CC-BY terms |

---

## NEXT IMMEDIATE ACTIONS

**Week of Oct 25:**
1. **Monday:** Phase 1 kickoff - API enumeration + dataset catalog
2. **Wednesday:** Sample 100 datasets, validate quality
3. **Friday:** Deliver datasets_catalog.jsonl (all 1,513 items)

**Success metric:** "datosabiertos.gob.ec API fully cataloged with 0 errors"

---

**Prepared by:** GitHub Copilot / YACHAQ-LEX Team  
**Last Updated:** October 18, 2025  
**Next Review:** October 25, 2025 (Phase 1 progress check)
