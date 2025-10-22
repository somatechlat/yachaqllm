# Data Ingestion Playbook

This document defines how we collect, validate, and operate the YACHAQ-LEX data pipeline. All instructions here supersede earlier notes.

## Source Inventory

| Source | Script / Status | Notes |
| --- | --- | --- |
| Servicio de Rentas Internas (SRI) | `rag/ingest/real_sri_datasets_scraper.py` (production) | Handles annual CSVs, uploads to `s3://yachaq-lex-raw-0017472631/sri/`. |
| Registro Oficial | `rag/ingest/real_registro_oficial_scraper.py` (production) | Scrapes gazettes and metadata. |
| Asamblea Nacional | `rag/ingest/real_asamblea_scraper.py` (production) | Legislative documents. |
| Datos Abiertos (CKAN) | `rag/ingest/real_datosabiertos_scraper.py` (production) | Enumerates full CKAN catalog; CLI options below. |
| SERCOP (Compras Públicas) | `rag/ingest/real_sercop_scraper.py` (planned) | OCDS API harvester (design complete, implementation pending). |
| Academic DSpace Repositories | Template harvester (planned) | See DSpace section for keyword + metadata guidance. |

## Running Scrapers Locally

Activate the virtual environment and run with conservative limits before production:

```bash
source .venv/bin/activate
python rag/ingest/real_datosabiertos_scraper.py --dry-run --limit 10 --dataset-limit 5 --verbose
```

Key flags:
- `--dry-run`: stores files under `datosabiertos_local/` instead of S3.
- `--limit`: caps total resources; use for quick smoke tests.
- `--dataset-limit`: limits number of datasets.
- `--force`: reprocesses resources already recorded in JSONL ledgers.

After validation, remove `--dry-run` to stream results to S3.

## Running on the Scraper VM

1. Copy scripts via `gcloud compute scp` to `/home/macbookpro201916i964gb1tb/yachaqllm_repo/`.
2. Use helper launchers for long jobs. Example for Datos Abiertos:
   ```bash
   gcloud compute ssh yachaq-scrape-1 --project=gen-lang-client-0017472631 --zone=us-central1-a --command "cd yachaqllm_repo && ./run_datosabiertos.sh"
   ```
3. Monitor progress with:
   ```bash
   gcloud compute ssh yachaq-scrape-1 --project=gen-lang-client-0017472631 --zone=us-central1-a --command "cd yachaqllm_repo && tail -f datosabiertos_full.log"
   ```
4. Confirm process with `pgrep -a -f real_datosabiertos_scraper.py`.
5. Stop jobs cleanly using `pkill -f real_datosabiertos_scraper.py` when needed.

## Storage Conventions

- **Raw data**: `s3://yachaq-lex-raw-0017472631/<source>/year=YYYY/...`
- **Metadata ledgers**: JSONL files under `rag/ingest/*_data.jsonl` (synced to S3 before processing).
- **Local dry-run directories**: `datosabiertos_local/`, `sri_local/` – ignored via `.gitignore`.
- Each record must include source, ID, title, description, tags, license, SHA256, content length, crawl timestamp, and storage location.

## DSpace Repositories (Academia)

All university repositories share a common harvesting approach:

1. **Discovery**
   - Use DSpace REST (`/rest/search/`) or HTML `simple-search` endpoints.
   - Iterate through collections/communities when available.

2. **Domain Filters**
   - Apply keywords across title, abstract, and subject fields:
     - Tax/accounting: `contabilidad`, `impuesto`, `tributación`, `SRI`, `auditoría`, `NIIF`.
     - Administrative law: `derecho administrativo`, `gestión pública`, `trámite`, `ventanilla única`.
     - Customs: `aduanas`, `SENAE`, `arancel`, `régimen aduanero`, `importación`, `exportación`.
     - Procurement: `SERCOP`, `contratación pública`, `compras públicas`, `presupuesto`.
     - Municipal procedures: `ordenanza`, `GAD`, `licencia`, `catastro`.
   - Discard off-topic matches automatically; perform manual QA on samples.

3. **Metadata Fields**
   - Capture: title, authors, degree, faculty, keywords, abstract, submission date, URI, download URL.
   - Store extracted text and metadata JSON side-by-side for downstream processing.

4. **Downloading**
   - Stream PDFs; compute SHA256 and file size.
   - Save to `s3://yachaq-lex-raw-0017472631/academia/institution=<sigla>/year=YYYY/`.

5. **Future Automation**
   - Standardize via a reusable harvester template (TBD script name `real_dspace_scraper.py`).
   - Parameter file per institution to define community IDs, throttle settings, and keyword overrides.

## Upcoming Scrapers

- **SERCOP (OCDS)**
  - Endpoints: `https://portal.compraspublicas.gob.ec/sercop/data/` (JSON releases).
  - Plan: implement pagination, date filters, and resource downloads; store JSON bundles compressed.

- **Municipal Portals** (Quito, Cuenca, Guayaquil)
  - Identify structured datasets (CSV, JSON) related to trámites and ordinances.
  - Document each portal’s rate limits and authentication requirements.

## Operational Checklist
- [ ] Run local dry-run with limits for every new scraper.
- [ ] Capture log sample (`tail -n 50`) and attach to PR for traceability.
- [ ] Sync updated metadata JSONL to S3 before processing jobs.
- [ ] Record ingestion completion in coverage dashboard (to be implemented).
- [ ] Archive logs and PID files after production runs.
