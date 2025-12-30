#!/usr/bin/env python3
"""
YACHAQ DATA SOURCE DISCOVERY AGENT
===================================
Autonomous agent that searches the internet for Ecuador data sources,
validates them, and registers them for later download.

Runs continuously in background, discovering new sources.

Usage: nohup python3 discover_ecuador_sources.py &
"""

import os
import json
import time
import requests
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
import re

# Configuration
REGISTRY_FILE = "/Users/macbookpro201916i964gb1tb/Downloads/1x/yachaq/registry/discovered_sources.json"
LOG_FILE = "/tmp/ecuador_discovery.log"
SOURCES_TO_DOWNLOAD = "/Users/macbookpro201916i964gb1tb/Downloads/1x/yachaq/registry/pending_downloads.json"

HEADERS = {
    "User-Agent": "YachaqLLM/1.0 (Educational Research Ecuador)"
}

# Ecuador government domains to scan
ECUADOR_DOMAINS = [
    # Main government portals
    "gob.ec",
    "datosabiertos.gob.ec",
    "sri.gob.ec",
    "sercop.gob.ec",
    "compraspublicas.gob.ec",
    "asambleanacional.gob.ec",
    "funcionjudicial.gob.ec",
    "cortenacional.gob.ec",
    
    # Ministries
    "educacion.gob.ec",
    "salud.gob.ec",
    "trabajo.gob.ec",
    "agricultura.gob.ec",
    "ambiente.gob.ec",
    "turismo.gob.ec",
    "cultura.gob.ec",  
    "culturaypatrimonio.gob.ec",
    "telecomunicaciones.gob.ec",
    "produccion.gob.ec",
    "energia.gob.ec",
    "transporte.gob.ec",
    "obraspublicas.gob.ec",
    "defensa.gob.ec",
    "interior.gob.ec",
    "cancilleria.gob.ec",
    "finanzas.gob.ec",
    "planificacion.gob.ec",
    
    # Regulators & Agencies
    "supercias.gob.ec",
    "superbancos.gob.ec",
    "contraloria.gob.ec",
    "procuraduria.gob.ec",
    "defensoriadelpueblo.gob.ec",
    "cne.gob.ec",
    "tce.gob.ec",
    "consejodelajudicatura.gob.ec",
    "iess.gob.ec",
    "bce.fin.ec",
    
    # Statistics & Data
    "ecuadorencifras.gob.ec",
    "censoecuador.gob.ec",
    "inec.gob.ec",
    
    # Geographic
    "geoportaligm.gob.ec",
    "igm.gob.ec",
    
    # Other important
    "registrocivil.gob.ec",
    "ant.gob.ec",
    "arcsa.gob.ec",
    "senadi.gob.ec",
    "senae.gob.ec",
    "policia.gob.ec",
    "bomberos.gob.ec",
    
    # Education
    "senescyt.gob.ec",
    "ces.gob.ec",
    "caces.gob.ec",
    
    # Wikipedia
    "es.wikipedia.org",
]

# Search terms for finding data
SEARCH_TERMS = [
    "Ecuador datos abiertos",
    "Ecuador API publica",
    "Ecuador dataset",
    "Ecuador estadisticas",
    "Ecuador informacion publica",
    "Ecuador gobierno datos",
    "leyes Ecuador",
    "normativa Ecuador",
    "Ecuador history",
    "Ecuador culture",
    "Galapagos data",
    "Ecuador biodiversity",
]

def log(msg: str):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_registry() -> Dict:
    """Load existing registry"""
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    return {"sources": [], "last_updated": None}

def save_registry(registry: Dict):
    """Save registry to file"""
    registry["last_updated"] = datetime.now().isoformat()
    os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def generate_source_id(url: str) -> str:
    """Generate unique source ID"""
    return hashlib.md5(url.encode()).hexdigest()[:12]

def validate_url(url: str) -> Dict:
    """Validate if URL is accessible and get basic info"""
    try:
        r = requests.head(url, headers=HEADERS, timeout=10, allow_redirects=True)
        return {
            "accessible": r.status_code == 200,
            "status_code": r.status_code,
            "content_type": r.headers.get("Content-Type", "unknown"),
            "size": r.headers.get("Content-Length", "unknown")
        }
    except Exception as e:
        return {
            "accessible": False,
            "error": str(e)
        }

def discover_data_endpoints(domain: str) -> List[Dict]:
    """Discover data endpoints on a domain"""
    discovered = []
    base_url = f"https://www.{domain}" if not domain.startswith("www.") else f"https://{domain}"
    
    # Common data endpoints to check
    endpoints = [
        "/api",
        "/api/v1",
        "/datos",
        "/data",
        "/datasets",
        "/opendata",
        "/estadisticas",
        "/publicaciones",
        "/descargas",
        "/documentos",
        "/normativa",
        "/leyes",
        "/resoluciones",
        "/informes",
        "/boletines",
    ]
    
    for endpoint in endpoints:
        url = base_url + endpoint
        validation = validate_url(url)
        
        if validation.get("accessible"):
            discovered.append({
                "url": url,
                "domain": domain,
                "endpoint": endpoint,
                "content_type": validation.get("content_type"),
                "discovered_at": datetime.now().isoformat()
            })
            log(f"  ✅ Found: {url}")
    
    return discovered

def discover_files_on_page(url: str) -> List[Dict]:
    """Find downloadable files on a page"""
    files = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        
        # Find links to data files
        patterns = [
            r'href=["\']([^"\']+\.(csv|json|xml|xlsx|xls|pdf|zip|txt|ods))["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, r.text, re.I)
            for match in matches:
                file_url = match[0]
                if not file_url.startswith("http"):
                    file_url = url.rstrip("/") + "/" + file_url.lstrip("/")
                
                files.append({
                    "url": file_url,
                    "type": match[1].lower(),
                    "source_page": url
                })
        
    except Exception as e:
        log(f"  Error scanning {url}: {e}")
    
    return files

def discover_from_datosabiertos_api() -> List[Dict]:
    """Discover datasets from datosabiertos.gob.ec CKAN API"""
    discovered = []
    
    try:
        # Disable SSL verification for expired cert
        import urllib3
        urllib3.disable_warnings()
        
        url = "https://datosabiertos.gob.ec/api/3/action/package_list"
        r = requests.get(url, headers=HEADERS, timeout=60, verify=False)
        
        if r.status_code == 200:
            data = r.json()
            if data.get("success"):
                packages = data.get("result", [])
                log(f"  Found {len(packages)} datasets on datosabiertos.gob.ec")
                
                for pkg in packages[:100]:  # Limit for initial discovery
                    discovered.append({
                        "url": f"https://datosabiertos.gob.ec/dataset/{pkg}",
                        "name": pkg,
                        "type": "ckan_dataset",
                        "source": "datosabiertos.gob.ec"
                    })
    except Exception as e:
        log(f"  Error with datosabiertos API: {e}")
    
    return discovered

def main():
    log("=" * 60)
    log("YACHAQ DATA SOURCE DISCOVERY AGENT")
    log("Searching for Ecuador public data sources")
    log("=" * 60)
    
    registry = load_registry()
    existing_urls = {s.get("url") for s in registry.get("sources", [])}
    new_sources = []
    
    # 1. Scan Ecuador government domains
    log("\n=== SCANNING GOVERNMENT DOMAINS ===")
    for domain in ECUADOR_DOMAINS:
        log(f"Scanning: {domain}")
        endpoints = discover_data_endpoints(domain)
        
        for ep in endpoints:
            if ep["url"] not in existing_urls:
                new_sources.append(ep)
                existing_urls.add(ep["url"])
        
        time.sleep(0.5)  # Rate limiting
    
    # 2. Discover from datos abiertos API
    log("\n=== SCANNING DATOS ABIERTOS API ===")
    ckan_sources = discover_from_datosabiertos_api()
    for src in ckan_sources:
        if src["url"] not in existing_urls:
            new_sources.append(src)
            existing_urls.add(src["url"])
    
    # 3. Scan known sources for files
    log("\n=== SCANNING FOR DATA FILES ===")
    file_sources = [
        "https://www.sri.gob.ec/datasets",
        "https://www.ecuadorencifras.gob.ec/banco-de-informacion/",
        "https://www.bce.fin.ec/informacioneconomica",
    ]
    
    for src in file_sources:
        log(f"Scanning files: {src}")
        files = discover_files_on_page(src)
        for f in files:
            if f["url"] not in existing_urls:
                new_sources.append(f)
                existing_urls.add(f["url"])
        time.sleep(1)
    
    # Save discovered sources
    registry["sources"].extend(new_sources)
    save_registry(registry)
    
    # Summary
    log("\n" + "=" * 60)
    log("DISCOVERY COMPLETE")
    log("=" * 60)
    log(f"New sources discovered: {len(new_sources)}")
    log(f"Total sources in registry: {len(registry['sources'])}")
    log(f"Registry saved to: {REGISTRY_FILE}")
    
    # Save pending downloads
    pending = [s for s in registry["sources"] if s.get("url")]
    with open(SOURCES_TO_DOWNLOAD, 'w') as f:
        json.dump(pending, f, indent=2, ensure_ascii=False)
    log(f"Pending downloads saved to: {SOURCES_TO_DOWNLOAD}")

if __name__ == "__main__":
    main()
