"""CDP harvester for Compras Públicas (SERCOP).

Flow:
- Use existing PydollCDPDiscovery to perform a CDP capture (render page & run JS).
- Read the saved HTML snapshot and parse the results table from the rendered DOM.
- Write `results.jsonl` with the first N rows (default 10) into `out_dir`.
- For the first M rows (default 3), follow detail links and attempt to download attached documents.

Notes:
- This script requires `pydoll` to be installed and local Chrome available.
- It is conservative in parsing; if selectors differ we fall back to heuristics.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup

try:
    from rag.discovery.pydoll_cdp_discovery import PydollCDPDiscovery, PydollNotInstalled
except Exception:
    PydollCDPDiscovery = None  # type: ignore
    PydollNotInstalled = RuntimeError


DEFAULT_URL = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/PC/buscarProceso.cpe?sg=1"


async def capture(url: str, out_dir: str | Path) -> dict:
    if PydollCDPDiscovery is None:
        raise PydollNotInstalled("Pydoll not installed or import failed")
    d = PydollCDPDiscovery(output_dir=str(out_dir))
    trace = await d.capture_trace(url)
    return trace


def parse_rows_from_html(html: str, base_url: str) -> List[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows: List[dict] = []

    # Heuristic 1: find links that look like process detail
    for a in soup.find_all("a", href=True):
        href = a["href"]
        txt = a.get_text(strip=True)
        if not txt:
            continue
        if re.search(r"verProceso|detalle|verProceso|idProceso|/ProcesoContratacion/", href, re.I) or re.search(r"proceso|detalle", txt, re.I):
            rows.append({"title": txt, "href": href})

    # Heuristic 2: find result tables with many rows
    if not rows:
        tables = soup.find_all("table")
        for t in tables:
            trs = t.find_all("tr")
            for tr in trs:
                tds = tr.find_all("td")
                if len(tds) >= 2:
                    txt = " | ".join(td.get_text(strip=True) for td in tds)
                    # try to find a link inside the row
                    a = tr.find("a", href=True)
                    href = a["href"] if a else None
                    rows.append({"title": txt, "href": href})

    # Normalize hrefs to absolute where possible
    from urllib.parse import urljoin

    norm_rows: List[dict] = []
    for r in rows:
        href = r.get("href")
        if href:
            abs_href = urljoin(base_url, href)
        else:
            abs_href = None
        norm_rows.append({"title": r.get("title"), "href": abs_href})
    return norm_rows


def save_results(out_dir: Path, trace_id: str, rows: List[dict], limit: int = 10) -> Path:
    out = out_dir
    out.mkdir(parents=True, exist_ok=True)
    results_file = out / f"{trace_id}.results.jsonl"
    with results_file.open("w", encoding="utf-8") as fh:
        for i, r in enumerate(rows[:limit]):
            rec = {"trace_id": trace_id, "rank": i + 1, "title": r.get("title"), "href": r.get("href")}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return results_file


def download_documents(rows: List[dict], out_dir: Path, sample_n: int = 3) -> List[dict]:
    import requests

    saved = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, r in enumerate(rows[:sample_n]):
        href = r.get("href")
        if not href:
            saved.append({"rank": i + 1, "href": None, "docs": []})
            continue
        try:
            # fetch the detail page HTML
            resp = requests.get(href, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            docs = []
            for a in soup.find_all("a", href=True):
                link = a["href"]
                if re.search(r"\.pdf$|\.zip$|\.docx?$|\.xlsx?$", link, re.I):
                    from urllib.parse import urljoin

                    abs_link = urljoin(href, link)
                    fn = abs_link.split("/")[-1].split("?")[0]
                    save_path = out_dir / f"{i+1}__{fn}"
                    try:
                        r2 = requests.get(abs_link, timeout=60)
                        if r2.status_code == 200 and r2.content:
                            save_path.write_bytes(r2.content)
                            docs.append(str(save_path.name))
                    except Exception:
                        continue
            saved.append({"rank": i + 1, "href": href, "docs": docs})
        except Exception as e:
            saved.append({"rank": i + 1, "href": href, "docs": [], "error": str(e)})
    return saved


def main(url: str = DEFAULT_URL, out_dir: str | Path = "rag/discovery/out_cdp", dry_n: int = 10, sample_docs_n: int = 3) -> int:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    try:
        trace = asyncio.run(capture(url, out_path))
    except Exception as e:
        print("CDP capture failed:", e)
        return 2

    trace_id = trace.get("trace_id") or trace.get("session", {}).get("session_id") or "trace"
    # locate HTML snapshot
    html_path = None
    if trace.get("artifacts") and trace["artifacts"].get("html_snapshot_path"):
        html_path = out_path / trace["artifacts"]["html_snapshot_path"]
    # fallback: find newest .html in out_dir
    if not html_path or not html_path.exists():
        htmls = sorted(out_path.glob("*.html"), key=lambda p: p.stat().st_mtime)
        if htmls:
            html_path = htmls[-1]

    if not html_path or not html_path.exists():
        print("No HTML snapshot found to parse")
        return 3

    html = html_path.read_text(encoding="utf-8")
    rows = parse_rows_from_html(html, base_url=url)
    print(f"Parsed {len(rows)} candidate rows from rendered DOM")

    # Fallback: inspect the saved trace for XHR JSON payloads that may
    # contain the process listings (simpler, flatter logic to avoid deep
    # nested try/excepts which caused syntax issues).
    if len(rows) < dry_n:
        trace_path = out_path / f"{trace_id}.json"
        if trace_path.exists():
            try:
                trace_blob = json.loads(trace_path.read_text(encoding="utf-8"))
                events = trace_blob.get("events", []) or []
            except Exception:
                events = []

            for ev in events:
                try:
                    payload = None
                    if isinstance(ev, dict):
                        pv = ev.get("payload")
                        if isinstance(pv, dict):
                            payload = pv.get("response_body") or pv.get("body")
                        if not payload:
                            payload = ev.get("response_body") or ev.get("body")

                    if not payload:
                        continue

                    if isinstance(payload, dict):
                        payload = payload.get("body") or payload.get("base64") or None
                    if isinstance(payload, bytes):
                        payload = payload.decode("utf-8", errors="ignore")
                    if not isinstance(payload, str):
                        continue

                    # find a JSON-like substring
                    txt = payload.strip()
                    m = re.search(r"(\{.*?\}|\[.*?\])", txt, re.S)
                    if not m:
                        # try callback wrapper
                        m2 = re.search(r"\((\{.*\}|\[.*\])\)", txt, re.S)
                        if not m2:
                            continue
                        json_text = m2.group(1)
                    else:
                        json_text = m.group(1)

                    try:
                        maybe = json.loads(json_text)
                    except Exception:
                        continue

                    candidates = []
                    if isinstance(maybe, dict):
                        for key in ("lista", "Lista", "procesos", "Procesos", "data", "d", "result", "resultados", "rows"):
                            val = maybe.get(key)
                            if isinstance(val, list) and val:
                                candidates = val
                                break
                    elif isinstance(maybe, list):
                        candidates = maybe

                    for item in candidates:
                        title = None
                        href = None
                        if isinstance(item, dict):
                            for tkey in ("titulo", "tituloProceso", "nombre", "descripcion", "nombreProceso", "proceso", "title"):
                                if item.get(tkey):
                                    title = str(item.get(tkey))
                                    break
                            for hkey in ("url", "link", "detalle", "href", "enlace", "file", "archivo"):
                                if item.get(hkey):
                                    href = item.get(hkey)
                                    break
                            if not href and item.get("idProceso"):
                                href = f"/ProcesoContratacion/compras/PC/detalleProceso.cpe?idProceso={item.get('idProceso')}"
                        else:
                            title = str(item)

                        if title or href:
                            from urllib.parse import urljoin
                            rows.append({"title": title or "", "href": urljoin(url, href) if href else None})

                except Exception:
                    # continue with next event on any parse error
                    continue

    # final count
    print(f"Total candidate rows after XHR-inspection: {len(rows)}")

    results_file = save_results(out_path, trace_id, rows, limit=dry_n)
    print("Wrote results to", results_file)

    docs_out_dir = out_path / f"{trace_id}-docs"
    docs_report = download_documents(rows, docs_out_dir, sample_n=sample_docs_n)
    print("Downloaded docs for sample rows, report:")
    print(json.dumps(docs_report, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
