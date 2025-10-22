import asyncio
import sys
from datetime import datetime

URL = "https://www.compraspublicas.gob.ec/ProcesoContratacion/compras/PC/buscarProceso.cpe?sg=1"
OUT_MD = "rag/discovery/out_sercop_crawl4ai.md"
OUT_JSON = "rag/discovery/out_sercop_crawl4ai.json"

async def main():
    try:
        from crawl4ai import AsyncWebCrawler
    except Exception as e:
        print("crawl4ai not installed:", e, file=sys.stderr)
        raise

    async with AsyncWebCrawler() as crawler:
        print(f"Crawling {URL} ...")
        result = await crawler.arun(url=URL)
        markdown = getattr(result, "markdown", "")
        data = {
            "url": URL,
            "captured_at": datetime.utcnow().isoformat() + "Z",
            "markdown": markdown,
        }
        with open(OUT_MD, "w", encoding="utf-8") as f:
            f.write(markdown or "")
        import json
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Wrote markdown -> {OUT_MD}")

if __name__ == '__main__':
    asyncio.run(main())
