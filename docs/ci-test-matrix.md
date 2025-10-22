# CI Test Matrix & Contract Tests

Purpose
-------
Define which tests run at each CI gate and outline contract-test definitions derived from canonical traces.

CI gates
--------
- Pull Request (PR) Gate — Fast tests
  - Linting (style, static typing)
  - Unit tests (fast, < 60s)
  - Contract smoke tests (verify payload builder against small set of canonical traces)

- Merge to main — Integration
  - All PR tests
  - Integration tests with mocked adapters/services
  - Contract tests (full set)

- Release / Deploy — Staging E2E
  - All integration tests
  - End-to-end run on staging (manual-solve or mocked solver)
  - Canary harvests and trace-drift check

Test categories
---------------
- Unit tests: form parsers, payload serializer, adapter mocks, retry logic
- Contract tests: for each canonical trace, assert correct request recreation and response shape
- Integration tests: harvester against mock HTTP server that emulates target behaviors (login redirect, captcha response, pagination)
- E2E/Canary: execute Pydoll discovery + harvester on staging; validate parsed outputs and manifests

Contract test definition (example)
---------------------------------
Given: canonical trace T containing event e-1 (XHR)
Assertions:
1. Reconstructed request URL and method match e-1 (path+query normalized)
2. For each header in `replay_hints.canonical_headers`, header is present with matching semantics
3. For canonical form fields, form payload equals e-1.form_fields (or canonical subset)
4. Response shape: if e-1.response.body_snippet indicates JSON with top-level `count` integer, assert parser can parse this structure

Failure modes:
- If a contract test fails on PR, fail the PR and surface diff artifact for review.
- If a contract test fails on main (post-merge), block release and run Pydoll discovery to detect drift.

Test data management
--------------------
- Maintain a `tests/traces/` directory with sanitized canonical traces for contract tests.
- Golden response snippets and expected parsed outputs stored in `tests/golden/` and versioned.

CI pipeline tips
----------------
- Keep PR gate fast: select a small subset of canonical traces for quick contract checks.
- Run full contract suite on main to detect regressions early.
- For E2E runs, prefer lightly-sampled canaries to avoid solver costs.

Document owner: Yachaq Data Platform
File: docs/ci-test-matrix.md
