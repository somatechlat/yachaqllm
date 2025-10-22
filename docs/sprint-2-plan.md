# Sprint 2 Plan — Pydoll (CDP) Discovery Integration

Goal
----
Integrate Pydoll to produce high-fidelity discovery traces capturing DOM-derived tokens, XHRs, screenshots and captcha images. These traces will be the authoritative source for building production harvesters and contract tests.

Scope
-----
- Implement an async Pydoll-based discovery runner that captures network events and forms.
- Persist screenshots, captcha images, raw responses and canonical traces as per `docs/trace-schema.md`.
- Create integration tests (skip when Pydoll not installed) and docs for running locally.

Acceptance criteria
-------------------
1. The CDP runner launches Chrome via Pydoll and navigates to target URL.
2. The runner captures XHR events and records request/response headers + bodies into the trace.
3. The runner extracts form inputs (including dynamic tokens) and records a serialized example.
4. If a captcha image is present, the runner saves the image and writes a captcha artifact entry into trace.audit.captchas.
5. A sample trace is written for at least one target and validated against `docs/trace-schema.md`.

Tasks & estimate (solo developer)
---------------------------------
1. Implement Pydoll capture harness (3 days)
   - launch browser, start tab, navigate, enable network logging
   - intercept network events (request/response bodies)
   - capture screenshots and DOM snapshots
2. Form extraction & serialization (1 day)
   - parse DOM to find target forms, extract field names/values and mark dynamic fields
3. Captcha detection & artifact extraction (1 day)
   - detect images with likely captcha ids/classes and save image blob
4. Tests & docs (1 day)
   - integration test that runs only if `pydoll-python` is installed
   - usage docs and sample command lines

Run instructions (dev machine)
-----------------------------
1. Install Pydoll in your virtualenv: `pip install pydoll-python`
2. Activate venv and run the CDP discovery script (example):

```bash
source .venv/bin/activate
python -m rag.discovery.pydoll_cdp_discovery_cli "https://target.example/search"
```

Notes
-----
- Pydoll and Chrome versions should be compatible. If Pydoll cannot find Chrome, set a custom binary path in the script options.
- Keep traces small for CI by sampling requests and storing large bodies as separate artifacts.

Document owner: Yachaq Data Platform
File: docs/sprint-2-plan.md
