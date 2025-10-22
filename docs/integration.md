## YACHAQ-LEX Capture & Extraction Integration

This document describes the canonical integration between the capture engine (Pydoll),
the lightweight fallback (requests), the extractor (Crawl4AI), and the captcha queue (human-first).

Goals
- Reproducible captures: every CDP capture MUST save a full HTML snapshot and a screenshot.
- Deterministic post-processing: Crawl4AI runs against saved HTML snapshots (no re-fetch).
- Human-first captcha handling: when a captcha is detected, a manifest JSONL line is appended to the canonical queue and humans solve within TTL.

Roles
- Pydoll (capture): capture screenshots, network events, and save `html_snapshot` file. Produces a trace JSON linking to artifacts.
- requests (fallback): deterministic HTTP-level capture and form submit; produces trace JSON and downloads captcha images when present.
- Crawl4AI (extractor): run as a post-processor on the saved HTML snapshot and produce Markdown/structured JSON for RAG.
- Captcha queue (human): `rag/ingest/comprehensive_data/sercop_captcha_queue/manifest.jsonl` is the canonical manifest file.

Workflow (canonical)
1. Capture: run Pydoll capture for URL → produces `trace_id.json`, `trace_id.png`, and `trace_id.html`.
2. Detection: capture code inspects DOM/HTML for captcha artifacts (e.g., `generadorCaptcha.php`).
3. Manifest: if captcha present, create a manifest JSONL entry containing `form_defaults`, `cookies`, `captcha_path`, `captcha_src`, `referer`, `search_url`, `ttl_hint_seconds`.
4. Postprocess: call Crawl4AI on the saved HTML snapshot to generate Markdown and structured JSON; save results adjacent to the trace.
5. Human solve: human solver consumes manifest, solves captcha and returns solution to ingestion pipeline for final submission.

Acceptance criteria
- Every new trace has `artifacts.html_snapshot` pointing to a saved HTML file.
- Crawl4AI runs on the saved file and produces Markdown that includes the form text and captcha reference.
- Manifest entries are appended immediately when captcha is detected and include cookies.

Notes
- Mock adapters are allowed for unit tests only; production runtime uses the human-first adapter.
