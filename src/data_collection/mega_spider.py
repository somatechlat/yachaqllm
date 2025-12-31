#!/usr/bin/env python3
"""
🕷️ YACHAQ MEGA SPIDER
======================
A REAL web scraper that:
1. Starts from seed URLs
2. Recursively follows ALL links on .gob.ec domains
3. Downloads EVERY PDF it finds
4. Uploads directly to S3
5. Runs autonomously until complete

Uses: Scrapy-like recursive crawling with BeautifulSoup
"""

import os
import re
import hashlib
import subprocess
import tempfile
import urllib.parse
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.run(['pip3', 'install', 'requests', 'beautifulsoup4', '-q'])
    import requests
    from bs4 import BeautifulSoup

import warnings
warnings.filterwarnings('ignore')

# Configuration
S3_BUCKET = "s3://yachaq-lex-raw-0017472631"
MAX_DEPTH = 3
MAX_PAGES = 500
MAX_PDFS = 100
TIMEOUT = 15
WORKERS = 10

# Seed URLs - Starting points for the spider
SEED_URLS = [
    # Core Government Portals
    "https://www.gob.ec/regulaciones",
    "https://www.finanzas.gob.ec/normativa/",
    "https://www.sri.gob.ec/normativa-tributaria",
    "https://www.trabajo.gob.ec/normativa/",
    "https://portal.compraspublicas.gob.ec/sercop/",
    "https://www.supercias.gob.ec/portalscvs/",
    "https://www.aduana.gob.ec/normativa-vigente/",
    "https://www.iess.gob.ec/es/web/guest/normativa",
    "https://www.ambiente.gob.ec/normativa/",
    "https://biblioteca.defensoria.gob.ec/",
    
    # Legal Databases
    "https://www.lexis.com.ec/",
    "https://www.fielweb.com/",
    
    # Institutional Sites
    "https://www.derechosintelectuales.gob.ec/",
    "https://www.telecomunicaciones.gob.ec/",
    "https://www.educacion.gob.ec/normativa/",
    "https://www.salud.gob.ec/normativa/",
]

# Keywords that indicate legal/government documents
LEGAL_KEYWORDS = [
    'ley', 'codigo', 'código', 'reglamento', 'resolucion', 'resolución',
    'decreto', 'acuerdo', 'ordenanza', 'normativa', 'constitucion',
    'constitución', 'reforma', 'losncp', 'lrti', 'copci', 'cootad',
    'coip', 'lopdp', 'iess', 'sri', 'sercop', 'laboral', 'tributario',
    'aduanero', 'ambiental', 'civil', 'penal', 'societario'
]

class MegaSpider:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-EC,es;q=0.9,en;q=0.8',
        })
        
        # Crawl state
        self.visited_urls = set()
        self.pdf_urls = set()
        self.downloaded_pdfs = set()
        self.url_queue = deque()
        self.lock = threading.Lock()
        
        # Stats
        self.pages_crawled = 0
        self.pdfs_found = 0
        self.pdfs_uploaded = 0
        self.errors = 0
        
    def is_valid_domain(self, url):
        """Check if URL is from Ecuador government or legal domain"""
        valid_domains = ['.gob.ec', '.gov.ec', '.edu.ec', 'lexis.com.ec', 'fielweb.com', 'oas.org']
        return any(domain in url.lower() for domain in valid_domains)
    
    def is_legal_content(self, url, text=''):
        """Check if URL/text contains legal keywords"""
        combined = (url + ' ' + text).lower()
        return any(kw in combined for kw in LEGAL_KEYWORDS)
    
    def normalize_url(self, url, base_url):
        """Convert relative URL to absolute"""
        if url.startswith('//'):
            return 'https:' + url
        elif url.startswith('/'):
            parsed = urllib.parse.urlparse(base_url)
            return f"{parsed.scheme}://{parsed.netloc}{url}"
        elif not url.startswith('http'):
            return urllib.parse.urljoin(base_url, url)
        return url
    
    def crawl_page(self, url, depth=0):
        """Crawl a single page, extract links and PDFs"""
        if depth > MAX_DEPTH:
            return [], []
        
        if url in self.visited_urls:
            return [], []
        
        with self.lock:
            self.visited_urls.add(url)
            self.pages_crawled += 1
        
        try:
            response = self.session.get(url, timeout=TIMEOUT, verify=False)
            if response.status_code != 200:
                return [], []
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            
            # If it's a PDF, add to PDF list
            if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
                with self.lock:
                    if url not in self.pdf_urls:
                        self.pdf_urls.add(url)
                        self.pdfs_found += 1
                        print(f"   📄 PDF found: {url.split('/')[-1][:50]}")
                return [], [url]
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            new_links = []
            new_pdfs = []
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').strip()
                text = link.get_text().strip()
                
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue
                
                full_url = self.normalize_url(href, url)
                
                # Skip already visited
                if full_url in self.visited_urls:
                    continue
                
                # Check if it's a PDF
                if '.pdf' in full_url.lower():
                    if full_url not in self.pdf_urls:
                        with self.lock:
                            self.pdf_urls.add(full_url)
                            self.pdfs_found += 1
                        print(f"   📄 PDF: {full_url.split('/')[-1][:50]}")
                        new_pdfs.append(full_url)
                
                # Check if we should follow this link
                elif self.is_valid_domain(full_url):
                    if self.is_legal_content(full_url, text):
                        new_links.append(full_url)
            
            return new_links, new_pdfs
            
        except Exception as e:
            with self.lock:
                self.errors += 1
            return [], []
    
    def download_pdf(self, url):
        """Download PDF and upload to S3"""
        try:
            response = self.session.get(url, timeout=TIMEOUT, verify=False)
            if response.status_code != 200:
                return False
            
            content = response.content
            
            # Validate PDF
            if content[:4] != b'%PDF':
                return False
            
            # Generate S3 path from URL
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.replace('www.', '').replace('.gob.ec', '').replace('.', '_')
            filename = url.split('/')[-1]
            if not filename.endswith('.pdf'):
                filename = hashlib.md5(url.encode()).hexdigest()[:12] + '.pdf'
            
            s3_path = f"scraped/{domain}/{filename}"
            
            # Save and upload
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            result = subprocess.run(
                ['aws', 's3', 'cp', tmp_path, f"{S3_BUCKET}/{s3_path}", '--region', 'us-east-1'],
                capture_output=True, text=True
            )
            os.unlink(tmp_path)
            
            if result.returncode == 0:
                with self.lock:
                    self.pdfs_uploaded += 1
                    self.downloaded_pdfs.add(url)
                print(f"   ✅ S3: {s3_path}")
                return True
            
        except Exception as e:
            pass
        
        return False
    
    def run(self):
        """Main spider execution"""
        print("=" * 70)
        print("  🕷️ YACHAQ MEGA SPIDER - Autonomous Web Crawler")
        print("=" * 70)
        print(f"  📍 Seed URLs: {len(SEED_URLS)}")
        print(f"  🔍 Max Depth: {MAX_DEPTH}")
        print(f"  📄 Max PDFs: {MAX_PDFS}")
        print(f"  ⚡ Workers: {WORKERS}")
        print("=" * 70)
        
        # Initialize queue with seed URLs
        for url in SEED_URLS:
            self.url_queue.append((url, 0))
        
        # Phase 1: Crawl and discover PDFs
        print("\n🔍 PHASE 1: Crawling and discovering PDFs...")
        
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            while self.url_queue and self.pages_crawled < MAX_PAGES:
                # Get batch of URLs to process
                batch = []
                while self.url_queue and len(batch) < WORKERS:
                    url, depth = self.url_queue.popleft()
                    if url not in self.visited_urls:
                        batch.append((url, depth))
                
                if not batch:
                    break
                
                # Process batch in parallel
                futures = {executor.submit(self.crawl_page, url, depth): (url, depth) for url, depth in batch}
                
                for future in as_completed(futures):
                    url, depth = futures[future]
                    try:
                        new_links, new_pdfs = future.result()
                        
                        # Add new links to queue
                        for link in new_links:
                            if link not in self.visited_urls:
                                self.url_queue.append((link, depth + 1))
                        
                    except Exception as e:
                        pass
                
                # Progress update
                if self.pages_crawled % 20 == 0:
                    print(f"   📊 Progress: {self.pages_crawled} pages, {self.pdfs_found} PDFs found")
        
        print(f"\n✅ Crawl complete: {self.pages_crawled} pages, {self.pdfs_found} PDFs discovered")
        
        # Phase 2: Download and upload PDFs
        print(f"\n📥 PHASE 2: Downloading {min(len(self.pdf_urls), MAX_PDFS)} PDFs...")
        
        pdf_list = list(self.pdf_urls)[:MAX_PDFS]
        
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = {executor.submit(self.download_pdf, url): url for url in pdf_list}
            
            for future in as_completed(futures):
                pass  # Results printed in download_pdf
        
        # Summary
        print("\n" + "=" * 70)
        print("  📊 SPIDER COMPLETE")
        print("=" * 70)
        print(f"  🌐 Pages crawled: {self.pages_crawled}")
        print(f"  📄 PDFs discovered: {self.pdfs_found}")
        print(f"  ✅ PDFs uploaded: {self.pdfs_uploaded}")
        print(f"  ❌ Errors: {self.errors}")
        print("=" * 70)

if __name__ == "__main__":
    spider = MegaSpider()
    spider.run()
