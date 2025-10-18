# YACHAQ-LEX Training Plan

## Current Data Status
- **9,328 metadata records** scraped from Ecuador government
- **Sources**: Datos Abiertos (8,739), Asamblea (305), SRI (125), GAD (88), Academic (28), Others (43)
- **Location**: s3://yachaq-lex-raw-0017472631/

## Training Strategy

### Phase 1: Data Collection (NOW - 48 hours)
1. **Run all scrapers continuously** on AWS EC2
2. **Download actual files** from 9,328 URLs
3. **Target**: 50GB+ raw data (PDFs, CSVs, XLSX)
4. **Priority sources**:
   - Registro Oficial PDFs (legal documents)
   - SRI tax datasets (125 files)
   - Asamblea laws (305 documents)
   - Datos Abiertos files (8,739 resources)

### Phase 2: Data Processing (48-72 hours)
1. **Extract text** from PDFs using PyMuPDF
2. **Parse structured data** from CSV/XLSX
3. **Clean and deduplicate**
4. **Create training dataset**:
   - Format: JSONL with instruction-response pairs
   - Example: {"instruction": "¿Qué es el RUC?", "response": "El RUC es..."}

### Phase 3: Model Training (72-96 hours)
1. **Base model**: Qwen2.5-7B-Instruct
2. **Method**: QLoRA 4-bit
3. **Hardware**: AWS p3.2xlarge (V100 GPU) or GCP A100
4. **Training config**:
   - LoRA rank: 64
   - Learning rate: 2e-4
   - Batch size: 4
   - Gradient accumulation: 4
   - Epochs: 3
   - Max length: 2048 tokens

### Phase 4: Deployment (96+ hours)
1. **Quantize**: AWQ/GPTQ for inference
2. **Serve**: vLLM on AWS/GCP
3. **RAG**: Integrate with vector DB (Pinecone/Weaviate)

## Immediate Actions
1. Start EC2 instance for continuous scraping
2. Download all 9,328 files
3. Upload raw data to S3
4. Begin text extraction
