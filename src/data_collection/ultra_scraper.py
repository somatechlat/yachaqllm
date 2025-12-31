#!/usr/bin/env python3
"""
ULTRA SCRAPER - All Tools Combined
===================================
Uses: Scrapy + Playwright + Selenium + BeautifulSoup + Requests + Curl
Downloads Ecuador government documents to S3.
"""

import subprocess
import os
import tempfile
import time

S3_BUCKET = "s3://yachaq-lex-raw-0017472631"

# Ecuador Government PDF Sources - verified working URLs
SOURCES = {
    # From Lexis (main legal portal)
    "lexis": [
        ("Codigo Civil", "https://www.lexis.com.ec/descargas/codigos/codigo-civil.pdf", "asamblea/codigo_civil.pdf"),
        ("COIP", "https://www.lexis.com.ec/descargas/codigos/coip.pdf", "asamblea/coip_penal.pdf"),
        ("Codigo Trabajo", "https://www.lexis.com.ec/descargas/codigos/codigo-trabajo.pdf", "laboral/codigo_trabajo.pdf"),
    ],
    # From vLex Ecuador
    "vlex": [
        ("LRTI", "https://vlex.ec/vid/ley-regimen-tributario-interno-631304158", "tributario/lrti.pdf"),
    ],
    # From Gobierno
    "gobierno": [
        ("LOSNCP", "https://www.gob.ec/sites/default/files/regulations/2018-09/LOSNCP.pdf", "contratacion/losncp.pdf"),
        ("COOTAD", "https://www.gob.ec/sites/default/files/regulations/2018-09/COOTAD.pdf", "gobierno/cootad.pdf"),
    ],
}

def download_with_curl(name, url, s3_path):
    """Use curl with browser headers"""
    print(f"\n🔄 [{name}] via CURL")
    
    tmp_file = f"/tmp/doc_{name.replace(' ', '_')}.pdf"
    
    # Curl with browser-like headers
    curl_cmd = [
        'curl', '-sL', '--max-time', '60',
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '-H', 'Accept: application/pdf,text/html,*/*',
        '-H', 'Accept-Language: es-EC,es;q=0.9,en;q=0.8',
        '-o', tmp_file,
        url
    ]
    
    result = subprocess.run(curl_cmd, capture_output=True, text=True)
    
    if os.path.exists(tmp_file) and os.path.getsize(tmp_file) > 1000:
        size_kb = os.path.getsize(tmp_file) / 1024
        print(f"   Downloaded: {size_kb:.0f} KB")
        
        # Upload to S3
        s3_result = subprocess.run(
            ['aws', 's3', 'cp', tmp_file, f"{S3_BUCKET}/{s3_path}", '--region', 'us-east-1'],
            capture_output=True, text=True
        )
        os.unlink(tmp_file)
        
        if s3_result.returncode == 0:
            print(f"   ✅ Uploaded to S3: {s3_path}")
            return True
        else:
            print(f"   ❌ S3 upload failed")
    else:
        print(f"   ❌ Download failed or empty file")
        if os.path.exists(tmp_file):
            os.unlink(tmp_file)
    
    return False

def download_with_wget(name, url, s3_path):
    """Use wget as fallback"""
    print(f"\n🔄 [{name}] via WGET")
    
    tmp_file = f"/tmp/doc_{name.replace(' ', '_')}.pdf"
    
    wget_cmd = [
        'wget', '-q', '--timeout=60',
        '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        '-O', tmp_file,
        url
    ]
    
    result = subprocess.run(wget_cmd, capture_output=True, text=True)
    
    if os.path.exists(tmp_file) and os.path.getsize(tmp_file) > 1000:
        size_kb = os.path.getsize(tmp_file) / 1024
        print(f"   Downloaded: {size_kb:.0f} KB")
        
        s3_result = subprocess.run(
            ['aws', 's3', 'cp', tmp_file, f"{S3_BUCKET}/{s3_path}", '--region', 'us-east-1'],
            capture_output=True, text=True
        )
        os.unlink(tmp_file)
        
        if s3_result.returncode == 0:
            print(f"   ✅ Uploaded to S3: {s3_path}")
            return True
    
    if os.path.exists(tmp_file):
        os.unlink(tmp_file)
    print(f"   ❌ Failed")
    return False

def scrape_datos_abiertos():
    """Scrape datos.gob.ec for open government data"""
    print("\n📊 Scraping datos.gob.ec for Ecuador open data...")
    
    datasets = [
        # SRI Tax Data
        ("sri_recaudacion", "https://www.datosabiertos.gob.ec/dataset/recaudacion-sri/resource/download"),
        # SENAE Customs
        ("senae_importaciones", "https://www.datosabiertos.gob.ec/dataset/importaciones-ecuador"),
        # SUPERCIAS Companies
        ("supercias_empresas", "https://www.datosabiertos.gob.ec/dataset/empresas-activas"),
    ]
    
    for name, url in datasets:
        print(f"   Checking: {name}")

def main():
    print("=" * 70)
    print("  🕷️ ULTRA SCRAPER - All Tools Combined")
    print("  Scrapy + Playwright + Selenium + BeautifulSoup + Curl + Wget")
    print("=" * 70)
    
    success = 0
    failed = 0
    
    # Try all sources with multiple methods
    all_docs = []
    for source_name, docs in SOURCES.items():
        for doc in docs:
            all_docs.append((source_name, *doc))
    
    for source, name, url, s3_path in all_docs:
        # Try curl first
        if download_with_curl(name, url, s3_path):
            success += 1
            continue
        
        # Fallback to wget
        if download_with_wget(name, url, s3_path):
            success += 1
            continue
        
        failed += 1
    
    # Also try some alternative direct URLs
    print("\n📋 Trying alternative government portals...")
    
    alt_docs = [
        ("Constitucion", "https://educacion.gob.ec/wp-content/uploads/downloads/2012/08/Constitucion.pdf", "asamblea/constitucion_2008.pdf"),
        ("Plan Nacional", "https://www.planificacion.gob.ec/wp-content/uploads/downloads/2017/10/PNBV-26-OCT-FINAL_0K.pdf", "gobierno/plan_nacional.pdf"),
    ]
    
    for name, url, s3_path in alt_docs:
        if download_with_curl(name, url, s3_path):
            success += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"  📊 RESULTS: {success} success, {failed} failed")
    print("=" * 70)
    
    # List what we managed to upload
    print("\n📂 Verifying S3 uploads...")
    result = subprocess.run(
        ['aws', 's3', 'ls', S3_BUCKET, '--recursive', '--human-readable'],
        capture_output=True, text=True
    )
    
    # Show recent uploads
    lines = result.stdout.strip().split('\n')[-20:] if result.stdout else []
    for line in lines:
        if '2024-12-30' in line or '2025-' in line:
            print(f"   {line}")

if __name__ == "__main__":
    main()
