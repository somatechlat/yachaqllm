# Canonical Trace JSON Schema (Discovery Traces)

Version: 1.0

Purpose
-------
This document defines the canonical JSON schema for browser discovery traces (HAR-like) captured by the Pydoll discovery tool. Traces capture all information required to reproduce client behavior, derive request payloads for production harvesters, power contract tests, and provide forensic artifacts for incidents.

Design goals
------------
- Complete: capture requests/responses, DOM-derived tokens, screenshots.
- Replayable: enough context to rebuild requests in a new session.
- Auditable: store solver attempts, capture provenance, and trace_id.
- Privacy-aware: cookie/token storage is optional and encrypted.
- Versioned: schema version field for migrations.

Top-level shape
---------------

All traces MUST follow this top-level structure:

- trace_version: string (schema version, e.g. "1.0")
- trace_id: string (unique id)
- capture_time: ISO8601 timestamp (UTC)
- source: object { source_id, source_name, environment }
- page_url: string (the URL visited)
- browser: object { user_agent, browser_version, headless: bool, platform }
- session: object { session_id, cookies_reference?, cookie_summary? }
- form_extractions: array of extracted forms
- events: array of network events (ordered by time)
- dom_snapshot: optional (path/key or inline stripped DOM)
- console_logs: array of console messages
- screenshots: array of screenshot metadata
- annotations: array of user/system annotations
- replay_hints: object (normalization rules, canonical headers)
- artifacts: object (external storage keys for large bodies)
- metadata: object (job_id if triggered by job, environment tags)
- audit: object (captchas encountered, solver attempts)
- signatures: object (optional integrity signature)

Field details
-------------

trace_version
- string, e.g. "1.0"

trace_id
- string, globally unique id (UUID or timestamp-prefixed id)

capture_time
- ISO8601 (UTC) when capture started

source
- source_id: string (logical id)
- source_name: string
- environment: string (dev|staging|prod)

page_url
- full URL visited

browser
- user_agent: string
- browser_version: string
- headless: boolean
- platform: string
- options: object (optional list of flags)

session
- session_id: string
- cookies_reference: optional string (external storage key for encrypted cookie jar)
- cookie_summary: optional object mapping cookie-name → { present: bool, expires: ISO8601|null, secure: bool }

form_extractions
- Array, one per form of interest. Each object:
  - form_id: string|null
  - form_selector: CSS or XPath
  - action: string
  - method: GET|POST
  - extracted_fields: array of { name, value, type (input/select/textarea/hidden), is_dynamic:boolean, notes }
  - serialized_example: string (JS Form.serialize() or equivalent)
  - timestamp: ISO8601

events (network events)
- Ordered array; each event represents a captured network interaction.
- Event object:
  - event_id: string
  - type: "xhr"|"document"|"fetch"|"stylesheet"|"image"|"other"
  - initiator: string (script|user)
  - request: { method, url, headers, body|null, body_encoding?, form_fields? }
  - response: { status, headers, body_snippet?, body_size, body_storage_key?, content_type, duration_ms }
  - timestamp_start / timestamp_end
  - replayable_hint: boolean (essential to replay flow)
  - notes: optional

dom_snapshot
- Optional: path/key or inline sanitized DOM. Prefer external storage for large snapshots.

console_logs
- Array of { level: log|warn|error, message, timestamp }

screenshots
- Array of { screenshot_id, timestamp, storage_key, width, height }

annotations
- Array of { actor: system|user, message, timestamp, severity }

replay_hints
- canonical_headers: array[string] (headers that must be reproduced)
- headers_ignore_list: array[string]
- canonicalize_payload_rules: object
- recommended_sequence: array[event_id]

artifacts
- raw_response_keys: map event_id → storage_key
- raw_cookie_key: optional storage_key (encrypted)
- trace_snapshot_key: key for entire saved trace

metadata
- job_id: optional
- capture_agent: string
- tags: array[string]

audit
- captchas: array of { captcha_id, event_id, image_key, attempts: [{ adapter, result, confidence, timestamp, note }], final_status }
- solver_summary: { total_attempts, successes, avg_latency_ms }

signatures
- optional integrity metadata: { signature_id, algorithm, signature_value }

Minimal required fields for contract tests
----------------------------------------

Traces intended for automated contract tests must include at least:
- trace_version, trace_id, capture_time
- page_url, browser.user_agent
- session.cookie_summary or cookies_reference
- form_extractions with at least one relevant form
- events[] with XHR(s) of interest including request.method, request.url, request.headers and request.body/form_fields and response.status
- artifacts.raw_response_keys or response.body_snippet
- replay_hints.canonical_headers

If any of the above are missing the trace is flagged as "insufficient for automated replay".

Storage & lifecycle
-------------------
- Store traces under `traces/<source>/...` partition
- Large bodies stored as separate artifacts; link via `body_storage_key`
- Sensitive artifacts encrypted (raw cookie jars)
- Retention: canonical traces ≥ 90 days (configurable)

Example (conceptual snippet)
----------------------------

See the `trace` produced by the Pydoll discovery run for a minimal example: it will contain `form_extractions` with the serialized POST payload and an `events[]` entry with `replayable_hint=true` pointing to the XHR of interest.

Acceptance criteria for a canonical discovery trace
--------------------------------------------------
1. Contains at least one `form_extractions` for the interaction of interest with details.
2. Contains the XHR event(s) used to fetch listings with full request.headers and form fields.
3. Contains response.status and either `body_snippet` or `body_storage_key` for each important event.
4. Includes at least one screenshot.
5. Lists `replay_hints.canonical_headers`.
6. Does not inline raw cookie values unless encrypted and referenced via `artifacts.raw_cookie_key`.

Usage notes
-----------
- Discovery engineers should run Pydoll to capture traces for representative queries. Those traces become the single source-of-truth for payload building and contract tests.
- Contract tests are derived from traces and should fail CI if canonical headers/payload shape changes unexpectedly.

---
Document owner: Yachaq Data Platform
File: docs/trace-schema.md
