#!/usr/bin/env python3
"""
THE CATCH-ALL SCRAPER
=====================
Monitors everything:
- Downloads
- New Pages
- Network Requests for .pdf
"""

import asyncio
import os
import subprocess
import tempfile
from playwright.async_api import async_playwright

S3_BUCKET = "s3://yachaq-lex-raw-0017472631"

async def catch_all_iess():
    print("\n🚀 Catch-All Scraping IESS...")
    url = "https://www.iess.gob.ec/resoluciones/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        
        # Listen for any new page or download
        context.on("page", lambda p: print(f"   📢 New page detected: {p.url[:60]}"))
        page.on("request", lambda r: None) # debug if needed

        await page.goto(url, wait_until="networkidle")
        await asyncio.sleep(5)
        
        # Find anything that looks clickable
        clickable = await page.query_selector_all("a, button")
        print(f"   Found {len(clickable)} clickable elements")
        
        for i, el in enumerate(clickable):
            text = await el.inner_text()
            if "aquí" in text.lower() or "pdf" in text.lower() or "descargar" in text.lower():
                print(f"   [{i}] Clicking '{text.strip()}'...")
                try:
                    # Try to catch EITHER a download or a new page
                    async with context.expect_event("page", timeout=5000) as event:
                        await el.click()
                    new_page = await event.value
                    print(f"      ✓ New tab opened: {new_page.url[:60]}")
                    # If it's a PDF URL, we can download it
                    if ".pdf" in new_page.url.lower():
                         print(f"      🎯 PDF URL found: {new_page.url}")
                except:
                    # Maybe it's a direct download
                    pass
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(catch_all_iess())
