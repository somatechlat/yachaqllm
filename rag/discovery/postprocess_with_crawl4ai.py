import asyncio
import json
import sys
from pathlib import Path
import subprocess
import tempfile
import venv
import shutil


async def run_on_file(html_path: str):
    try:
        from crawl4ai import AsyncWebCrawler
    except Exception as e:
        # If crawl4ai is not importable (or incompatible with current deps),
        # create a temporary venv, install crawl4ai there, and run a short
        # subprocess that performs the crawl. This avoids modifying the main
        # project's venv and isolates dependency resolution.
        print("crawl4ai not importable in main env, attempting isolated venv:", e, file=sys.stderr)
        tmpdir = Path(tempfile.mkdtemp(prefix="c4ai-venv-"))
        try:
            venv.create(tmpdir, with_pip=True)
            py = tmpdir / ("bin/python" if sys.platform != "win32" else "Scripts\\python.exe")
            # pip install crawl4ai into tmp venv
            subprocess.check_call([str(py), "-m", "pip", "install", "--quiet", "crawl4ai"]) 
            # run the helper script inside the venv
            helper = Path(__file__).with_suffix(".runner.py")
            helper.write_text("""
import asyncio, json, sys
from crawl4ai import AsyncWebCrawler
async def main(p):
    async with AsyncWebCrawler() as crawler:
        r = await crawler.arun(url=p)
        print('CRAWL4AI_DONE')
        md = getattr(r, 'markdown', '')
        print(md)
if __name__ == '__main__':
    asyncio.run(main(sys.argv[1]))
""")
            # run it with the file:// URL
            url = f"file://{Path(html_path).resolve()}"
            out = subprocess.check_output([str(py), str(helper), url], stderr=subprocess.STDOUT, text=True)
            # parse output (helper prints markdown after sentinel)
            if "CRAWL4AI_DONE" in out:
                md = out.split("CRAWL4AI_DONE", 1)[1].strip()
                p = Path(html_path)
                out_md = p.with_suffix(".crawl4ai.md")
                out_json = p.with_suffix(".crawl4ai.json")
                out_md.write_text(md or "", encoding="utf-8")
                json.dump({"url": str(p), "markdown": md}, out_json.open("w", encoding="utf-8"), ensure_ascii=False, indent=2)
                print("Wrote", out_md, out_json)
            else:
                raise RuntimeError("crawl4ai runner failed")
        finally:
            try:
                shutil.rmtree(tmpdir)
            except Exception:
                pass
        return

    p = Path(html_path)
    if not p.exists():
        raise FileNotFoundError(f"HTML snapshot not found: {html_path}")

    # Crawl4AI prefers URLs, but can accept file://
    url = f"file://{p.resolve()}"
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        markdown = getattr(result, "markdown", "")
        out_md = p.with_suffix(".crawl4ai.md")
        out_json = p.with_suffix(".crawl4ai.json")
        with out_md.open("w", encoding="utf-8") as f:
            f.write(markdown or "")
        with out_json.open("w", encoding="utf-8") as f:
            json.dump({"url": str(p), "markdown": markdown}, f, ensure_ascii=False, indent=2)
        print("Wrote", out_md, out_json)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: postprocess_with_crawl4ai.py <path-to-html-snapshot>")
        raise SystemExit(2)
    asyncio.run(run_on_file(sys.argv[1]))
