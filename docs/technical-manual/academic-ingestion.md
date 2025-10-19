# Academic Ingestion Playbook

This playbook describes the end-to-end process for harvesting Ecuadorian academic corpora, persisting them in S3, and preparing curated datasets for YACHAQ-LLM SageMaker training jobs.

## Roles and Tooling

- **Crawler Frameworks:** Scrapy for structured navigation, Selenium for JavaScript-heavy pagination, and OAI-PMH harvesters for native DSpace endpoints.
- **Parsing Stack:** BeautifulSoup (HTML), pdfminer or pypdf (PDF extraction), Apache Tika as fallback for complex documents.
- **Storage:** `s3://yachaq-lex-data-bucket-<suffix>/raw/ecuador_academia/` for raw downloads, `s3://yachaq-lex-data-bucket-<suffix>/curated/` for cleaned text chunks.
- **Orchestration:** Each source has an explicit entry in `config/ecuador_academic_sources.yaml`. Orchestrators read this manifest and launch dedicated jobs.
- **Metadata Contract:** Every record uses the schema defined in `rag/app/contracts.py` extended with academic fields (`authors`, `institution`, `degree`, `license`, `language`).

## Pipeline Stages

1. **Source Selection:** Choose a single repository from the manifest. Update the run sheet with the planned crawl window to avoid overlap.
2. **Harvest:** Execute the designated harvester (Scrapy, Selenium, or OAI-PMH). Respect rate limits (default 1 req/sec) and capture full metadata plus file URLs.
3. **Persist Raw Assets:** Upload source PDFs/HTML to the raw S3 prefix (`<prefix>/<institution>/<YYYY>/<MM>/<DD>/<document_id>.pdf`). Attach a JSONL manifest summarizing metadata, SHA256 hash, and license.
4. **Validate:** Run automated validation (schema checks, language detection, license verification). Failures remain in raw storage with a rejection reason for manual review.
5. **Transform:** Extract text into paragraph-level chunks, append normalized metadata, and store parquet/JSONL outputs under the curated prefix. Maintain provenance by referencing the raw object key.
6. **Indexing:** Optionally feed curated text into Qdrant for retrieval evaluation while the training corpus is staged.
7. **SageMaker Preparation:** Group curated outputs into sharded training files (`*.jsonl.zst`) and update the SageMaker channel manifest (`training/configs/yachaq_academia.json`).
8. **Audit Trail:** Record every run in `rag/ingest/logs/harvest_history.csv` with columns `timestamp,institution,documents_total,documents_failed,s3_prefix,operator`.

## Quality and Compliance Checks

- Ensure every document has a license compatible with redistribution (Creative Commons or institutional open access statements).
- Scrub personally identifiable information if it falls outside theses/public records (e.g., emails in acknowledgements).
- Verify Spanish language coverage; flag documents with non-Spanish primary language for separate processing.
- Keep Git clean: no raw documents or keys committed to the repository. Use `.gitignore` safeguards around local staging folders.

## Integration with SageMaker

- Training jobs reference the curated S3 prefix and the manifest file produced in Stage 7.
- Hyperparameters for localized legal/tax fine-tuning live in `training/configs/yachaq_sagemaker_params.json` (to be added once training scripts are finalized).
- After each training run, export evaluation metrics back to `rag/eval/` and log them in the experiment tracker.

## Next Steps

- Implement per-source spiders based on the manifest entries.
- Build automated validation scripts aligned with the extended metadata contract.
- Add CI secret scanning to enforce the updated secrets policy.
