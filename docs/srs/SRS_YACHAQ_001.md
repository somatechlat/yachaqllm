# ISO-SRS-29148: Yachaq LLM EC
## Software Requirements Specification

| Document ID | SRS-YACHAQ-001 |
|-------------|----------------|
| **Version** | 1.0.0 |
| **Date** | 2025-12-30 |
| **Status** | Approved |
| **Standard** | ISO/IEC 29148:2018 |

---

## 1. INTRODUCTION

### 1.1 Purpose
The purpose of this document is to specify the requirements for **Yachaq LLM EC**, an AI system specialized in Ecuadorian knowledge domains.

### 1.2 Scope
The system encompasses:
1. **Data Collection Framework**: Autonomous discovery and ingestion of public Ecuadorian data.
2. **Training Infrastructure**: Fine-tuning Llama 3.1 8B using AWS SageMaker.
3. **Inference System**: Deployment via AWS Bedrock.

---

## 2. LEGAL COMPLIANCE

### 2.1 Ecuador Data Protection (LOPDP)
Compliance with *Ley Orgánica de Protección de Datos Personales*.

- **Principle of Legality**: Utilization of public government data (LOTAIP).
- **Prohibition of PII**: Automated filtering of personal identifiers.
- **Traceability**: Immutable logging of all data sources.

---

## 3. SYSTEM ARCHITECTURE

### 3.1 Components

| Component | Technology | Description |
|-----------|------------|-------------|
| **Collector** | Python/Requests | Abstraction layer for data ingestion |
| **Storage** | AWS S3 | Encrypted object storage (SSE-S3) |
| **Compute** | SageMaker | Managed training infrastructure (ml.g5) |
| **Model** | Llama 3.1 8B | Foundation model (QLoRA fine-tuned) |

### 3.2 Data Flow
`Source (Web/API)` -> `Collector` -> `Validation` -> `S3 (Raw)` -> `Preprocessing` -> `S3 (Prepared)` -> `Training`

---

## 4. INFRASTRUCTURE

### 4.1 AWS Configuration
- **Account**: 302776397208
- **Region**: us-east-1
- **VPC**: Default VPC with public subnets (for collectors)

### 4.2 Storage Strategy
- **Bucket**: `yachaq-lex-raw-0017472631`
- **Structure**:
  - `/raw`: Original files (pdf, json, html)
  - `/processed`: Cleaned text
  - `/training`: Tokenized binaries

---

## 5. QUALITY ASSURANCE

### 5.1 Metrics
- **Legal Accuracy**: >95% citation correctness
- **Hallucination Rate**: <1% on factual queries
- **Data Quality**: >0.3 score (heuristic)

### 5.2 Testing
- **Unit Tests**: Coverage >80% for core logic
- **Integration Tests**: End-to-end data pipeline verification
- **Model Eval**: Standard legal benchmarks (LegalBench)

---

**Approved by:**
Project User / Lead Developer
