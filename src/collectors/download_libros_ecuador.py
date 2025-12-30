#!/usr/bin/env python3
"""
YACHAQ ECUADOR BOOKS & LITERATURE COLLECTOR
============================================
Download public domain Ecuadorian books and literature

Sources:
- Project Gutenberg (public domain)
- Internet Archive (archive.org)
- Biblioteca Nacional del Ecuador (digital)
- Casa de la Cultura Ecuatoriana
"""

import os
import json
import time
import requests
from datetime import datetime
import subprocess
import re

S3_BUCKET = "s3://yachaq-lex-raw-0017472631"
S3_PREFIX = "libros_ecuador"
LOCAL_TEMP = "/tmp/libros_ecuador"
LOG_FILE = "/tmp/libros_ecuador_download.log"

# Ecuadorian Authors (Public Domain)
ECUADORIAN_AUTHORS = [
    "Juan Montalvo",
    "Juan León Mera",
    "José Joaquín de Olmedo",
    "Eugenio Espejo",
    "Dolores Veintimilla",
    "Medardo Ángel Silva",
    "Gonzalo Zaldumbide",
    "Jorge Icaza",
    "Pablo Palacio",
]

# Known Public Domain Works
WORKS = {
    "Cumandá": {"author": "Juan León Mera", "year": 1879},
    "Huasipungo": {"author": "Jorge Icaza", "year": 1934},
    "Las Catilinarias": {"author": "Juan Montalvo", "year": 1880},
    "La Emancipada": {"author": "Miguel Riofrío", "year": 1863},
    "Siete Tratados": {"author": "Juan Montalvo", "year": 1882},
}

HEADERS = {
    "User-Agent": "YachaqLLM/1.0 (Educational Research)"
}

os.makedirs(LOCAL_TEMP, exist_ok=True)

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def search_gutenberg(query):
    """Search Project Gutenberg for works"""
    url = f"https://gutendex.com/books/?search={query}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception as e:
        log(f"Gutenberg search error: {e}")
        return []

def download_gutenberg_text(book_id):
    """Download text from Project Gutenberg"""
    url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
        if r.status_code == 200:
            return r.text
    except:
        pass
    
    # Try alternative URL
    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
        if r.status_code == 200:
            return r.text
    except:
        pass
    return None

def search_internet_archive(query):
    """Search Internet Archive for Ecuadorian texts"""
    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": f'{query} AND mediatype:texts',
        "fl[]": ["identifier", "title", "creator", "date"],
        "rows": 50,
        "output": "json"
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.json().get("response", {}).get("docs", [])
    except Exception as e:
        log(f"Archive.org search error: {e}")
        return []

def download_archive_text(identifier):
    """Download text from Internet Archive"""
    # Get metadata
    meta_url = f"https://archive.org/metadata/{identifier}"
    try:
        r = requests.get(meta_url, headers=HEADERS, timeout=30)
        meta = r.json()
        
        # Find text file
        for f in meta.get("files", []):
            if f.get("name", "").endswith(".txt"):
                txt_url = f"https://archive.org/download/{identifier}/{f['name']}"
                r = requests.get(txt_url, headers=HEADERS, timeout=120)
                if r.status_code == 200:
                    return r.text
    except Exception as e:
        log(f"Archive download error: {e}")
    return None

def save_to_s3(content, filename, metadata):
    """Save content to S3 with metadata"""
    local_path = os.path.join(LOCAL_TEMP, filename)
    s3_path = f"{S3_BUCKET}/{S3_PREFIX}/{filename}"
    
    # Save with metadata header
    with open(local_path, 'w', encoding='utf-8') as f:
        f.write(f"# METADATA\n")
        f.write(f"# Title: {metadata.get('title', 'Unknown')}\n")
        f.write(f"# Author: {metadata.get('author', 'Unknown')}\n")
        f.write(f"# Source: {metadata.get('source', 'Unknown')}\n")
        f.write(f"# License: Public Domain\n")
        f.write(f"# Collected: {datetime.now().isoformat()}\n")
        f.write(f"# ---\n\n")
        f.write(content)
    
    size = os.path.getsize(local_path)
    log(f"  Saving: {filename} ({size/1024:.1f} KB)")
    
    subprocess.run(["aws", "s3", "cp", local_path, s3_path], check=True)
    os.remove(local_path)
    return True

def main():
    log("=" * 60)
    log("YACHAQ LIBROS ECUADOR COLLECTOR")
    log("Literature & Books - Public Domain")
    log("=" * 60)
    
    collected = 0
    
    # Search for Ecuadorian authors on Gutenberg
    log("\n=== PROJECT GUTENBERG ===")
    for author in ECUADORIAN_AUTHORS:
        log(f"Searching: {author}")
        books = search_gutenberg(author)
        for book in books:
            title = book.get("title", "Unknown")
            book_id = book.get("id")
            log(f"  Found: {title} (ID: {book_id})")
            
            text = download_gutenberg_text(book_id)
            if text and len(text) > 1000:
                filename = f"gutenberg_{book_id}_{author.replace(' ', '_')}.txt"
                save_to_s3(text, filename, {
                    "title": title,
                    "author": author,
                    "source": "Project Gutenberg"
                })
                collected += 1
            time.sleep(1)
    
    # Search Internet Archive for Ecuador
    log("\n=== INTERNET ARCHIVE ===")
    archive_searches = [
        "Ecuador historia",
        "literatura ecuatoriana",
        "Juan Montalvo",
        "Juan León Mera",
        "poesía ecuatoriana",
    ]
    
    for query in archive_searches:
        log(f"Searching: {query}")
        docs = search_internet_archive(query)
        for doc in docs[:5]:  # Limit per query
            identifier = doc.get("identifier")
            title = doc.get("title", "Unknown")
            log(f"  Found: {title}")
            
            text = download_archive_text(identifier)
            if text and len(text) > 1000:
                filename = f"archive_{identifier[:30]}.txt"
                save_to_s3(text, filename, {
                    "title": title,
                    "author": doc.get("creator", "Unknown"),
                    "source": "Internet Archive"
                })
                collected += 1
            time.sleep(1)
    
    log("\n" + "=" * 60)
    log(f"LIBROS COLLECTED: {collected}")
    log("=" * 60)

if __name__ == "__main__":
    main()
