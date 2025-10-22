"""Harvest from the latest CDP snapshot in out_cdp.

- Finds the newest `.html` under `rag/discovery/out_cdp`.
- Parses the DOM, extracts candidate rows (title + href), writes `snapshot.results.jsonl`.
- Downloads documents for the first 3 rows into `<trace_id>-docs/`.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup


OUT_DIR = Path("rag/discovery/out_cdp")


def find_latest_html(out_dir: Path) -> Path | None:
    htmls = sorted(out_dir.glob("*.html"), key=lambda p: p.stat().st_mtime)
    return htmls[-1] if htmls else None


def parse_rows(html: str, base_url: str) -> List[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        txt = a.get_text(strip=True)
        if not txt:
            continue
        if re.search(r"verProceso|detalle|verProceso|idProceso|/ProcesoContratacion/", href, re.I) or re.search(r"proceso|detalle", txt, re.I):
            rows.append({"title": txt, "href": href})
    if not rows:
        for tr in soup.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 2:
                txt = " | ".join(td.get_text(strip=True) for td in tds)
                a = tr.find("a", href=True)
                href = a["href"] if a else None
                rows.append({"title": txt, "href": href})
    # normalize
    from urllib.parse import urljoin

    norm = []
    for r in rows:
        href = r.get("href")
        if href:
            abs_href = urljoin(base_url, href)
        else:
            abs_href = None
        norm.append({"title": r.get("title"), "href": abs_href})
    return norm


def save_results(out_dir: Path, trace_id: str, rows: List[dict], limit: int = 10) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    f = out_dir / f"{trace_id}.snapshot.results.jsonl"
    with f.open("w", encoding="utf-8") as fh:
        for i, r in enumerate(rows[:limit]):
            fh.write(json.dumps({"trace_id": trace_id, "rank": i + 1, "title": r.get("title"), "href": r.get("href")}, ensure_ascii=False) + "\n")
    return f


def download_docs(rows: List[dict], out_dir: Path, sample_n: int = 3) -> List[dict]:
    import requests

    saved = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, r in enumerate(rows[:sample_n]):
        href = r.get("href")
        if not href:
            saved.append({"rank": i + 1, "href": None, "docs": []})
            continue
        try:
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


def main():
    out_dir = OUT_DIR
    html_path = find_latest_html(out_dir)
    if not html_path:
        print("No HTML snapshot found in", out_dir)
        return 2
    html = html_path.read_text(encoding="utf-8")
    rows = parse_rows(html, base_url="https://www.compraspublicas.gob.ec")
    print("Found", len(rows), "candidate rows in snapshot")
    # derive trace_id from html filename
    trace_id = html_path.stem
    res_file = save_results(out_dir, trace_id, rows, limit=10)
    print("Saved results to", res_file)
    docs_dir = out_dir / f"{trace_id}-docs"
    docs_report = download_docs(rows, docs_dir, sample_n=3)
    print("Docs report:")
    print(json.dumps(docs_report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
