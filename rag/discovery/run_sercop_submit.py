#!/usr/bin/env python3
"""Submit the first form on the SERCOP search page and save a canonical trace.

This helper uses requests+BeautifulSoup and is intended for quick local runs
to trigger search submissions (and captcha exposure) without needing a
browser. It writes a trace JSON and any detected captcha images into the
output directory.
"""
from __future__ import annotations

import base64
import datetime
import json
import sys
import uuid
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def main(url: str, out_dir: str = "rag/discovery/out_sercop_run") -> int:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    try:
        r = requests.get(url, timeout=15)
    except Exception as exc:
        print("Failed to GET url:", exc)
        return 2

    soup = BeautifulSoup(r.text, "html.parser")
    form = soup.find("form")
    if not form:
        print("No form found on page; nothing to submit")
        return 0

    # Collect fields (including hidden inputs)
    data = {}
    for inp in form.find_all(["input", "select", "textarea"]):
        name = inp.get("name")
        if not name:
            continue
        if inp.name == "input":
            data[name] = inp.get("value", "")
        elif inp.name == "select":
            opt = inp.find("option")
            data[name] = opt.get("value") if (opt and opt.get("value")) else (opt.text if opt else "")
        else:
            data[name] = inp.text or ""

    method = (form.get("method") or "get").lower()
    action = urljoin(url, form.get("action") or "")

    print("Submitting form to:", action, "method:", method, "fields:", list(data.keys()))

    try:
        if method == "post":
            resp = requests.post(action, data=data, timeout=20)
        else:
            resp = requests.get(action, params=data, timeout=20)
    except Exception as exc:
        print("Form submit failed:", exc)
        return 3

    # Build trace identifiers and save full HTML snapshot for reproducible post-processing
    tid = str(uuid.uuid4())
    captime = datetime.datetime.now(datetime.timezone.utc).isoformat()
    body = resp.text or ""

    try:
        html_path = out / f"{tid}.html"
        html_path.write_text(body or "", encoding="utf-8")
    except Exception:
        pass

    # Best-effort: postprocess saved HTML with Crawl4AI
    try:
        from rag.discovery.postprocess_with_crawl4ai import run_on_file as _run_on_file

        _run_on_file(str(html_path))
    except Exception:
        pass

    captchas = []
    imgs = BeautifulSoup(body, "html.parser").find_all("img")
    for idx, img in enumerate(imgs):
        src = img.get("src")
        meta = " ".join([str(img.get("id") or ""), str(img.get("class") or ""), str(img.get("alt") or "")])
        if not src:
            continue
        if "captcha" in meta.lower() or "captcha" in src.lower():
            storage_key = None
            p = None
            try:
                if src.startswith("data:"):
                    header, b64 = src.split(",", 1)
                    b = base64.b64decode(b64)
                    p = out / f"{tid}-captcha-{idx}.png"
                    p.write_bytes(b)
                    storage_key = str(p.name)
                else:
                    r2 = requests.get(urljoin(action, src), timeout=15)
                    if r2.status_code == 200:
                        p = out / f"{tid}-captcha-{idx}.png"
                        p.write_bytes(r2.content)
                        storage_key = str(p.name)
            except Exception:
                storage_key = None

            # Emit human-first manifest entry for this captcha (best-effort)
            try:
                from rag.captcha.human_adapter import prepare_task

                fd = data or {}
                cookies = resp.cookies.get_dict() if hasattr(resp, 'cookies') else {}
                captcha_bytes = p.read_bytes() if (p is not None and p.exists()) else b""
                prepare_task(form_defaults=fd if isinstance(fd, dict) else {}, cookies=cookies, captcha_bytes=captcha_bytes, captcha_src=src, referer=action, search_url=url)
            except Exception:
                pass

            captchas.append({"src": src, "storage_key": storage_key, "meta": dict(img.attrs)})

    trace = {
        "trace_version": "1.0",
        "trace_id": tid,
        "capture_time": captime,
        "source": {"source_id": "requests-fallback", "source_name": "requests-fallback", "environment": "local"},
        "page_url": action,
        "browser": None,
        "session": {"session_id": tid},
        "form_extractions": [{"name": form.get("name"), "action": form.get("action"), "method": form.get("method"), "fields": [{"name": k, "value": v} for k, v in data.items()]}],
        "events": [{"type": "http.response", "timestamp": captime, "request": {"method": method.upper(), "url": action}, "response": {"status": resp.status_code, "headers": dict(resp.headers), "body_snippet": body[:1000]}}],
        "screenshots": [],
        "artifacts": {"raw_response_keys": {}},
        "metadata": {"capture_agent": "requests_fallback_form_submit"},
        "audit": {"captchas": captchas},
    }

    (out / f"{tid}.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2))
    print("Wrote trace", tid, "to", out)
    return 0


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/PC/buscarProceso.cpe?sg=1"
    sys.exit(main(url))
