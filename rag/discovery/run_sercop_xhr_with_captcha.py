#!/usr/bin/env python3
"""Replay SERCOP AJAX using saved trace cookies and a solved captcha.

Usage: .venv/bin/python3 rag/discovery/run_sercop_xhr_with_captcha.py <captcha_text> [trace_json]

If trace_json is omitted, the script picks the newest JSON under rag/discovery/out_sercop_run/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


OUT_RUN = Path("rag/discovery/out_sercop_run")
OUT_CDP = Path("rag/discovery/out_cdp")
AJAX_URL = "https://www.compraspublicas.gob.ec/ProcesoContratacion/servicio/interfazWeb.php"


def load_trace(trace_path: Path) -> dict:
    return json.loads(trace_path.read_text(encoding="utf-8"))


def extract_form_fields(html_path: Path) -> dict:
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    fields = {}
    if not form:
        return fields
    for inp in form.find_all(["input", "select", "textarea"]):
        name = inp.get("name")
        if not name:
            continue
        if inp.name == "input":
            fields[name] = inp.get("value", "")
        elif inp.name == "select":
            opt = inp.find("option")
            fields[name] = opt.get("value") if (opt and opt.get("value")) else (opt.text if opt else "")
        else:
            fields[name] = inp.text or ""
    return fields


def post_listing(session: requests.Session, fields: dict, captcha_text: str) -> tuple[int, str]:
    # inject captcha and pagination
    fields = dict(fields)
    fields["image"] = captcha_text
    fields["captccc2"] = fields.get("captccc2", "1")
    fields["paginaActual"] = fields.get("paginaActual", "0")
    # ensure registroxPagina present
    fields["registroxPagina"] = fields.get("registroxPagina", 20)

    # Serialize fields as Prototype/Form.serialize would (simple key=value&...)
    from urllib.parse import quote_plus

    data_str = "&".join(f"{quote_plus(str(k))}={quote_plus(str(v))}" for k, v in fields.items())

    post_payload = {
        "data": data_str,
        "clazz": "SolicitudCompra",
        "action": "buscarProcesoxEntidad",
    }

    headers = {
        "User-Agent": "yachaq-lex-scraper/1.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "X-Prototype-Version": "1.7",
        "Referer": "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/PC/buscarProceso.cpe?sg=1",
    }

    resp = session.post(AJAX_URL, headers=headers, data=post_payload, timeout=30)
    return resp.status_code, resp.text


def extract_rows_from_json(js) -> list:
    rows = []
    if not js:
        return rows
    if isinstance(js, dict):
        for key in ("lista", "Lista", "procesos", "Procesos", "data", "d", "result", "rows"):
            if key in js and isinstance(js[key], list):
                js = js[key]
                break
    if isinstance(js, list):
        for item in js:
            if isinstance(item, dict):
                title = item.get("c") or item.get("titulo") or item.get("nombre") or item.get("r")
                href = None
                if item.get("i"):
                    href = f"https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/PC/informacionProcesoContratacion.cpe?idSoliCompra={item.get('i')}"
                rows.append({"title": title, "href": href, "raw": item})
            else:
                rows.append({"title": str(item), "href": None, "raw": item})
    return rows


def save_results(trace_id: str, rows: list):
    OUT_CDP.mkdir(parents=True, exist_ok=True)
    out_file = OUT_CDP / f"{trace_id}.xhr.results.jsonl"
    with out_file.open("w", encoding="utf-8") as fh:
        for i, r in enumerate(rows[:100]):
            rec = {"trace_id": trace_id, "rank": i + 1, "title": r.get("title"), "href": r.get("href"), "raw": r.get("raw")}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return out_file


def download_docs(rows: list, trace_id: str, sample_n: int = 3) -> list:
    OUT_CDP.mkdir(parents=True, exist_ok=True)
    docs_dir = OUT_CDP / f"{trace_id}-docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    import requests as rq

    saved = []
    for i, r in enumerate(rows[:sample_n]):
        href = r.get("href")
        if not href:
            saved.append({"rank": i + 1, "href": None, "docs": []})
            continue
        try:
            resp = rq.get(href, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            docs = []
            for a in soup.find_all("a", href=True):
                link = a["href"]
                if link.lower().endswith(('.pdf', '.zip', '.doc', '.docx', '.xls', '.xlsx')):
                    abs_link = urljoin(href, link)
                    fn = abs_link.split("/")[-1].split("?")[0]
                    path = docs_dir / f"{i+1}__{fn}"
                    try:
                        r2 = rq.get(abs_link, timeout=60)
                        if r2.status_code == 200 and r2.content:
                            path.write_bytes(r2.content)
                            docs.append(str(path.name))
                    except Exception:
                        continue
            saved.append({"rank": i + 1, "href": href, "docs": docs})
        except Exception as e:
            saved.append({"rank": i + 1, "href": href, "docs": [], "error": str(e)})
    return saved


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: run_sercop_xhr_with_captcha.py <captcha_text> [trace_json]")
        return 2
    captcha = argv[0]
    trace_path = Path(argv[1]) if len(argv) > 1 else None
    if not trace_path:
        traces = sorted(OUT_RUN.glob("*.json"), key=lambda p: p.stat().st_mtime)
        if not traces:
            print("No traces found in", OUT_RUN)
            return 3
        trace_path = traces[-1]

    trace = load_trace(trace_path)
    cookies = trace.get("cookies") or {}
    html_name = trace.get("artifacts", {}).get("html") or trace_path.with_suffix('.html').name
    html_path = trace_path.parent / html_name
    if not html_path.exists():
        print("HTML snapshot not found for trace", trace_path)
        return 4

    fields = extract_form_fields(html_path)
    # merge any fallback defaults
    fields.setdefault('captccc2', '1')
    fields.setdefault('paginaActual', '0')
    fields.setdefault('registroxPagina', 20)

    session = requests.Session()
    session.cookies.update(cookies)

    status, text = post_listing(session, fields, captcha)
    print("XHR POST status:", status)

    js = None
    try:
        js = json.loads(text)
    except Exception:
        # try to extract a JSON substring
        import re
        m = re.search(r"(\{.*\}|\[.*\])", text, re.S)
        if m:
            try:
                js = json.loads(m.group(1))
            except Exception:
                js = None

    rows = extract_rows_from_json(js)
    print(f"Extracted {len(rows)} rows")
    trace_id = trace.get('trace_id') or trace_path.stem
    results_file = save_results(trace_id, rows)
    docs_report = []
    if rows:
        docs_report = download_docs(rows, trace_id, sample_n=3)
    print("Wrote results to", results_file)
    print("Docs report:", json.dumps(docs_report, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
