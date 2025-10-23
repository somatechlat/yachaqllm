#!/usr/bin/env python3
"""Fetch the SERCOP search page and save the explicit captcha image to disk.

Writes files under `rag/discovery/out_sercop_run/`:
- <uuid>.html
- captchas/<uuid>-captcha.png

Prints the captcha path on success.
"""
from __future__ import annotations

import datetime
import json
import sys
import uuid
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


DEFAULT_URL = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/PC/buscarProceso.cpe?sg=1"


def main(url: str = DEFAULT_URL, out_dir: str = "rag/discovery/out_sercop_run") -> int:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    captchas_dir = out / "captchas"
    captchas_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    try:
        r = session.get(url, timeout=15)
        r.raise_for_status()
    except Exception as exc:
        print("Failed to GET search page:", exc)
        return 2

    tid = str(uuid.uuid4())
    html_path = out / f"{tid}.html"
    html_path.write_text(r.text or "", encoding="utf-8")

    soup = BeautifulSoup(r.text, "html.parser")
    # Find captcha image - common src contains 'generadorCaptcha'
    img = None
    for im in soup.find_all("img"):
        src = im.get("src") or ""
        if "generadorCaptcha" in src or "captcha" in src.lower():
            img = src
            break

    captcha_path = None
    if img:
        captcha_url = urljoin(url, img)
        try:
            r2 = session.get(captcha_url, timeout=15)
            r2.raise_for_status()
            # derive filename
            fn = f"{tid}-captcha.png"
            p = captchas_dir / fn
            p.write_bytes(r2.content)
            captcha_path = str(p)
        except Exception as exc:
            print("Failed to download captcha image:", exc)

    trace = {
        "trace_version": "1.0",
        "trace_id": tid,
        "capture_time": datetime.datetime.utcnow().isoformat() + "Z",
        "page_url": url,
        "session": {"session_id": tid},
        "form_extractions": [],
        "artifacts": {"html": str(html_path.name), "captcha": captcha_path},
        "cookies": session.cookies.get_dict(),
    }

    (out / f"{tid}.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")

    if captcha_path:
        print(captcha_path)
        return 0
    else:
        print("No captcha image found on the page; saved HTML to", str(html_path))
        return 3


if __name__ == "__main__":
    sys.exit(main())
