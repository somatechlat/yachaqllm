# Sprint 1 Plan — Discovery & Canonical Traces

Goal
----
Produce a working discovery runner that can capture canonical traces for any target site. This sprint delivers a minimal, runnable discovery tool (requests-based fallback) that outputs traces conforming to `docs/trace-schema.md`. The full Pydoll integration will follow in Sprint 2; this sprint provides immediate value and testable artifacts.

Scope & Acceptance
------------------
- Deliver a discovery runner that accepts a URL and writes a canonical trace JSON and a raw response artifact.
- Produce 3 canonical traces for representative queries (to be collected by discovery engineers).
- Provide contract-test skeletons and CI-friendly tests that validate the produced traces have required fields.

Work items (tasks)
-------------------
1. Implement `rag/discovery/pydoll_discovery.py` (skeleton implementation using requests): 2 days
   - CLI runner: accept URL, output dir
   - Save raw response and minimal trace JSON conforming to `docs/trace-schema.md`
2. Tests & CI hooks: 1 day
   - Unit tests for discovery API (no external network required)
   - Contract-test placeholders that will run against the saved traces
3. Capture canonical traces: 1 day
   - Use the discovery runner to capture traces for 3 representative queries; store under `traces/`.
4. Review & handoff: 1 day
   - Team review of traces and update of trace-schema if gaps found

Deliverables
------------
- `rag/discovery/pydoll_discovery.py` (CLI + API)
- `traces/` sample artifacts (3 traces)
- Unit test skeletons in `tests/`
- Updated `docs/` references if necessary

Risks & mitigation
------------------
- Network variability may affect trace capture — we store raw responses and use sanitized copies for tests.
- Pydoll integration postponed to Sprint 2; ensure the trace schema supports later CDP-level fields.

Definition of Done
------------------
- Discovery runner writes at least one canonical trace with the minimal required fields and a raw response artifact. Tests for API and CI hooks exist and pass locally.

---
Document owner: Yachaq Data Platform
File: docs/sprint-1-plan.md
