CRETE #!/usr/bin/env python3
"""
🧠 YACHAQ INTELLIGENT DOCUMENT HUNTER
=====================================
A smart, autonomous crawler that:
1. Searches for documents using multiple strategies
2. Crawls government portals systematically
3. Validates and downloads PDFs
4. Uploads directly to S3

Uses: requests, BeautifulSoup, concurrent downloads
"""

import os
import re
import hashlib
import subprocess
import tempfile
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.run(['pip3', 'install', 'requests', 'beautifulsoup4', '-q'])
    import requests
    from bs4 import BeautifulSoup

# Configuration
S3_BUCKET = "s3://yachaq-lex-raw-0017472631"
MAX_WORKERS = 5
TIMEOUT = 30

# What we're hunting for
TARGET_DOCUMENTS = {
    # Core Legal Documents
    "ley_seguridad_social": {
        "keywords": ["Ley de Seguridad Social", "IESS", "seguro social"],
        "s3_path": "iess/ley_seguridad_social.pdf"
    },
    "copci": {
        "keywords": ["COPCI", "Código Orgánico de la Producción", "comercio inversiones"],
        "s3_path": "aduanas/copci.pdf"
    },
    "codigo_ingenios": {
        "keywords": ["Código Ingenios", "Economía Social de los Conocimientos", "SENADI"],
        "s3_path": "propiedad_intelectual/codigo_ingenios.pdf"
    },
    "lrti": {
        "keywords": ["LRTI", "Ley de Régimen Tributario Interno", "impuesto renta"],
        "s3_path": "tributario/lrti.pdf"
    },
    "codigo_trabajo": {
        "keywords": ["Código del Trabajo", "código laboral", "trabajadores"],
        "s3_path": "laboral/codigo_trabajo.pdf"
    },
    "losncp": {
        "keywords": ["LOSNCP", "contratación pública", "SERCOP"],
        "s3_path": "contratacion/losncp.pdf"
    },
    "ley_companias": {
        "keywords": ["Ley de Compañías", "sociedades", "SUPERCIAS"],
        "s3_path": "supercias/ley_companias.pdf"
    },
    "coa": {
        "keywords": ["Código Orgánico del Ambiente", "COA", "ambiental"],
        "s3_path": "ambiente/coa.pdf"
    },
}

# Known government portals to crawl
GOV_PORTALS = [
    "https://www.gob.ec/regulaciones",
    "https://www.finanzas.gob.ec/normativa/",
    "https://www.trabajo.gob.ec/biblioteca/",
    "https://www.supercias.gob.ec/portalscvs/",
    "https://portal.compraspublicas.gob.ec/sercop/normativa/",
    "https://www.aduana.gob.ec/normativa-vigente/",
    "https://www.sri.gob.ec/normativa",
    "https://www.iess.gob.ec/es/web/guest/normativa",
    "https://biblioteca.defensoria.gob.ec/",
]

# Direct verified URLs (fallback)
VERIFIED_URLS = {
    "ley_seguridad_social": "https://biblioteca.defensoria.gob.ec/bitstream/37000/3398/1/Ley%20de%20Seguridad%20Social.pdf",
    "copci": "https://www.aduana.gob.ec/wp-content/uploads/2019/05/COPCI-21-02-2019.pdf",
    "codigo_ingenios": "http://www.derechosintelectuales.gob.ec/wp-content/uploads/downloads/2024/enero/a_2_16_codigo_ingenios_enero_2024.pdf",
    "ley_companias": "https://www.supercias.gob.ec/bd_supercias/descargas/ss/LEY_DE_COMPANIAS.pdf",
    "cootad": "https://www.cpccs.gob.ec/wp-content/uploads/2020/01/cootad.pdf",
    "constitucion": "https://www.oas.org/juridico/pdfs/mesicic4_ecu_const.pdf",
    "codigo_civil": "https://www.oas.org/juridico/spanish/mesicic2_ecu_anexo15.pdf",
}

class DocumentHunter:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8',
            'Accept-Language': 'es-EC,es;q=0.9,en;q=0.8',
        })
        self.downloaded = set()
        self.failed = []
        self.stats = defaultdict(int)
    
    def is_valid_pdf(self, content):
        """Check if content is a valid PDF"""
        return content[:4] == b'%PDF'
    
    def download_and_upload(self, url, s3_path, doc_name):
        """Download a URL and upload to S3 if valid PDF"""
        try:
            print(f"   📥 Downloading: {url[:60]}...")
            response = self.session.get(url, timeout=TIMEOUT, verify=False, stream=True)
            
            if response.status_code == 200:
                content = response.content
                
                if self.is_valid_pdf(content):
                    # Save temp and upload
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                        tmp.write(content)
                        tmp_path = tmp.name
                    
                    size_kb = len(content) / 1024
                    print(f"   ✓ Valid PDF ({size_kb:.0f} KB)")
                    
                    # Upload to S3
                    full_s3_path = f"{S3_BUCKET}/{s3_path}"
                    result = subprocess.run(
                        ['aws', 's3', 'cp', tmp_path, full_s3_path, '--region', 'us-east-1'],
                        capture_output=True, text=True
                    )
                    os.unlink(tmp_path)
                    
                    if result.returncode == 0:
                        print(f"   ✅ S3: {s3_path}")
                        self.downloaded.add(doc_name)
                        self.stats["uploaded"] += 1
                        return True
                else:
                    print(f"   ⚠️ Not a PDF (HTML page or error)")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:40]}")
        
        self.stats["failed"] += 1
        return False
    
    def crawl_portal(self, portal_url):
        """Crawl a government portal for PDF links"""
        print(f"\n🔍 Crawling: {portal_url}")
        try:
            response = self.session.get(portal_url, timeout=TIMEOUT, verify=False)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all PDF links
            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text().lower()
                
                # Check if it's a PDF or looks like a legal document
                if '.pdf' in href.lower() or any(kw in text for kw in ['ley', 'código', 'reglamento', 'resolución']):
                    full_url = urllib.parse.urljoin(portal_url, href)
                    pdf_links.append((full_url, text.strip()[:50]))
            
            print(f"   Found {len(pdf_links)} potential documents")
            return pdf_links[:20]  # Limit to avoid overwhelming
            
        except Exception as e:
            print(f"   ❌ Crawl failed: {str(e)[:40]}")
            return []
    
    def hunt(self):
        """Main hunting logic"""
        print("=" * 70)
        print("  🧠 YACHAQ INTELLIGENT DOCUMENT HUNTER")
        print("=" * 70)
        
        # Phase 1: Download verified URLs first (guaranteed to work)
        print("\n📋 PHASE 1: Downloading verified documents...")
        for doc_name, url in VERIFIED_URLS.items():
            if doc_name in TARGET_DOCUMENTS:
                s3_path = TARGET_DOCUMENTS[doc_name]["s3_path"]
            else:
                s3_path = f"legal/{doc_name}.pdf"
            
            print(f"\n🎯 {doc_name}")
            self.download_and_upload(url, s3_path, doc_name)
        
        # Phase 2: Crawl government portals
        print("\n\n📋 PHASE 2: Crawling government portals...")
        all_links = []
        for portal in GOV_PORTALS[:5]:  # Limit portals for speed
            links = self.crawl_portal(portal)
            all_links.extend(links)
        
        # Phase 3: Download promising links
        print(f"\n\n📋 PHASE 3: Processing {len(all_links)} discovered links...")
        for url, title in all_links[:10]:
            # Match against target documents
            for doc_name, info in TARGET_DOCUMENTS.items():
                if doc_name not in self.downloaded:
                    if any(kw.lower() in title.lower() or kw.lower() in url.lower() for kw in info["keywords"]):
                        print(f"\n🎯 Potential match for {doc_name}: {title}")
                        self.download_and_upload(url, info["s3_path"], doc_name)
                        break
        
        # Summary
        print("\n" + "=" * 70)
        print("  📊 HUNT COMPLETE")
        print("=" * 70)
        print(f"  ✅ Uploaded: {self.stats['uploaded']}")
        print(f"  ❌ Failed: {self.stats['failed']}")
        print(f"\n  📂 Documents in S3:")
        for doc in self.downloaded:
            print(f"     - {doc}")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore')
    
    hunter = DocumentHunter()
    hunter.hunt()
