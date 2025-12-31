#!/usr/bin/env python3
"""
DEBUG SCRAPER
Captures screenshots to see what's happening.
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_page(name, url):
    print(f"\n📸 Debugging {name}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5) # Extra wait for JS
            path = f"debug_{name}.png"
            await page.screenshot(path=path)
            print(f"   ✓ Screenshot saved: {path}")
            
            # Print page title and some text
            title = await page.title()
            print(f"   Title: {title}")
            
            # Count links
            links = await page.query_selector_all("a")
            print(f"   Found {len(links)} total links on page")
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
        await browser.close()

async def main():
    # New URLs to test
    targets = [
        ("IESS_Resoluciones_Alt", "https://www.iess.gob.ec/resoluciones/"),
        ("SRI_Biblioteca", "https://www.sri.gob.ec/biblioteca-virtual"),
        ("SENAC_Normativa", "https://www.aduana.gob.ec/normativa-vigente/")
    ]
    for name, url in targets:
        await debug_page(name, url)

if __name__ == "__main__":
    asyncio.run(main())
