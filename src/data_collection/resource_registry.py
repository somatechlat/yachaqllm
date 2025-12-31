#!/usr/bin/env python3
"""
🧠 YACHAQ INTELLIGENT RESOURCE REGISTRY
========================================
A SMART data collector that:
1. DISCOVERS web resources from Ecuador government domains
2. BUILDS A REGISTRY with metadata (title, domain, type, size)
3. SCORES each resource for QUALITY and RELEVANCE
4. ONLY downloads resources that pass the quality threshold
5. Uploads to S3 with proper organization

This is NOT a blind scraper - it's an intelligent curator.
"""

import os
import re
import json
import hashlib
import subprocess
import tempfile
import urllib.parse
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

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
REGISTRY_FILE = "/tmp/yachaq_resource_registry.json"
MIN_QUALITY_SCORE = 0.6
MAX_RESOURCES_TO_DOWNLOAD = 50
TIMEOUT = 15

# HIGH-VALUE keywords (score boost)
HIGH_VALUE_KEYWORDS = {
    # Legal codes (highest value)
    'codigo': 3, 'código': 3, 'ley organica': 3, 'ley orgánica': 3,
    'constitucion': 3, 'constitución': 3, 'coip': 3, 'copci': 3,
    'cootad': 3, 'lopdp': 3, 'lrti': 3, 'losncp': 3,
    
    # Regulations (high value)
    'reglamento': 2, 'decreto': 2, 'resolucion': 2, 'resolución': 2,
    'acuerdo ministerial': 2, 'ordenanza': 2,
    
    # Normative (medium value)
    'normativa': 1.5, 'reforma': 1.5, 'codificacion': 1.5,
    
    # Government domains (authority)
    'sri': 1.5, 'sercop': 1.5, 'iess': 1.5, 'supercias': 1.5,
    'aduana': 1.5, 'trabajo': 1.5, 'ambiente': 1.5,
}

# LOW-VALUE keywords (score penalty)
LOW_VALUE_KEYWORDS = {
    'informe': -0.5, 'certificado': -0.5, 'formulario': -0.3,
    'manual usuario': -0.5, 'cronograma': -0.5, 'presupuesto': -0.5,
    'estados financieros': -1, 'balance': -1, 'ejecucion': -0.5,
}

# AUTHORITATIVE domains (score boost)
AUTHORITATIVE_DOMAINS = {
    'asambleanacional.gob.ec': 2,
    'lexis.com.ec': 2,
    'sri.gob.ec': 1.5,
    'trabajo.gob.ec': 1.5,
    'supercias.gob.ec': 1.5,
    'sercop.gob.ec': 1.5,
    'compraspublicas.gob.ec': 1.5,
    'iess.gob.ec': 1.5,
    'aduana.gob.ec': 1.5,
    'oas.org': 1.5,
    'finanzas.gob.ec': 1,
    'defensa.gob.ec': 1,
    'telecomunicaciones.gob.ec': 1,
}

class ResourceRegistry:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        })
        self.resources = []
        self.visited_urls = set()
        
    def calculate_quality_score(self, url, title, domain):
        """Calculate a quality score (0-1) for a resource"""
        score = 0.3  # Base score
        
        combined_text = (url + ' ' + title).lower()
        
        # Apply keyword scoring
        for keyword, boost in HIGH_VALUE_KEYWORDS.items():
            if keyword in combined_text:
                score += boost * 0.1
        
        for keyword, penalty in LOW_VALUE_KEYWORDS.items():
            if keyword in combined_text:
                score += penalty * 0.1
        
        # Apply domain authority
        for auth_domain, boost in AUTHORITATIVE_DOMAINS.items():
            if auth_domain in domain:
                score += boost * 0.15
                break
        
        # Normalize to 0-1
        return max(0, min(1, score))
    
    def categorize_resource(self, url, title):
        """Determine the S3 category for a resource"""
        combined = (url + ' ' + title).lower()
        
        if any(k in combined for k in ['codigo', 'código', 'ley', 'constitucion']):
            return 'legal/codigos'
        elif any(k in combined for k in ['sri', 'tributario', 'impuesto', 'lrti']):
            return 'tributario'
        elif any(k in combined for k in ['sercop', 'contratacion', 'losncp', 'compras publicas']):
            return 'contratacion'
        elif any(k in combined for k in ['trabajo', 'laboral', 'codigo del trabajo']):
            return 'laboral'
        elif any(k in combined for k in ['iess', 'seguridad social', 'pension']):
            return 'iess'
        elif any(k in combined for k in ['aduana', 'copci', 'senae', 'importacion']):
            return 'aduanas'
        elif any(k in combined for k in ['supercias', 'compañia', 'societario']):
            return 'supercias'
        elif any(k in combined for k in ['ambiente', 'coa', 'ambiental']):
            return 'ambiente'
        elif any(k in combined for k in ['reglamento', 'decreto', 'acuerdo']):
            return 'normativa'
        else:
            return 'otros'
    
    def discover_resources(self, seed_urls, max_depth=2):
        """Crawl and discover resources, building the registry"""
        print("=" * 70)
        print("  🧠 PHASE 1: DISCOVERING RESOURCES")
        print("=" * 70)
        
        to_visit = [(url, 0) for url in seed_urls]
        
        while to_visit:
            url, depth = to_visit.pop(0)
            
            if depth > max_depth or url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            try:
                response = self.session.get(url, timeout=TIMEOUT, verify=False)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                domain = urllib.parse.urlparse(url).netloc
                
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '').strip()
                    text = link.get_text().strip()[:100]
                    
                    if not href or href.startswith('#'):
                        continue
                    
                    full_url = urllib.parse.urljoin(url, href)
                    
                    # Check if it's a PDF
                    if '.pdf' in full_url.lower() and full_url not in self.visited_urls:
                        score = self.calculate_quality_score(full_url, text, domain)
                        category = self.categorize_resource(full_url, text)
                        
                        resource = {
                            'url': full_url,
                            'title': text or full_url.split('/')[-1],
                            'domain': domain,
                            'category': category,
                            'quality_score': round(score, 2),
                            'discovered_at': datetime.now().isoformat(),
                        }
                        self.resources.append(resource)
                        self.visited_urls.add(full_url)
                    
                    # Follow links to same domain
                    elif depth < max_depth:
                        link_domain = urllib.parse.urlparse(full_url).netloc
                        if '.gob.ec' in link_domain or '.edu.ec' in link_domain:
                            to_visit.append((full_url, depth + 1))
                
            except Exception as e:
                continue
            
            if len(self.resources) % 50 == 0 and len(self.resources) > 0:
                print(f"   📊 Discovered {len(self.resources)} resources...")
        
        print(f"\n✅ Discovery complete: {len(self.resources)} resources found")
    
    def analyze_registry(self):
        """Analyze and report on the registry"""
        print("\n" + "=" * 70)
        print("  📊 PHASE 2: ANALYZING REGISTRY")
        print("=" * 70)
        
        # Sort by quality score
        self.resources.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Category breakdown
        by_category = defaultdict(list)
        for r in self.resources:
            by_category[r['category']].append(r)
        
        print("\n📂 Resources by Category:")
        for cat, resources in sorted(by_category.items(), key=lambda x: -len(x[1])):
            high_quality = [r for r in resources if r['quality_score'] >= MIN_QUALITY_SCORE]
            print(f"   {cat}: {len(resources)} total, {len(high_quality)} high-quality")
        
        # Quality breakdown
        high_quality = [r for r in self.resources if r['quality_score'] >= MIN_QUALITY_SCORE]
        medium_quality = [r for r in self.resources if 0.4 <= r['quality_score'] < MIN_QUALITY_SCORE]
        low_quality = [r for r in self.resources if r['quality_score'] < 0.4]
        
        print(f"\n📈 Quality Breakdown:")
        print(f"   🌟 High (≥{MIN_QUALITY_SCORE}): {len(high_quality)}")
        print(f"   ⭐ Medium: {len(medium_quality)}")
        print(f"   ⚪ Low: {len(low_quality)}")
        
        # Top 10 resources
        print(f"\n🏆 TOP 10 HIGH-VALUE RESOURCES:")
        for i, r in enumerate(self.resources[:10], 1):
            print(f"   {i}. [{r['quality_score']:.2f}] {r['title'][:50]}...")
            print(f"      → {r['category']} | {r['domain']}")
        
        return high_quality
    
    def download_and_upload(self, resources):
        """Download only high-quality resources and upload to S3"""
        print("\n" + "=" * 70)
        print(f"  📥 PHASE 3: DOWNLOADING {len(resources)} HIGH-VALUE RESOURCES")
        print("=" * 70)
        
        uploaded = 0
        for i, resource in enumerate(resources[:MAX_RESOURCES_TO_DOWNLOAD], 1):
            url = resource['url']
            category = resource['category']
            filename = url.split('/')[-1]
            if not filename.endswith('.pdf'):
                filename = hashlib.md5(url.encode()).hexdigest()[:12] + '.pdf'
            
            print(f"\n[{i}/{min(len(resources), MAX_RESOURCES_TO_DOWNLOAD)}] {resource['title'][:40]}...")
            print(f"   Score: {resource['quality_score']} | Category: {category}")
            
            try:
                response = self.session.get(url, timeout=TIMEOUT, verify=False)
                if response.status_code == 200 and response.content[:4] == b'%PDF':
                    # Save to temp
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                        tmp.write(response.content)
                        tmp_path = tmp.name
                    
                    # Upload to S3
                    s3_path = f"{S3_BUCKET}/curated/{category}/{filename}"
                    result = subprocess.run(
                        ['aws', 's3', 'cp', tmp_path, s3_path, '--region', 'us-east-1'],
                        capture_output=True, text=True
                    )
                    os.unlink(tmp_path)  # Delete local file
                    
                    if result.returncode == 0:
                        print(f"   ✅ S3: curated/{category}/{filename}")
                        uploaded += 1
                    else:
                        print(f"   ❌ S3 upload failed")
                else:
                    print(f"   ⚠️ Not a valid PDF")
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:40]}")
        
        return uploaded
    
    def save_registry(self):
        """Save registry to file"""
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.resources, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Registry saved to {REGISTRY_FILE}")
    
    def run(self, seed_urls):
        """Full pipeline: discover → analyze → download"""
        # Phase 1: Discover
        self.discover_resources(seed_urls, max_depth=2)
        
        # Save registry
        self.save_registry()
        
        # Phase 2: Analyze
        high_quality = self.analyze_registry()
        
        # Phase 3: Download only high-quality
        if high_quality:
            uploaded = self.download_and_upload(high_quality)
            print(f"\n" + "=" * 70)
            print(f"  ✅ COMPLETE: {uploaded} high-value resources uploaded to S3")
            print("=" * 70)
        else:
            print("\n⚠️ No high-quality resources found to download")

# Seed URLs - authoritative sources
SEED_URLS = [
    "https://www.lexis.com.ec/biblioteca",
    "https://www.sri.gob.ec/normativa-tributaria",
    "https://portal.compraspublicas.gob.ec/sercop/normativa/",
    "https://www.supercias.gob.ec/portalscvs/",
    "https://www.trabajo.gob.ec/normativa/",
    "https://www.aduana.gob.ec/normativa-vigente/",
    "https://biblioteca.defensoria.gob.ec/",
]

if __name__ == "__main__":
    registry = ResourceRegistry()
    registry.run(SEED_URLS)
