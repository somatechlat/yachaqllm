"""Single-file canonical CDP discovery runner.

This module attempts to use Pydoll when available to capture a high-fidelity
trace (network events, DOM snapshots, screenshots). If Pydoll is not
installed it falls back to a lightweight requests-based capture so you can
generate traces on machines without the CDP dependency.

The goal is to keep all Sprint 2 discovery logic in this one canonical file to
make iteration and testing simpler.
"""

from __future__ import annotations

import base64
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PydollNotInstalled(RuntimeError):
    pass


def _import_pydoll():
    try:
        # Some pydoll packages keep APIs in submodules (e.g., pydoll.browser)
        import pydoll  # type: ignore
        try:
            # ensure the browser submodule is imported so callers can use pydoll.browser
            import pydoll.browser  # type: ignore
        except Exception:
            # ignore: we'll still return the top-level module
            pass
        return pydoll
    except Exception:
        return None


class PydollCDPDiscovery:
    """Canonical discovery runner: Pydoll when available, requests fallback.

    Usage: create instance and call `await capture_trace(url)`.
    """

    def __init__(self, output_dir: str | Path = "rag/discovery/out_cdp") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def capture_trace(self, url: str, user_agent: Optional[str] = None) -> Dict:
        """Capture a trace for the given URL.

        If Pydoll is available this will attempt a CDP capture. Otherwise it
        falls back to a single GET request using requests and writes a minimal
        trace JSON so downstream components can proceed.
        """
        pydoll = _import_pydoll()
        trace_id = str(uuid.uuid4())
        capture_time = datetime.now(timezone.utc).isoformat()

        if pydoll is None:
            # Requests fallback
            return await self._requests_fallback(url, trace_id, capture_time)

        # Attempt Pydoll-based capture. This is defensive: Pydoll versions and
        # helper methods differ, so we try common patterns and gracefully
        # continue when pieces are missing.
        try:
            return await self._pydoll_capture(pydoll, url, user_agent, trace_id, capture_time)
        except Exception as exc:  # pragma: no cover - depends on environment
            logger.exception("Pydoll capture failed, falling back to requests: %s", exc)
            return await self._requests_fallback(url, trace_id, capture_time)

    async def _pydoll_capture(self, pydoll, url: str, user_agent: Optional[str], trace_id: str, capture_time: str) -> Dict:
        # best-effort use of pydoll APIs
        network_events: List[Dict] = []
        screenshot_b64: Optional[str] = None

        # Use a minimal API shape that many pydoll versions expose. We avoid
        # depending on private attributes; everything is wrapped in try/except.
        async with pydoll.browser.Chrome() as browser:  # type: ignore[attr-defined]
            tab = await browser.start()

            # Try enabling network domain if supported
            try:
                if hasattr(tab, "client"):
                    # Some wrappers expose a raw client to call CDP methods
                    await tab.client.send("Network.enable")  # type: ignore
            except Exception:
                logger.debug("Could not enable Network via raw client")

            # Collect events by registering an event sink if available
            events_collector = []

            try:
                # If tab exposes an `on` hook to subscribe to events. In pydoll
                # Tab.on is a coroutine that must be awaited; previously we
                # attempted to call it without awaiting, which raised a
                # RuntimeWarning. Here we register async handlers properly.
                on = getattr(tab, "on", None)
                client = getattr(tab, "client", None)
                if callable(on):
                    async def _on_request(ev):
                        events_collector.append({"event": "Network.requestWillBeSent", "payload": ev})

                    async def _on_response(ev):
                        # Try to fetch response body when possible via CDP
                        payload = {"event": "Network.responseReceived", "payload": ev}
                        try:
                            req_id = ev.get("requestId") if isinstance(ev, dict) else None
                            if req_id and client is not None:
                                try:
                                    body_resp = await client.send("Network.getResponseBody", {"requestId": req_id})  # type: ignore
                                    payload["response_body"] = body_resp
                                except Exception:
                                    # Some servers or requests may not allow body retrieval
                                    payload["response_body"] = None
                        except Exception:
                            payload["response_body"] = None
                        events_collector.append(payload)

                    try:
                        # await registration coroutines
                        await on("Network.requestWillBeSent", _on_request)
                        await on("Network.responseReceived", _on_response)
                    except Exception:
                        logger.debug("tab.on exists but subscribing to events failed")
            except Exception:
                logger.debug("No tab.on event subscription available")

            # Navigate
            try:
                await tab.go_to(url)
            except Exception:
                # Some pydoll versions use navigate or goto
                try:
                    await tab.navigate(url)
                except Exception:
                    logger.debug("Navigation helpers missing or failed")

            # Wait a bit for the page to settle (best-effort)
            try:
                await tab.wait_for_network_idle(timeout=5)
            except Exception:
                logger.debug("wait_for_network_idle not available or timed out")

            # try screenshot
            try:
                screenshot_b64 = await tab.take_screenshot(as_base64=True)
            except Exception:
                logger.debug("take_screenshot not available")

            # Try to pull recorded events from known attributes
            try:
                recorded = getattr(tab, "recorded_events", None)
                if recorded is not None:
                    network_events = list(recorded)
                else:
                    get_rec = getattr(tab, "get_recorded_events", None)
                    if callable(get_rec):
                        maybe = await get_rec()
                        network_events = list(maybe or [])
                    else:
                        network_events = list(events_collector)
            except Exception:
                network_events = list(events_collector)

            # Best-effort form extraction: try to evaluate a small JS snippet to
            # serialize forms. Some pydoll versions expose `tab.eval` or similar.
            form_extractions = []
            try:
                eval_fn = getattr(tab, "eval", None) or getattr(tab, "evaluate", None)
                if callable(eval_fn):
                    js = (
                        "Array.from(document.forms).map(f => {"
                        "return {name: f.name || null, action: f.action || null, method: f.method || null, "
                        "fields: Array.from(f.elements).map(e => ({name: e.name || null, type: e.type || null, value: e.value || null}))}; })"
                    )
                    try:
                        res = await eval_fn(js, return_by_value=True)  # type: ignore
                        form_extractions = res or []
                    except Exception:
                        form_extractions = []
            except Exception:
                form_extractions = []

            # Captcha detection: look for <img> elements with likely captcha
            # indicators in id/class/src/alt/title. Save data URLs or fetch via
            # requests when possible.
            captchas: List[Dict] = []
            try:
                # Try JS-based discovery first
                js_find = (
                    "Array.from(document.images).map(i=>({src:i.src, id:i.id||null, class:i.className||null, alt:i.alt||null, title:i.title||null}))"
                )
                images = []
                try:
                    if callable(eval_fn):
                        images = await eval_fn(js_find, return_by_value=True)  # type: ignore
                except Exception:
                    images = []

                # heuristics
                for img in images or []:
                    src = img.get("src") if isinstance(img, dict) else None
                    if not src:
                        continue
                    meta_text = " ".join([str(img.get(k) or "") for k in ("id", "class", "alt", "title")])
                    if any(tok in (meta_text or "").lower() for tok in ("captcha", "recaptcha", "captchaimg")) or "captcha" in (src or ""):
                        # Save image: decode data: URI or fetch
                        storage_key = None
                        try:
                            if src.startswith("data:"):
                                header, b64 = src.split(",", 1)
                                b = base64.b64decode(b64)
                                p = self.output_dir / f"{trace_id}-captcha-{len(captchas)}.png"
                                p.write_bytes(b)
                                storage_key = str(p.name)
                            else:
                                # fetch with requests; cookies may be needed in some cases
                                import requests

                                try:
                                    rr = requests.get(src, timeout=15)
                                    if rr.status_code == 200:
                                        p = self.output_dir / f"{trace_id}-captcha-{len(captchas)}.png"
                                        p.write_bytes(rr.content)
                                        storage_key = str(p.name)
                                except Exception:
                                    storage_key = None
                        except Exception:
                            storage_key = None

                        captchas.append({"src": src, "storage_key": storage_key, "meta": img})
            except Exception:
                captchas = []

            # Build trace
            trace = {
                "trace_version": "1.0",
                "trace_id": trace_id,
                "capture_time": capture_time,
                "source": {"source_id": "pydoll-cdp", "source_name": "pydoll-cdp", "environment": "local"},
                "page_url": url,
                "browser": {"user_agent": user_agent or "pydoll", "browser_version": "unknown", "headless": True, "platform": "cdp"},
                "session": {"session_id": trace_id},
                "form_extractions": form_extractions,
                "events": network_events,
                "screenshots": [],
                "artifacts": {"raw_response_keys": {}},
                "metadata": {"capture_agent": "pydoll_cdp_discovery"},
                "audit": {"captchas": captchas, "solver_summary": {"total_attempts": 0, "successes": 0, "avg_latency_ms": 0}},
            }

            # save screenshot artifact if present
            if screenshot_b64:
                ss_path = self.output_dir / f"{trace_id}.png"
                try:
                    # try pydoll util first
                    try:
                        ss_bytes = pydoll.utils.decode_base64_to_bytes(screenshot_b64)  # type: ignore[attr-defined]
                    except Exception:
                        ss_bytes = base64.b64decode(screenshot_b64)
                    ss_path.write_bytes(ss_bytes)
                    trace["screenshots"].append({"screenshot_id": "ss-1", "timestamp": capture_time, "storage_key": str(ss_path.name)})
                except Exception:
                    logger.debug("Failed to write screenshot artifact")

            # persist trace
            trace_path = self.output_dir / f"{trace_id}.json"
            trace_path.write_text(json.dumps(trace, ensure_ascii=False, indent=2))
            return trace

    async def _requests_fallback(self, url: str, trace_id: str, capture_time: str) -> Dict:
        # Minimal requests-based capture to produce a canonical trace
        import requests

        try:
            r = requests.get(url, timeout=15)
            status = r.status_code
            headers = dict(r.headers)
            body = r.text[:20000]
        except Exception as exc:
            logger.debug("requests fallback failed: %s", exc)
            status = None
            headers = {}
            body = ""

        event = {
            "type": "http.response",
            "timestamp": capture_time,
            "request": {"method": "GET", "url": url},
            "response": {"status": status, "headers": headers, "body_snippet": body[:1000]},
        }

        # Parse forms with BeautifulSoup to extract input names/values
        form_extractions = []
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(body, "html.parser")
            for f in soup.find_all("form"):
                fields = []
                for inp in f.find_all(["input", "select", "textarea"]):
                    name = inp.get("name")
                    typ = inp.get("type") if inp.name == "input" else inp.name
                    val = inp.get("value") if inp.name == "input" else (inp.text or None)
                    fields.append({"name": name, "type": typ, "value": val})
                form_extractions.append({"name": f.get("name"), "action": f.get("action"), "method": f.get("method"), "fields": fields})
        except Exception:
            form_extractions = []

        # Detect captcha images in the requests fallback
        captchas = []
        try:
            from bs4 import BeautifulSoup
            import requests as _requests

            soup = BeautifulSoup(body, "html.parser")
            imgs = soup.find_all("img")
            for i, img in enumerate(imgs):
                src = img.get("src")
                meta = " ".join([str(img.get("id") or ""), str(img.get("class") or ""), str(img.get("alt") or "")])
                if src and ("captcha" in (meta or "").lower() or "captcha" in src.lower()):
                    storage_key = None
                    try:
                        if src.startswith("data:"):
                            header, b64 = src.split(",", 1)
                            b = base64.b64decode(b64)
                            p = self.output_dir / f"{trace_id}-captcha-{i}.png"
                            p.write_bytes(b)
                            storage_key = str(p.name)
                        else:
                            try:
                                r2 = _requests.get(src, timeout=15)
                                if r2.status_code == 200:
                                    p = self.output_dir / f"{trace_id}-captcha-{i}.png"
                                    p.write_bytes(r2.content)
                                    storage_key = str(p.name)
                            except Exception:
                                storage_key = None
                    except Exception:
                        storage_key = None
                    captchas.append({"src": src, "storage_key": storage_key, "meta": {"attrs": img.attrs}})
        except Exception:
            captchas = []

        trace = {
            "trace_version": "1.0",
            "trace_id": trace_id,
            "capture_time": capture_time,
            "source": {"source_id": "requests-fallback", "source_name": "requests-fallback", "environment": "local"},
            "page_url": url,
            "browser": None,
            "session": {"session_id": trace_id},
            "form_extractions": form_extractions,
            "events": [event],
            "screenshots": [],
            "artifacts": {"raw_response_keys": {}},
            "metadata": {"capture_agent": "requests_fallback"},
            "audit": {"captchas": captchas},
        }

        trace_path = self.output_dir / f"{trace_id}.json"
        trace_path.write_text(json.dumps(trace, ensure_ascii=False, indent=2))
        return trace
