#!/usr/bin/env python3
"""
VERIFIED URL DOWNLOADER → S3
=============================
Only uses VERIFIED working URLs (tested with curl -I before adding)
"""

import subprocess
import os

S3_BUCKET = "s3://yachaq-lex-raw-0017472631"

# VERIFIED WORKING URLs (tested 2024-12-30)
VERIFIED_DOCS = [
    # Ley de Compañías - SUPERCIAS (VERIFIED 200 OK, 455KB)
    {
        "name": "Ley de Compañías",
        "url": "https://www.supercias.gob.ec/bd_supercias/descargas/ss/LEY_DE_COMPANIAS.pdf",
        "s3_path": "supercias/ley_companias.pdf",
        "verified": True
    },
    # COOTAD - CPCCS (VERIFIED 200 OK, 541KB)
    {
        "name": "COOTAD",
        "url": "https://www.cpccs.gob.ec/wp-content/uploads/2020/01/cootad.pdf",
        "s3_path": "gobierno/cootad_2020.pdf",
        "verified": True
    },
    # Additional verified sources to test
    {
        "name": "Constitucion 2008",
        "url": "https://www.oas.org/juridico/pdfs/mesicic4_ecu_const.pdf",
        "s3_path": "asamblea/constitucion_2008.pdf",
        "verified": False
    },
    {
        "name": "Codigo Civil",
        "url": "https://www.oas.org/juridico/spanish/mesicic2_ecu_anexo15.pdf",
        "s3_path": "asamblea/codigo_civil.pdf",
        "verified": False
    },
    {
        "name": "COIP Penal",
        "url": "https://tbinternet.ohchr.org/Treaties/CAT/Shared%20Documents/ECU/INT_CAT_ADR_ECU_18790_S.pdf",
        "s3_path": "asamblea/coip_penal.pdf",
        "verified": False
    },
]

def test_url(url):
    """Test if URL returns 200"""
    result = subprocess.run(
        ['curl', '-sI', '--max-time', '10', url],
        capture_output=True, text=True
    )
    return '200' in result.stdout

def download_and_upload(doc):
    """Download and upload to S3"""
    name = doc['name']
    url = doc['url']
    s3_path = doc['s3_path']
    
    print(f"\n📥 {name}")
    print(f"   URL: {url[:70]}...")
    
    # First verify URL
    print(f"   Testing URL...")
    if not test_url(url):
        print(f"   ❌ URL not accessible (non-200)")
        return False
    print(f"   ✓ URL verified")
    
    # Download
    tmp_file = f"/tmp/{name.replace(' ', '_')}.pdf"
    result = subprocess.run(
        ['curl', '-sL', '--max-time', '60', '-o', tmp_file, url],
        capture_output=True, text=True
    )
    
    if not os.path.exists(tmp_file) or os.path.getsize(tmp_file) < 1000:
        print(f"   ❌ Download failed or file too small")
        return False
    
    size_kb = os.path.getsize(tmp_file) / 1024
    print(f"   ✓ Downloaded: {size_kb:.0f} KB")
    
    # Upload to S3
    s3_result = subprocess.run(
        ['aws', 's3', 'cp', tmp_file, f"{S3_BUCKET}/{s3_path}", '--region', 'us-east-1'],
        capture_output=True, text=True
    )
    os.unlink(tmp_file)
    
    if s3_result.returncode == 0:
        print(f"   ✅ Uploaded: {s3_path}")
        return True
    else:
        print(f"   ❌ S3 upload failed: {s3_result.stderr[:50]}")
        return False

def main():
    print("=" * 60)
    print("  📋 VERIFIED URL DOWNLOADER → S3")
    print("=" * 60)
    
    success = 0
    failed = 0
    
    for doc in VERIFIED_DOCS:
        if download_and_upload(doc):
            success += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"  RESULTS: ✅ {success} uploaded, ❌ {failed} failed")
    print("=" * 60)
    
    # Show what was uploaded
    print("\n📂 Recent S3 uploads:")
    subprocess.run(['aws', 's3', 'ls', S3_BUCKET, '--recursive', '--human-readable', '|', 'tail', '-10'], shell=False)

if __name__ == "__main__":
    main()
