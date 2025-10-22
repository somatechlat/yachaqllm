# Captcha Adapter Specification (Canonical)

Purpose
-------
This document defines the canonical interface and behavior expected from Captcha Solver adapters used by the harvesting pipeline. The Captcha Service must be pluggable, mockable for tests, auditable, and support three-tier fallback (OCR → external solver → human-in-the-loop).

Goals
-----
- Provide a consistent adapter interface for different solver backends.
- Ensure TTL, confidence, and audit metadata are captured.
- Support synchronous and asynchronous solve flows (external solver or manual human solve).
- Provide mockable behavior for unit and integration testing.

Core concepts
-------------
- Captcha Task: an artifact containing the captcha image and sufficient context to submit a solver request.
- Adapter: a pluggable component implementing the solver interface for a backend (local OCR, provider API, manual UI).
- Attempt: a single attempt by an adapter to solve the captcha; adapters may return multiple attempts.
- TTL: time-to-live (seconds) of a captcha task; solutions older than TTL are invalid.

High-level flow
---------------
1. Harvester requests a captcha for a Job/Trace when a captcha image is encountered.
2. Captcha service enqueues and selects adapter(s) according to configuration and policy.
3. Adapter attempts to solve and returns a `SolveResult` or a `Pending` status (for human-in-loop).
4. Captcha service records attempt in audit and returns final `SolveResult` to harvester when solved or indicates failure/timeouts.

Adapter Interface (canonical)
-----------------------------

All adapters MUST implement the following interface (pseudocode namespaced, description only):

- solve(task: CaptchaTask, timeout_seconds: int) -> SolveResult | PendingResult | AdapterError
- status(task_id: string) -> PendingStatus | SolveResult | AdapterError
- cancel(task_id: string) -> CancelResult

Types
-----

CaptchaTask
- Fields:
  - task_id: string (unique)
  - image_key: string (storage key or raw base64)
  - image_encoding: string (e.g., "png", "jpeg", "base64")
  - context: object (form defaults, headers, referer, session_id)
  - created_at: ISO8601
  - ttl_seconds: int

SolveResult
- Fields:
  - task_id: string
  - adapter: string (adapter id)
  - result: string (solved text)
  - confidence: float (0.0-1.0)
  - latency_ms: int
  - timestamp: ISO8601
  - metadata: object (adapter-specific info)

PendingResult
- Fields:
  - task_id
  - adapter (e.g., "human-queue")
  - pending_token: string (reference used to fetch final result)
  - estimated_wait_seconds: int
  - timestamp

PendingStatus
- Fields:
  - task_id
  - state: "pending"|"completed"|"expired"
  - result: SolveResult|null
  - attempts: array of attempt metadata

AdapterError
- Fields:
  - task_id
  - adapter
  - error_code: string
  - message: string
  - retryable: boolean
  - timestamp

CancelResult
- Fields:
  - task_id
  - adapter
  - cancelled: boolean
  - timestamp

Adapter behavior & policies
---------------------------
- Timeouts: adapters must respect the provided `timeout_seconds`. If the adapter cannot finish within the timeout, it should return a retryable AdapterError.
- Retries: adapters may internally retry; the Captcha Service is responsible for global retry budgets.
- Confidence thresholds: caller (harvester) decides minimum confidence for auto-accept. Low-confidence results should trigger fallback to next adapter.
- Human-in-loop: if configured adapters return PendingResult, system must provide a human queue with TTL awareness.

Audit & provenance
------------------
Every attempt must be logged to an audit store (artifact), including:
- task_id, adapter, result (if any), confidence, latency_ms, timestamp, attempt_number
- image_key and reference to trace/job where the captcha originated
- adapter-specific metadata (solver_id, cost, API response id)

Security & secrets
------------------
- Adapter credentials (API keys) must be stored in the secrets manager and never in trace manifests.
- When adapters log metadata, they MUST NOT log raw API keys or secrets.

Failure modes & recommended handling
-----------------------------------
- Temporary solver outage: mark attempt as retryable; use exponential backoff and fallbacks.
- Low confidence: fallback to next adapter (OCR → external → human) or mark for manual resolution.
- Expired captcha (TTL exceeded): discard solves and re-run discovery to obtain a fresh captcha; do not use old solves.

Testing & mocks
---------------
- Provide a MockAdapter that responds deterministically for unit and integration tests.
- Provide canned sample captcha images for offline OCR tests.

Operational controls
--------------------
- Rate limits / cost governor: caps on adapter usage per time window and budget alerts.
- Metrics: attempts_total, attempts_success, attempts_failure, avg_latency_ms, pending_queue_size
- Alerts: high failure rate, pending queue age exceeds TTL/2, adapter cost threshold reached

Example usage
-------------
- Harvester calls CaptchaService.solve(task, timeout=20)
- CaptchaService calls OCRAdapter.solve(); if result.confidence < 0.6, call ExternalAdapter.solve(); if still low or fail, push to HumanAdapter and return PendingResult.

Document owner: Yachaq Data Platform
File: docs/captcha-adapter.md
