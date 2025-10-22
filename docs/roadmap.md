# YACHAQ-LEX Roadmap

_Updated: 2025-10-21_

This roadmap mirrors the architecture implementation waves and highlights current status, short-term priorities, and upcoming milestones. Update this document at the close of every sprint review.

## Snapshot Overview

| Wave | Focus | Dates (target) | Status | Notes |
| --- | --- | --- | --- | --- |
| Wave 0 | Foundations | Week 0–1 | ✅ Complete | Repo hygiene, IAM scaffolding, runbooks ready. |
| Wave 1 | Acquisition Hardening | Week 1–3 | ⚠️ In Progress | Datos Abiertos live, SRI off, Compras Públicas pending. |
| Wave 2 | Processing & Curation | Week 3–6 | ⏳ Not Started | Awaiting stable ingestion signals. |
| Wave 3 | Training & Evaluation | Week 6–9 | ⏳ Not Started | Baseline configs drafted. |
| Wave 4 | Serving & RAG | Week 9–11 | ⏳ Not Started | Dependent on Wave 3 outputs. |
| Wave 5 | Continuous Improvement | Week 11–14 | ⏳ Not Started | Roadmap draft only. |

Status icons: ✅ (Done) • ⚠️ (In Progress with blockers/risks) • ⏳ (Not Started)

## Sprint Drill-Down

### Wave 1 – Acquisition Hardening (Week 1–3)
- **Sprint 1.1 (Current)**
  - ✅ Datos Abiertos scraper running with `--force` (PID 79954).
  - ❌ SRI scraper not running (restart required).
  - ⏳ Add structured logging + alerting hooks.
- **Sprint 1.2 (Next)**
  - Deliver SERCOP OCDS harvester.
  - Draft municipal data intake configs.
  - Publish ingestion coverage dashboard (Grafana/Quicksight candidate).

### Wave 2 – Processing & Curation (Week 3–6)
- Sprint 2.1: Containerize preprocessing jobs, Step Functions definitions.
- Sprint 2.2: Implement tagging/dedupe, produce curated preview dataset.
- Sprint 2.3: Package SFT datasets + eval sets.

### Wave 3 – Training & Evaluation (Week 6–9)
- Sprint 3.1: Baseline SageMaker training job (smoke test).
- Sprint 3.2: Full SFT + HPO + cost instrumentation.
- Sprint 3.3: Automated + human eval harness; registry gates.

### Wave 4 – Serving & RAG (Week 9–11)
- Sprint 4.1: Deploy fp16 endpoint, update RAG compose stack, monitoring dashboards.
- Sprint 4.2: Quantized variants, traffic shifting, QA cadence.

### Wave 5 – Continuous Improvement (Week 11–14)
- Sprint 5.1: Drift detection, security hardening, source backlog grooming.
- Sprint 5.2: Feedback ingestion service, vector store upgrade RFC, roadmap refresh.

## Compras Públicas (SERCOP) Initiative

**Objective:** Deliver end-to-end ingestion of procurement data (OCDS) to support fiscal transparency QA and RAG citations.

### Milestone Timeline
| Milestone | Target | Owner | Status |
| --- | --- | --- | --- |
| API Recon & Auth Validation | 2025-10-23 | Data Engineering | ⏳ Not Started |
| Schema + Storage Design | 2025-10-25 | Data Engineering | ⏳ Not Started |
| Harvester Implementation (`real_sercop_scraper.py`) | 2025-10-28 | Data Engineering | ⏳ Not Started |
| Dry-Run QA (10 dataset sample) | 2025-10-30 | Data QA | ⏳ Not Started |
| Production Launch | 2025-11-01 | Data Ops | ⏳ Not Started |
| Dashboard Update & Alerts | 2025-11-03 | Platform | ⏳ Not Started |

### Activity Breakdown
- **Discovery & Design**
  - Confirm OCDS endpoints, pagination, auth, and rate limits.
  - Define metadata schema (release ID, tender value, supplier, SIC codes, status).
  - Map storage layout: `s3://yachaq-lex-raw-0017472631/sercop/year=YYYY/month=MM/`.
- **Implementation**
  - Scaffold harvester using existing CKAN runner patterns.
  - Support incremental sync, resumable checkpoints, and data ledger JSONL.
  - Integrate logging hooks compatible with ingestion dashboard.
- **Validation & Launch**
  - Dry-run with sample date range; verify data completeness vs manual download.
  - QA checklist: schema validation, checksum, dedupe, license compliance.
  - Schedule production cron on `yachaq-scrape-1`; ensure PID/log management.
- **Post-Launch**
  - Add coverage metrics to dashboard.
  - Feed processed outputs into Step Functions once Wave 2 begins.

## Immediate Action Items
- [ ] Restart SRI scraper using `run_sri.sh` (or direct Python command) and confirm PID.
- [ ] Enable structured logging for Datos Abiertos + SRI (format: JSON per line).
- [ ] Kick off SERCOP discovery milestone (capture in issue tracker).
- [ ] Update this roadmap after Sprint 1.1 demo.
