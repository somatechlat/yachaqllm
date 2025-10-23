#!/usr/bin/env python3
"""Run a CDP-driven submit on SERCOP, injecting a provided captcha value.

Usage: .venv/bin/python3 rag/discovery/run_sercop_cdp_with_captcha.py <captcha_text>

Saves outputs under `rag/discovery/out_cdp/`:
- <trace_id>.html
- <trace_id>.results.jsonl
- <trace_id>-docs/ (downloaded attachments)
"""
from __future__ import annotations

import asyncio
import json
import sys
import uuid
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup


DEFAULT_URL = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/PC/buscarProceso.cpe?sg=1"


def parse_rows_from_html(html: str, base_url: str) -> List[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        txt = a.get_text(strip=True)
        if not txt:
            continue
        if "informacionProcesoContratacion" in href or "idSoliCompra" in href or "detalle" in href or "verProceso" in href:
            rows.append({"title": txt, "href": href})
    if not rows:
        # fallback: table rows
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


def download_documents(rows: List[dict], out_dir: Path, sample_n: int = 3) -> List[dict]:
    import requests
    from urllib.parse import urljoin

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
            soup = BeautifulSoup(resp.text, "html.parser")
            docs = []
            for a in soup.find_all("a", href=True):
                link = a["href"]
                if link.lower().endswith(('.pdf', '.zip', '.doc', '.docx', '.xls', '.xlsx')):
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


async def run(captcha_text: str, url: str = DEFAULT_URL, out_dir: str = "rag/discovery/out_cdp") -> int:
    try:
        import pydoll
        from pydoll import browser as _browser
    except Exception as exc:
        print("pydoll import failed:", exc)
        return 3

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    trace_id = str(uuid.uuid4())
    try:
        async with _browser.Chrome() as browser:
            tab = await browser.start()
            try:
                await tab.go_to(url)
            except Exception:
                try:
                    await tab.navigate(url)
                except Exception:
                    pass

            # small wait for scripts
            try:
                await tab.wait_for_network_idle(timeout=3)
            except Exception:
                await asyncio.sleep(1)

            # inject captcha into form and submit
            js = (
                "(function(){"
                "var f = document.forms[0]; if(!f) return {error:'no-form'};"
                f"var set = function(n,v){{ try{{ var el = f.elements[n]; if(el) el.value=v; }}catch(e){{}} }};"
                f"set('image','{captcha_text}'); set('captccc2','1'); set('paginaActual','0');"
                "var btn = f.querySelector('[type=submit]') || f.querySelector('button');"
                "if(btn){ btn.click(); return {submitted:true}; } else { f.submit(); return {submitted:true}; } })();"
            )

            eval_fn = getattr(tab, "eval", None) or getattr(tab, "evaluate", None)
            try:
                if callable(eval_fn):
                    await eval_fn(js, return_by_value=True)
            except Exception:
                pass

            try:
                await tab.wait_for_navigation(timeout=8)
            except Exception:
                try:
                    await tab.wait_for_network_idle(timeout=6)
                except Exception:
                    await asyncio.sleep(2)

            # capture HTML
            html = None
            try:
                if callable(eval_fn):
                    html = await eval_fn("document.documentElement.outerHTML", return_by_value=True)
            except Exception:
                html = None

            if not html:
                # fallback: try to get innerText
                try:
                    html = await eval_fn("document.documentElement.innerHTML", return_by_value=True)
                except Exception:
                    html = ""

            # save html
            html_path = out / f"{trace_id}.html"
            html_path.write_text(html or "", encoding="utf-8")

            # parse rows
            rows = parse_rows_from_html(html or "", base_url=url)
            print(f"Parsed {len(rows)} candidate rows")

            # save results
            results_file = out / f"{trace_id}.results.jsonl"
            with results_file.open("w", encoding="utf-8") as fh:
                for i, r in enumerate(rows[:10]):
                    rec = {"trace_id": trace_id, "rank": i + 1, "title": r.get("title"), "href": r.get("href")}
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

            # download docs
            docs_out = out / f"{trace_id}-docs"
            docs_report = download_documents(rows, docs_out, sample_n=3)
            (out / f"{trace_id}.meta.json").write_text(json.dumps({"trace_id": trace_id, "rows": len(rows), "docs_report": docs_report}, ensure_ascii=False, indent=2), encoding="utf-8")

            print("Wrote results to", results_file)
            print("Docs report:", json.dumps(docs_report, ensure_ascii=False))
            return 0

    except Exception as exc:
        print("CDP run failed:", exc)
        return 4


def main(argv: List[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: run_sercop_cdp_with_captcha.py <captcha_text>")
        return 2
    captcha = argv[0]
    return asyncio.run(run(captcha))


if __name__ == "__main__":
    raise SystemExit(main())
