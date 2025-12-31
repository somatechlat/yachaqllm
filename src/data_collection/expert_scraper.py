#!/usr/bin/env python3
"""
EXPERT INSTITUTIONAL SCRAPER
Handles:
1. SRI Security Modal (closes it)
2. IESS "(Click aquí)" links
3. Direct download to S3
"""

import asyncio
import os
import subprocess
import tempfile
from playwright.async_api import async_playwright
from urllib.parse import urljoin

S3_BUCKET = "s3://yachaq-lex-raw-0017472631"

async def scrape_iess_expert():
    print("\n🚀 Expert Scraping IESS Resoluciones...")
    url = "https://www.iess.gob.ec/resoluciones/"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        
        await page.goto(url, wait_until="networkidle")
        await asyncio.sleep(3)
        
        # Find all "(Click aquí)" links
        links = await page.get_by_text("(Click aquí)").all()
        print(f"   Found {len(links)} '(Click aquí)' links")
        
        for i, link in enumerate(links[:3]):
            print(f"   [{i+1}] Clicking link...")
            async with page.expect_download() as download_info:
                await link.click()
            download = await download_info.value
            
            # Save and upload
            path = f"/tmp/iess_res_{i}.pdf"
            await download.save_as(path)
            print(f"      ✓ Downloaded: {download.suggested_filename}")
            
            s3_path = f"{S3_BUCKET}/iess/resoluciones/{download.suggested_filename}"
            subprocess.run(['aws', 's3', 'cp', path, s3_path, '--region', 'us-east-1'], capture_output=True)
            os.unlink(path)
            print(f"      ✅ S3 Uploaded")
            
        await browser.close()

async def scrape_sri_expert():
    print("\n🚀 Expert Scraping SRI Biblioteca...")
    url = "https://www.sri.gob.ec/biblioteca-virtual"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        
        await page.goto(url, wait_until="networkidle")
        await asyncio.sleep(5)
        
        # Close modal if exists
        try:
            # Look for close button (often 'x' or a specific class)
            close_button = await page.get_by_label("Close").first
            if await close_button.is_visible():
                await close_button.click()
                print("   ✓ Security modal closed")
        except:
            print("   ⚠️ No modal found or failed to close")
            
        # Look for PDF links
        pdf_links = await page.query_selector_all("a[href*='.pdf']")
        print(f"   Found {len(pdf_links)} direct PDF links")
        
        for i, link in enumerate(pdf_links[:3]):
            href = await link.get_attribute("href")
            full_url = urljoin(url, href)
            print(f"   [{i+1}] Downloading: {full_url.split('/')[-1]}")
            
            async with page.expect_download() as download_info:
                await link.click()
            download = await download_info.value
            
            path = f"/tmp/sri_{i}.pdf"
            await download.save_as(path)
            s3_path = f"{S3_BUCKET}/tributario/biblioteca/{download.suggested_filename}"
            subprocess.run(['aws', 's3', 'cp', path, s3_path, '--region', 'us-east-1'], capture_output=True)
            os.unlink(path)
            print(f"      ✅ S3 Uploaded")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_iess_expert())
    asyncio.run(scrape_sri_expert())
