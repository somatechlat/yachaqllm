#!/usr/bin/env python3
"""
HEADLESS GOVERNMENT PDF DOWNLOADER
===================================
Uses Playwright (headless) + BeautifulSoup to download Ecuador government docs.
No visual browser - console only.
"""

import asyncio
import subprocess
import os
import tempfile
from bs4 import BeautifulSoup

# Check for playwright
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Installing playwright...")
    subprocess.run(['pip3', 'install', 'playwright', 'beautifulsoup4', '-q'])
    subprocess.run(['playwright', 'install', 'chromium'])
    from playwright.async_api import async_playwright

S3_BUCKET = "s3://yachaq-lex-raw-0017472631"

# Updated URLs - using known working PDF endpoints
SOURCES = [
    {
        "url": "https://www.finanzas.gob.ec/wp-content/uploads/downloads/2023/legislacion/LOPDP.pdf",
        "s3_path": "asamblea/year=2021/lopdp_ley_proteccion_datos_personales.pdf",
        "name": "LOPDP"
    },
    {
        "url": "https://www.finanzas.gob.ec/wp-content/uploads/downloads/2023/legislacion/COOTAD.pdf",
        "s3_path": "gobierno/cootad.pdf",
        "name": "COOTAD"
    },
    {
        "url": "https://www.finanzas.gob.ec/wp-content/uploads/downloads/2023/legislacion/CODIGO_ORGANICO_AMBIENTE.pdf",
        "s3_path": "asamblea/year=2017/coa_codigo_organico_ambiente.pdf",
        "name": "COA"
    },
    {
        "url": "https://www.finanzas.gob.ec/wp-content/uploads/downloads/2023/legislacion/COPCI.pdf",
        "s3_path": "gobierno/copci_comercio.pdf",
        "name": "COPCI"
    },
]

async def download_with_playwright(url, name, s3_path):
    """Use Playwright headless to download PDF"""
    print(f"\n📥 {name}")
    print(f"   URL: {url[:60]}...")
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(accept_downloads=True)
            page = await context.new_page()
            
            # Navigate
            response = await page.goto(url, wait_until='networkidle', timeout=60000)
            
            if response and response.ok:
                # Get page content for PDF or HTML
                content_type = response.headers.get('content-type', '')
                
                if 'application/pdf' in content_type:
                    # Direct PDF download
                    content = await response.body()
                    
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                        tmp.write(content)
                        tmp_path = tmp.name
                    
                    print(f"   Size: {len(content)/1024:.0f} KB")
                    
                    # Upload to S3
                    result = subprocess.run(
                        ['aws', 's3', 'cp', tmp_path, f"{S3_BUCKET}/{s3_path}", '--region', 'us-east-1'],
                        capture_output=True, text=True
                    )
                    os.unlink(tmp_path)
                    
                    if result.returncode == 0:
                        print(f"   ✅ Uploaded to S3")
                        await browser.close()
                        return True
                    else:
                        print(f"   ❌ S3 upload failed")
                else:
                    # HTML page - try to find PDF links
                    html = await page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
                    
                    if pdf_links:
                        print(f"   Found {len(pdf_links)} PDF links")
                        for link in pdf_links[:3]:
                            print(f"   - {link.get('href', '')[:50]}")
                    else:
                        print(f"   ❌ No PDF found on page")
            else:
                print(f"   ❌ Failed to load: {response.status if response else 'No response'}")
            
            await browser.close()
            return False
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:60]}")
            return False

async def main():
    print("=" * 60)
    print("  🏛️ HEADLESS GOVERNMENT PDF DOWNLOADER")
    print("  Using Playwright (headless) + BeautifulSoup")
    print("=" * 60)
    
    # Alternative: Try curl with headers
    print("\n📋 Trying curl with browser headers...")
    
    # Use curl with proper headers
    curl_docs = [
        ("LOPDP", "https://www.finanzas.gob.ec/wp-content/uploads/downloads/legislacion/LOPDP.pdf", "asamblea/year=2021/lopdp.pdf"),
        ("COOTAD", "https://www.finanzas.gob.ec/wp-content/uploads/downloads/legislacion/COOTAD.pdf", "gobierno/cootad.pdf"),
        ("LRTI", "https://www.sri.gob.ec/o/sri-tax-portlet/documentos/normativa/LRTI.pdf", "tributario/lrti.pdf"),
    ]
    
    for name, url, s3_path in curl_docs:
        print(f"\n📥 {name}")
        cmd = f'''curl -sL -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" "{url}" -o /tmp/{name}.pdf && aws s3 cp /tmp/{name}.pdf {S3_BUCKET}/{s3_path} --region us-east-1 2>/dev/null && echo "   ✅ Success" || echo "   ❌ Failed"'''
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout or result.stderr or "   Processing...")
    
    # Now try playwright for remaining
    print("\n📋 Using Playwright for remaining sources...")
    
    for source in SOURCES:
        await download_with_playwright(source['url'], source['name'], source['s3_path'])
    
    print("\n" + "=" * 60)
    print("  ✅ Download attempt complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
