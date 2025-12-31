#!/usr/bin/env python3
"""
REFINED INSTITUTIONAL SCRAPER
=============================
Deeper scraping with:
- Waiting for specific selectors
- Catching all links, not just .pdf extension
- Handling IESS nested structures
"""

import asyncio
import os
import subprocess
import tempfile
import time
from playwright.async_api import async_playwright
from urllib.parse import urljoin

S3_BUCKET = "s3://yachaq-lex-raw-0017472631"

async def scrape_iess_deep():
    print("\n🚀 Deep Scraping IESS Resoluciones...")
    url = "https://www.iess.gob.ec/es/web/guest/resoluciones-del-c.d"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
        # Look for all links
        links = await page.query_selector_all("a")
        found = []
        for link in links:
            href = await link.get_attribute("href")
            text = await link.inner_text()
            if href and ("pdf" in href.lower() or "resolucion" in text.lower()):
                found.append((text.strip(), urljoin(url, href)))
        
        print(f"   Found {len(found)} potential links in IESS")
        for i, (text, pdf_url) in enumerate(found[:5]):
            print(f"   [{i+1}] {text[:50]} -> {pdf_url[:50]}...")
            # Try to download
        
        await browser.close()

async def scrape_sri_deep():
    print("\n🚀 Deep Scraping SRI Normativa...")
    url = "https://www.sri.gob.ec/normativa-tributaria"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
        # SRI uses specific areas for normativa
        # Let's find links that look like normativa
        links = await page.query_selector_all("a")
        found = []
        for link in links:
            href = await link.get_attribute("href")
            text = await link.inner_text()
            if href and ("ley" in text.lower() or "reglamento" in text.lower() or "circular" in text.lower()):
                found.append((text.strip(), urljoin(url, href)))

        print(f"   Found {len(found)} potential links in SRI")
        for i, (text, pdf_url) in enumerate(found[:5]):
            print(f"   [{i+1}] {text[:50]} -> {pdf_url[:50]}...")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_iess_deep())
    asyncio.run(scrape_sri_deep())
