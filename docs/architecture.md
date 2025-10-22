# YACHAQ-LEX Architecture

## Mission
Build the authoritative Ecuador-focused legal, tax, customs, and government-process assistant. Every system component is optimized to ingest verified sources, curate them into trustworthy corpora, fine-tune Qwen2.5-7B-Instruct, and serve answers with citations.

## High-Level View
1. **Acquisition** – Python scrapers (VM-hosted) pull data from government portals and academic repositories. Raw payloads and structured metadata land in `s3://yachaq-lex-raw-0017472631`.
2. **Processing** – AWS Step Functions orchestrate SageMaker Processing jobs that clean, dedupe, chunk, and tag content into curated datasets in `s3://yachaq-lex-processed/` and `s3://yachaq-lex-training/`.
3. **Training** – SageMaker Training jobs fine-tune the base model using nanochat-style SFT datasets, backed by the `yachaq/nanochat-train` container.
4. **Evaluation & Registry** – SageMaker Processing jobs score each model build; models and metadata are registered in SageMaker Model Registry.
5. **Serving** – The best checkpoint is deployed to SageMaker Endpoints (fp16 primary, 8-bit optional), integrated with the RAG stack defined in `rag/app/`. Monitoring uses CloudWatch metrics and S3 inference logs.

## Component Details

### Data Acquisition Layer
- **Scrapers**: `rag/ingest/real_*.py` scripts plus upcoming DSpace harvesters. All runs support `--dry-run` and production modes with S3 uploads.
- **Execution Environment**: GCE VM (`yachaq-scrape-1`) with Python virtualenv `venv_yachaq`. Background jobs launched via helper scripts (`run_datosabiertos.sh`).
- **Storage Layout**: `s3://yachaq-lex-raw-0017472631/<source>/year=YYYY/...` for binaries, plus JSONL ledgers under `rag/ingest/*_data.jsonl`.

### Processing Layer (SageMaker)
- **Containers**: `yachaq/nanochat-preprocess` handles PDF/HTML to text, dedupe, keyword filtering, and chunking. Output writes to `s3://yachaq-lex-processed/`.
- **Pipelines**: Step Functions or orchestrated Batch jobs trigger:
  1. `clean_text_job` – Extracts text + metadata, produces canonical JSON.
  2. `filter_and_tag_job` – Applies keyword taxonomy (tax/legal/customs/admin) and drops out-of-domain content.
  3. `sft_packaging_job` – Produces nanochat-compatible SFT train/val/test splits.
  4. `eval_builder_job` – Creates held-out question/answer sets.
- **Metadata**: Each artifact carries source, institution, year, citation markers, checksum, and processing version.

### Training Layer
- **Base Model**: Qwen2.5-7B-Instruct.
- **Workflow**:
  1. Launch baseline training job (sample dataset) for smoke tests.
  2. Run full SFT job on curated corpus with warm-up, cosine decay, bf16 precision.
  3. Hyperparameter tuning (learning rate, weight decay) collects best checkpoint.
- **Outputs**: Models pushed to `s3://yachaq-lex-model-artifacts/<run-id>/` and registered with metrics + data hashes.

### Evaluation & Quantization
- SageMaker Processing job executes evaluation harness: accuracy, citation compliance, domain coverage.
- Post-training quantization options:
  - 8-bit (bitsandbytes) for default GPU serving.
  - 4-bit (AWQ/GPTQ) for cost-sensitive deployments.
  - Full precision artifact kept as source of truth.
- Each quantized model is re-evaluated before registry promotion.

### Serving & RAG Integration
- **Primary Endpoint**: fp16 model on `ml.g5.2xlarge` (autoscaling). System prompt enforces citation format.
- **Secondary Endpoints**: 8-bit or 4-bit variants as needed.
- **RAG Stack**: `docker/compose.rag.yaml` hosts API. Retrieval layer augments model responses when confidence < threshold.
- **Monitoring**: CloudWatch dashboards (latency, error rate), S3 inference logs, weekly manual QA sessions.

### Security & Compliance
- IAM roles enforce least privilege (separate ingestion, processing, training, deployment roles).
- All storage buckets versioned; PII filtering built into preprocessing jobs.
- Legal updates tracked through metadata; outdated laws flagged for refresh scrapes.

## Implementation Plan (Waves & Sprints)

### Wave 0 – Foundations (Week 0–1)
| Sprint | Scope & Key Activities | Deliverables |
| --- | --- | --- |
| Sprint 0.1 | Finalize repo hygiene; set up shared `.env` templates; tag existing scrapers with version metadata. | Updated repo README, `.env.sample`, scraper version matrix, access audit log. |
| Sprint 0.2 | Provision core AWS resources (S3 buckets, IAM roles); baseline Terraform validation; document runbooks. | Applied Terraform plan, IAM policy docs, `docs/operations/runbooks.md`, initial CloudWatch dashboard skeleton. |

Exit Criteria: Engineers can launch scrapers, push artifacts to the correct S3 prefixes, and assume least-privilege roles without manual tweaks.

### Wave 1 – Data Acquisition Hardening (Week 1–3)
| Sprint | Scope & Key Activities | Deliverables |
| --- | --- | --- |
| Sprint 1.1 | Stabilize production scrapers (SRI, Registro Oficial, Asamblea, Datos Abiertos); add structured logging + health alerts. | Updated scrapers with retry/backoff, log schema, `docs/data-ingestion.md` smoke checklist, PagerDuty alert spec. |
| Sprint 1.2 | Extend coverage to SERCOP OCDS and municipal datasets; publish ingestion coverage dashboard prototype. | New `real_sercop_scraper.py`, municipal harvester configs, dashboard notebook, S3 data manifests (raw + ledgers). |

Exit Criteria: All priority sources ingest nightly with monitoring, and coverage metrics are surfaced in a single place.

### Wave 2 – Processing & Curation Pipeline (Week 3–6)
| Sprint | Scope & Key Activities | Deliverables |
| --- | --- | --- |
| Sprint 2.1 | Containerize preprocessing jobs; author Step Functions definitions; wire automated triggers from ingestion completion. | `infra/aws/step_functions/*.json`, `yachaq/nanochat-preprocess` image push, CI pipeline to publish containers, processing job templates. |
| Sprint 2.2 | Implement dedupe, tagging, and chunking stages with domain-specific rules; validate outputs on sample corpora. | Processing config repo (`config/processing/*.yaml`), QA report, canonical schema docs, curated dataset in `s3://yachaq-lex-processed/preview/`. |
| Sprint 2.3 | Publish nanochat SFT packager; automate eval dataset creation; integrate with metadata registry. | `processing/sft_packager.py`, eval builder script, dataset catalog JSON, data version changelog. |

Exit Criteria: A full ingestion → processed pipeline runs via Step Functions with deterministic artifacts and QA sign-off.

### Wave 3 – Model Training & Evaluation (Week 6–9)
| Sprint | Scope & Key Activities | Deliverables |
| --- | --- | --- |
| Sprint 3.1 | Stand up SageMaker training template; run baseline smoke-training on subset; implement automatic metric collection. | `training/baseline_sagemaker.py` updates, training job config JSON, baseline metrics report stored in Model Registry. |
| Sprint 3.2 | Execute full-scale SFT job; add hyperparameter tuning jobs; snapshot artifacts; design rollback strategy. | Full SFT checkpoint in `s3://yachaq-lex-model-artifacts/`, tuning results table, rollback SOP, cost dashboard. |
| Sprint 3.3 | Build evaluation harness (automatic + human-in-the-loop); wire promotion gates in Model Registry. | `tests/test_evaluation_metrics.py` expansion, human eval rubric, promotion automation script, registry event notifications. |

Exit Criteria: Trained models pass quantitative + qualitative gates and are registered with reproducible lineage.

### Wave 4 – Serving & RAG Deployment (Week 9–11)
| Sprint | Scope & Key Activities | Deliverables |
| --- | --- | --- |
| Sprint 4.1 | Deploy fp16 endpoint; integrate with RAG API (`rag/app/`); add real-time monitoring dashboards. | SageMaker endpoint stack (Terraform/CDK), updated RAG Docker compose, CloudWatch dashboards, latency/error alerts. |
| Sprint 4.2 | Roll out 8-bit/4-bit variants; implement traffic shifting, canary releases, and post-deployment QA cadence. | Quantized model artifacts, deployment playbook, canary test suite, weekly QA checklist. |

Exit Criteria: Production API serves responses with redundancy, observability, and rollback levers in place.

### Wave 5 – Continuous Improvement & Governance (Week 11–14)
| Sprint | Scope & Key Activities | Deliverables |
| --- | --- | --- |
| Sprint 5.1 | Automate retraining triggers (data drift, policy updates); extend coverage to new sources; harden security posture. | Drift detection scripts, updated IAM guardrails, source backlog grooming doc, quarterly audit template. |
| Sprint 5.2 | Launch analytics + feedback loop; prioritize roadmap for advanced retrieval (vector DB upgrades, semantic rerankers). | User feedback ingestion service, analytics dashboards, vector store upgrade RFC, next-wave roadmap. |

Exit Criteria: System operates with continuous refresh, measurable KPIs, and a prioritized roadmap for the next cycle.

### Governance & Cadences
- Wave review checkpoint every two weeks with stakeholders to confirm exit criteria.
- Sprint demo at end of each sprint with updated artifacts stored in `/docs/reports/`.
- Risk log updated weekly; high-impact blockers escalate within 24 hours.
- Documentation (architecture, ingestion, operations) must be updated before sprint closure.
