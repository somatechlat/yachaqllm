# Job Manifest & Parsed Output Schema (Canonical)

Purpose
-------
Defines the canonical job manifest and parsed output formats used by the harvesting pipeline. Manifests provide durable linkage between scheduled jobs, discovery traces, captcha artifacts, raw responses and parsed outputs to enable replay, audit and idempotent reprocessing.

Design goals
------------
- Durable: represent job state sufficiently to resume and replay.
- Minimal secrets exposure: do not inline raw cookies or API secrets.
- Reusable: generic for any scraping target.
- Testable: mapping supports contract tests and can be validated in CI.

Top-level Job Manifest (one JSON object per job)
----------------------------------------------

Fields (required):

- job_id: string (unique id)
- created_at: ISO8601
- source_id: string (logical source)
- source_name: string
- scheduled_for: ISO8601 (when job scheduled)
- initiated_by: string (system|user|canary)
- status: string enum (pending|in_progress|succeeded|failed|cancelled)
- trace_id: optional string (if a Pydoll discovery trace was used)
- query_params: object (source-specific parameters used to run the job)
- attempts: int (how many times this job retried)
- last_error: optional object { code, message, timestamp }
- artifacts: object (see below)
- outputs: object (see parsed outputs mapping)
- audit: object (solver attempts summary, operator notes)
- metadata: object (free-form tags)

Artifacts sub-object
--------------------
- raw_response_keys: array[string] (object store keys for raw HTTP responses)
- trace_key: optional string (key of full trace JSON)
- captcha_keys: array[{ captcha_id, image_key, solver_result_key? }]
- cookie_key: optional string (encrypted cookie jar key; avoid inline storage)
- attachments: array[{ attachment_id, storage_key, content_type, size }]

Outputs sub-object
------------------
- parsed_key: string (storage key to NDJSON of parsed records)
- parsed_count: int
- dedup_key: optional string (dedup manifest or record index)

Parsed record NDJSON schema (one line per record)
------------------------------------------------

Each parsed record should contain both scraped data and provenance metadata.

Fields (recommended):
- record_id: string (stable id, e.g., derived from canonical process id or content-hash)
- job_id: string (originating job)
- source_id: string
- capture_time: ISO8601 (when harvested)
- raw_reference: string (raw_response_key or event_id that produced this record)
- extracted: object (domain-specific extracted fields)
- attachments: array[{name, storage_key, content_type, size}]
- hashes: { content_sha256 }
- provenance: { trace_id?, event_id?, url }
- system: { parser_version, extraction_rules_version }

Indexing & dedup
-----------------
- System should compute content hashes (SHA256) for each parsed record and store dedup manifests under `dedup/<source>/<date>/…`.
- Dedup process should be idempotent; record-level `record_id` should be deterministic when possible.

Manifest lifecycle
------------------
- Job manifest is created when job is scheduled and updated as job runs. Transitions: pending → in_progress → (succeeded|failed|cancelled).
- On success: manifest.status = "succeeded", parsed_key and parsed_count set.
- On failure: manifest.status = "failed", last_error populated, attempts incremented.

Best-practices & constraints
-----------------------------
- Avoid storing raw cookies inline; use `cookie_key` referencing encrypted storage.
- Keep manifests small and indexable; use object store keys for large bodies.
- Schemas must be versioned; include `manifest_schema_version` in metadata.

Example minimal manifest (conceptual)

{
  "job_id": "job-20251022-0001",
  "created_at": "2025-10-22T16:00:00Z",
  "source_id": "targetX",
  "scheduled_for": "2025-10-22T16:01:00Z",
  "initiated_by": "system",
  "status": "succeeded",
  "trace_id": "trace-20251022-0001",
  "query_params": {"q": "computador"},
  "attempts": 1,
  "artifacts": {"raw_response_keys": ["raw/targetX/job-.../e-1.json"], "captcha_keys": []},
  "outputs": {"parsed_key": "parsed/targetX/2025-10-22/job-...ndjson", "parsed_count": 20}
}

Document owner: Yachaq Data Platform
File: docs/manifest-schema.md
