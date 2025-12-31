#!/usr/bin/env python3
"""
MEGA INSTITUTIONAL SCRAPER
==========================
Uses Playwright (headless) to extract documents from complex institutional sites:
- IESS (Resoluciones)
- SENAE (Normativa Aduanera)
- SRI (Normativa Tributaria)
Downloads directly to S3.
"""

import asyncio
import os
import subprocess
import tempfile
import time
from playwright.async_api import async_playwright

S3_BUCKET = "s3://yachaq-lex-raw-0017472631"

targets = [
    {
        "name": "IESS_Resoluciones",
        "url": "https://www.iess.gob.ec/es/web/guest/resoluciones-del-c.d",
        "s3_prefix": "iess/resoluciones/",
        "selector": "a[href*='.pdf']"
    },
    {
        "name": "SENAE_Normativa",
        "url": "https://www.aduana.gob.ec/biblioteca-senae/",
        "s3_prefix": "aduanas/normativa/",
        "selector": "a[href*='.pdf']"
    },
    {
        "name": "SRI_Normativa",
        "url": "https://www.sri.gob.ec/normativa-tributaria",
        "s3_prefix": "tributario/normativa/",
        "selector": "a[href*='.pdf']"
    }
]

async def scrape_institutional(target):
    name = target["name"]
    url = target["url"]
    s3_prefix = target["s3_prefix"]
    selector = target["selector"]

    print(f"\n🚀 Scraping {name}...")
    print(f"   URL: {url}")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            # Navigate with long timeout
            await page.goto(url, wait_until="networkidle", timeout=90000)
            print(f"   ✓ Page loaded")

            # Scroll to load more if needed
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

            # Find all PDF links
            links = await page.query_selector_all(selector)
            found_urls = []
            for link in links:
                href = await link.get_attribute("href")
                if href and href.lower().endswith(".pdf"):
                    # Handle relative URLs
                    if href.startswith("/"):
                        from urllib.parse import urljoin
                        href = urljoin(url, href)
                    found_urls.append(href)

            found_urls = list(set(found_urls)) # Deduplicate
            print(f"   Found {len(found_urls)} potential PDF documents")

            # Process top 5 to avoid overloading
            success_count = 0
            for i, pdf_url in enumerate(found_urls[:5]):
                print(f"   [{i+1}/5] Downloading: {pdf_url.split('/')[-1]}")
                
                try:
                    # Download content
                    response = await page.request.get(pdf_url, timeout=30000)
                    if response.ok:
                        content = await response.body()
                        filename = pdf_url.split('/')[-1]
                        if not filename.endswith(".pdf"): filename += ".pdf"
                        
                        # Save temp
                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                            tmp.write(content)
                            tmp_path = tmp.name
                        
                        # Upload S3
                        s3_full_path = f"{S3_BUCKET}/{s3_prefix}{filename}"
                        res = subprocess.run(['aws', 's3', 'cp', tmp_path, s3_full_path, '--region', 'us-east-1'], capture_output=True)
                        os.unlink(tmp_path)
                        
                        if res.returncode == 0:
                            print(f"      ✅ S3: {filename}")
                            success_count += 1
                        else:
                            print(f"      ❌ S3 failed")
                    else:
                        print(f"      ❌ Download status: {response.status}")
                except Exception as e:
                    print(f"      ❌ Error: {str(e)[:50]}")

            print(f"   ✨ Completed {name}: {success_count} files uploaded")
            await browser.close()
            return success_count

        except Exception as e:
            print(f"   ❌ Scraper failed for {name}: {str(e)[:60]}")
            return 0

async def main():
    print("=" * 60)
    print("  🏛️ MEGA INSTITUTIONAL SCRAPER")
    print("=" * 60)
    
    total_success = 0
    for target in targets:
        total_success += await scrape_institutional(target)
    
    print("\n" + "=" * 60)
    print(f"  📊 FINAL RESULTS: {total_success} documents added to S3")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
