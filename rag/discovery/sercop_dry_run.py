#!/usr/bin/env python3
"""SERCOP dry-run harvester (requests-only).

- Submits the main search form with default values.
- Follows the JavaScript redirect returned by the POST response.
- Fetches the results page with cookies preserved.
- Extracts result rows and writes `results.jsonl` into the out_dir.
- Saves the HTML snapshot for reproducibility.

This is intentionally conservative; use CDP runner for JS-heavy flows.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup


DEFAULT_URL = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/PC/buscarProceso.cpe?sg=1"


def submit_search(session: requests.Session, url: str) -> requests.Response:
    r = session.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    form = soup.find("form")
    if not form:
        raise RuntimeError("No form found on page")

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
    action = form.get("action") or ""
    action = requests.compat.urljoin(url, action)

    if method == "post":
        resp = session.post(action, data=data, timeout=30)
    else:
        resp = session.get(action, params=data, timeout=30)
    resp.raise_for_status()
    return resp


def extract_js_redirect(html: str) -> str | None:
    # look for window.parent.location or location= assignment
    m = re.search(r"window\.parent\.location\s*=\s*['\"]([^'\"]+)['\"]", html)
    if m:
        return m.group(1)
    m = re.search(r"location\s*=\s*['\"]([^'\"]+)['\"]", html)
    if m:
        return m.group(1)
    return None


def fetch_results(session: requests.Session, redirect_url: str, referer: str) -> requests.Response:
    # If redirect is protocol-relative (//host/path), add https:
    if redirect_url.startswith("//"):
        redirect_url = "https:" + redirect_url
    elif redirect_url.startswith("/"):
        # relative path
        from urllib.parse import urljoin

        redirect_url = urljoin(referer, redirect_url)

    headers = {"Referer": referer, "User-Agent": "YACHAQ-LEX/1.0"}
    r = session.get(redirect_url, headers=headers, timeout=30)
    r.raise_for_status()
    return r


def parse_results_table(html: str) -> List[dict]:
    soup = BeautifulSoup(html, "html.parser")
    # Heuristic: find the results table by finding table rows with links to process detail
    rows = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "verProceso" in href or "detalle" in href or "verProceso" in a.get_text():
            row = {"text": a.get_text(strip=True), "href": href}
            rows.append(row)
    # fallback: find table rows
    if not rows:
        for tr in soup.find_all("tr"):
            t = [td.get_text(strip=True) for td in tr.find_all("td")]
            if t:
                rows.append({"cells": t})
    return rows


def main(url: str = DEFAULT_URL, out_dir: str | Path = "rag/discovery/out_cdp") -> int:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    try:
        post_resp = submit_search(session, url)
    except Exception as e:
        print("submit failed:", e)
        return 2

    redirect = extract_js_redirect(post_resp.text)
    if not redirect:
        # if server responded with a direct HTML results page, use it
        results_html = post_resp.text
    else:
        try:
            res = fetch_results(session, redirect, post_resp.url)
            results_html = res.text
        except Exception as e:
            print("fetch results failed:", e)
            return 3

    # persist html snapshot
    import uuid

    tid = str(uuid.uuid4())
    (out / f"{tid}.html").write_text(results_html, encoding="utf-8")

    rows = parse_results_table(results_html)
    jsnlines = []
    for r in rows:
        entry = {"harvest_id": tid, "row": r}
        jsnlines.append(entry)

    out_file = out / f"{tid}.results.jsonl"
    with out_file.open("w", encoding="utf-8") as fh:
        for e in jsnlines:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")

    print("Wrote", len(jsnlines), "rows to", out_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())