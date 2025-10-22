"""XHR-replay harvester for Compras Públicas (SERCOP).

This script performs the same ajax_call used by the site's JavaScript by
POSTing to the server endpoint with the appropriate 'clazz' and 'action'
parameters. It attempts to reproduce the 'buscarProcesoxEntidadCount' and
'buscarProcesoxEntidad' calls to fetch structured JSON results so we can
extract the first N rows without launching a browser.

Usage: run as a script. Writes results under `rag/discovery/out_cdp` by
default.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import List

import requests

DEFAULT_URL = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/PC/buscarProceso.cpe?sg=1"


def build_headers() -> dict:
    return {
        "User-Agent": os.environ.get("USER_AGENT", "yachaq-lex-scraper/1.0"),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
    }


def extract_rows_from_json(resp_json) -> List[dict]:
    rows = []
    if not resp_json:
        return rows
    # Response from buscarProcesoxEntidad is often an array-like structure
    # where each item has fields used by the client: c (code), i (id), v (version), r (entity), d (description), etc.
    if isinstance(resp_json, dict):
        # Sometimes the JSON is wrapped: look for common keys
        for key in ("lista", "Lista", "procesos", "Procesos", "data", "d", "result", "rows"):
            if key in resp_json and isinstance(resp_json[key], list):
                resp_json = resp_json[key]
                break

    if isinstance(resp_json, list):
        for item in resp_json:
            if isinstance(item, dict):
                title = item.get("c") or item.get("titulo") or item.get("nombre") or item.get("r")
                href = None
                if item.get("i"):
                    href = f"https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/PC/informacionProcesoContratacion.cpe?idSoliCompra={item.get('i')}"
                rows.append({"title": title, "href": href, "raw": item})
            else:
                rows.append({"title": str(item), "href": None, "raw": item})
    return rows


def save_results(out_dir: Path, trace_id: str, rows: List[dict], limit: int = 10) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    results_file = out_dir / f"{trace_id}.results.jsonl"
    with results_file.open("w", encoding="utf-8") as fh:
        for i, r in enumerate(rows[:limit]):
            rec = {"trace_id": trace_id, "rank": i + 1, "title": r.get("title"), "href": r.get("href"), "raw": r.get("raw")}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return results_file


def download_documents(rows: List[dict], out_dir: Path, sample_n: int = 3) -> List[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for i, r in enumerate(rows[:sample_n]):
        href = r.get("href")
        if not href:
            saved.append({"rank": i + 1, "href": None, "docs": []})
            continue
        try:
            resp = requests.get(href, timeout=30)
            resp.raise_for_status()
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(resp.text, "html.parser")
            docs = []
            for a in soup.find_all("a", href=True):
                link = a["href"]
                if any(link.lower().endswith(ext) for ext in (".pdf", ".zip", ".doc", ".docx", ".xls", ".xlsx")):
                    from urllib.parse import urljoin

                    abs_link = urljoin(href, link)
                    fn = abs_link.split("/")[-1].split("?")[0]
                    path = out_dir / f"{i+1}__{fn}"
                    try:
                        r2 = requests.get(abs_link, timeout=60)
                        if r2.status_code == 200 and r2.content:
                            path.write_bytes(r2.content)
                            docs.append(str(path.name))
                    except Exception:
                        continue
            saved.append({"rank": i + 1, "href": href, "docs": docs})
        except Exception as e:
            saved.append({"rank": i + 1, "href": href, "docs": [], "error": str(e)})
    return saved


def main(url: str = DEFAULT_URL, out_dir: str | Path = "rag/discovery/out_cdp", dry_n: int = 10, sample_docs_n: int = 3) -> int:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    headers = build_headers()

    # Attempt to reuse any prior requests-fallback trace which may include
    # serialized form fields and Set-Cookie headers. This increases the
    # chance of a valid server-side session and correct csrf_token.
    trace_id = "xhr-dryrun"
    fallback_dir = Path("rag/discovery/out_sercop_run")
    if fallback_dir.exists():
        traces = sorted(fallback_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
        if traces:
            latest = traces[-1]
            try:
                t = json.loads(latest.read_text(encoding="utf-8"))
                # pull form_extractions if available
                fe = (t.get("form_extractions") or [])
                if fe:
                    f0 = fe[0]
                    fields = f0.get("fields") or []
                    # convert list of {name,value} to payload dict
                    payload = {item.get("name"): item.get("value") for item in fields if item.get("name")}
                    trace_id = latest.stem
                # extract cookies from events Set-Cookie headers
                cookies = {}
                for ev in (t.get("events") or []):
                    try:
                        hdrs = ev.get("response", {}).get("headers", {})
                        sc = hdrs.get("Set-Cookie") or hdrs.get("set-cookie")
                        if sc:
                            # may contain multiple cookies separated by comma; split and parse name=value
                            parts = [p.strip() for p in sc.split(',') if '=' in p]
                            for part in parts:
                                nv = part.split(';', 1)[0].strip()
                                if '=' in nv:
                                    k, v = nv.split('=', 1)
                                    cookies[k] = v
                    except Exception:
                        continue
                if cookies:
                    session.cookies.update(cookies)
            except Exception:
                pass
    else:
        # Initial GET to obtain cookies and any hidden form fields
        try:
            r0 = session.get(url, headers={"User-Agent": headers.get("User-Agent")}, timeout=15)
            r0.raise_for_status()
            trace_id = r0.headers.get("X-Trace-Id") or "xhr-dryrun"
        except Exception:
            trace_id = "xhr-dryrun"

    # Build a minimal form payload. We reuse common defaults; the site supports many fields but most are optional.
    # Setting paginaActual=0 and registroxPagina=20 to fetch the first page.
    payload = {
        "paginaActual": 0,
        "registroxPagina": 20,
        # include other fields if known; leaving empty values should be acceptable
        "txtPalabrasClaves": "",
        "cmbEntidad": "",
        "cmbEstado": "",
        "captc": "",
    }

    # First, call the count endpoint to mimic site behavior (not strictly necessary)
    try:
        session.post(url, headers=headers, data={"data": "", "clazz": "SolicitudCompra", "action": "buscarProcesoxEntidadCount"}, timeout=30)
    except Exception:
        pass

    # Now call buscarProcesoxEntidad which returns the list
    try:
        # The site's ajax_call serializes the form (Form.serialize). We'll send our payload as form-encoded 'data'
        data_str = "&".join(f"{k}={v}" for k, v in payload.items())
        resp = session.post(url, headers=headers, data={"data": data_str, "clazz": "SolicitudCompra", "action": "buscarProcesoxEntidad"}, timeout=30)
        text = resp.text
        try:
            js = resp.json()
        except Exception:
            # try to extract JSON from response text
            import re

            m = re.search(r"(\{.*\}|\[.*\])", text, re.S)
            if m:
                try:
                    js = json.loads(m.group(1))
                except Exception:
                    js = None
            else:
                js = None
    except Exception as e:
        print("XHR request failed:", e)
        return 2

    rows = extract_rows_from_json(js)
    print(f"Extracted {len(rows)} rows from XHR response")

    results_file = save_results(out_path, trace_id, rows, limit=dry_n)
    print("Wrote results to", results_file)

    docs_out_dir = out_path / f"{trace_id}-docs"
    docs_report = download_documents(rows, docs_out_dir, sample_n=sample_docs_n)
    print("Downloaded docs for sample rows, report:")
    print(json.dumps(docs_report, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
