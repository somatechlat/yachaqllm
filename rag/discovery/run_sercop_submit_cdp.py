#!/usr/bin/env python3
"""Use Pydoll (CDP) to open the SERCOP search page, fill the search form, submit it,
and save a high-fidelity trace (screenshot + HTML snippet) to an output dir.

This is best-effort: it wraps many pydoll APIs in try/except to handle version
differences. It requires `pydoll` to be installed in the active environment and
Chrome available on the system.
"""
from __future__ import annotations

import asyncio
import base64
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


def _import_pydoll():
    try:
        import pydoll  # type: ignore
        import pydoll.browser  # type: ignore
        return pydoll
    except Exception:
        return None


async def run_submit(url: str, out_dir: str = "rag/discovery/out_sercop_cdp_submit") -> int:
    pydoll = _import_pydoll()
    if pydoll is None:
        print("Pydoll not installed in this environment")
        return 2

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    trace_id = str(uuid.uuid4())
    capture_time = datetime.now(timezone.utc).isoformat()

    try:
        async with pydoll.browser.Chrome() as browser:  # type: ignore[attr-defined]
            tab = await browser.start()

            # try enable network (best-effort)
            client = getattr(tab, "client", None)
            try:
                if client is not None:
                    await client.send("Network.enable")  # type: ignore
            except Exception:
                pass

            # navigate to page
            try:
                await tab.go_to(url)
            except Exception:
                try:
                    await tab.navigate(url)
                except Exception:
                    pass

            # allow some settle time / network idle
            try:
                await tab.wait_for_network_idle(timeout=5)
            except Exception:
                await asyncio.sleep(1)

            # Prepare a JS snippet that finds the first form and fills some fields
            # We'll set the date range and leave other fields as-is.
            js_fill = (
                "(function(){"
                "var f = document.forms[0]; if(!f) return {error:'no-form'};"
                "var set = function(n,v){ try{ var el = f.elements[n]; if(el) el.value=v;}catch(e){} };"
                "set('txtPalabrasClaves','');"
                "set('txtCodigoTipoCompra','TODOS');"
                "set('f_inicio', '2025-04-22'); set('f_fin','2025-10-22');"
                "return {hasForm:true, action:f.action || null, method:f.method || null}; })();"
            )

            eval_fn = getattr(tab, "eval", None) or getattr(tab, "evaluate", None)
            form_result = None
            try:
                if callable(eval_fn):
                    form_result = await eval_fn(js_fill, return_by_value=True)  # type: ignore
            except Exception:
                form_result = None

            # Submit the form via JS (call submit or click submit button)
            js_submit = (
                "(function(){ var f = document.forms[0]; if(!f) return {error:'no-form'};"
                "var btn = f.querySelector('[type=submit]') || f.querySelector('button');"
                "if(btn){ btn.click(); return {submitted:true}; } else { f.submit(); return {submitted:true}; } })();"
            )

            submit_result = None
            try:
                if callable(eval_fn):
                    submit_result = await eval_fn(js_submit, return_by_value=True)  # type: ignore
            except Exception:
                submit_result = None

            # Wait for navigation/network activity after submit
            try:
                await tab.wait_for_navigation(timeout=10)
            except Exception:
                try:
                    await tab.wait_for_network_idle(timeout=5)
                except Exception:
                    await asyncio.sleep(2)

            # capture screenshot
            screenshot_b64 = None
            try:
                screenshot_b64 = await tab.take_screenshot(as_base64=True)
            except Exception:
                screenshot_b64 = None

            # capture HTML snippet
            html_snippet = None
            try:
                if callable(eval_fn):
                    html_snippet = await eval_fn("document.documentElement.outerHTML", return_by_value=True)  # type: ignore
            except Exception:
                html_snippet = None

            # Save screenshot
            screenshots = []
            if screenshot_b64:
                try:
                    try:
                        ss_bytes = pydoll.utils.decode_base64_to_bytes(screenshot_b64)  # type: ignore[attr-defined]
                    except Exception:
                        ss_bytes = base64.b64decode(screenshot_b64)
                    ss_path = out / f"{trace_id}.png"
                    ss_path.write_bytes(ss_bytes)
                    screenshots.append({"screenshot_id": "ss-1", "timestamp": capture_time, "storage_key": str(ss_path.name)})
                except Exception:
                    pass

            trace: Dict = {
                "trace_version": "1.0",
                "trace_id": trace_id,
                "capture_time": capture_time,
                "source": {"source_id": "pydoll-cdp", "source_name": "pydoll-cdp", "environment": "local"},
                "page_url": url,
                "browser": {"user_agent": "pydoll", "browser_version": "unknown", "headless": True, "platform": "cdp"},
                "session": {"session_id": trace_id},
                "form_extractions": [form_result] if form_result else [],
                "events": [],
                "screenshots": screenshots,
                "artifacts": {"raw_response_keys": {}, "html_snippet": (html_snippet or '')[:20000]},
                "metadata": {"capture_agent": "pydoll_cdp_submit_helper"},
                "audit": {"captchas": []},
            }

            # write trace
            (out / f"{trace_id}.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2))

            print("Wrote CDP submit trace", trace_id, "to", out)
            return 0

    except Exception as exc:  # pragma: no cover - runtime
        print("CDP submit failed:", exc)
        return 3


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    url = argv[0] if argv else "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/PC/buscarProceso.cpe?sg=1"
    out = argv[1] if len(argv) > 1 else "rag/discovery/out_sercop_cdp_submit"
    return asyncio.run(run_submit(url, out))


if __name__ == "__main__":
    raise SystemExit(main())
