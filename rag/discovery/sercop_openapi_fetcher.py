#!/usr/bin/env python3
"""
Simple SERCOP open-api fetcher + portal-detail fallback.

Usage: python3 rag/discovery/sercop_openapi_fetcher.py 
It expects an input search page JSON at rag/discovery/out_openapi/sample_search_2024_software_page1.json
and will write results to rag/discovery/out_openapi/dryrun_<timestamp>/
"""
import requests
import json
import os
import sys
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from hashlib import sha256

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT_DIR = os.path.join(ROOT, 'out_openapi')
os.makedirs(OUT_DIR, exist_ok=True)

def load_search_page(path):
    return json.load(open(path, 'r', encoding='utf-8'))

def fetch_record(ocid):
    url = 'https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/record'
    r = requests.get(url, params={'ocid': ocid}, headers={'Accept':'application/json'}, timeout=30)
    r.raise_for_status()
    return r.json(), r.url

def try_portal_detail(ocid, candidate_ids):
    """Try several candidate portal detail URL patterns and save the first successful HTML."""
    base = 'https://portal.compraspublicas.gob.ec/sercop/'
    candidates = []
    # common paths observed
    for cid in candidate_ids:
        candidates.append(urljoin(base, f'ProcesoContratacion/informacionProcesoContratacion.cpe?ocid={cid}'))
        candidates.append(urljoin(base, f'ProcesoContratacion/informacionProcesoContratacion.cpe?id={cid}'))
        candidates.append(urljoin(base, f'ProcesoContratacion/informacionProcesoContratacion2.cpe?ocid={cid}'))
        candidates.append(urljoin(base, f'ProcesoContratacion/informacionProcesoContratacion2.cpe?id={cid}'))
        candidates.append(urljoin(base, f'ProcesoContratacion/informacionProcesoContratacion.cpe?codproc={cid}'))
    session = requests.Session()
    headers = {'User-Agent':'yachaq-llm-fetcher/1.0'}
    for url in candidates:
        try:
            r = session.get(url, headers=headers, timeout=30)
        except Exception:
            continue
        if r.status_code == 200 and len(r.text) > 1000:
            return {'portal_url': url, 'html': r.text, 'fetched_url': r.url}
    return None

def find_attachment_links_from_html(html, base_url='https://portal.compraspublicas.gob.ec'):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a'):
        href = a.get('href')
        txt = (a.get_text() or '').strip()
        if not href:
            continue
        full = urljoin(base_url, href)
        if href.lower().endswith('.pdf') or 'Descargar' in txt or 'archivo' in txt.lower() or 'document' in href.lower():
            links.append({'text': txt, 'href': full})
    # also look for inputs or onclicks with pdf
    for tag in soup.find_all(attrs={'onclick': True}):
        onclick = tag['onclick']
        # crude extract of url inside parentheses
        import re
        m = re.search(r"(https?://[^\'\"\)\s]+\.pdf)", onclick)
        if m:
            links.append({'text': 'onclick', 'href': m.group(1)})
    # dedupe
    seen=set()
    out=[]
    for l in links:
        if l['href'] in seen: continue
        seen.add(l['href'])
        out.append(l)
    return out

def download_file(url, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    local_name = os.path.join(out_dir, url.split('/')[-1].split('?')[0])
    try:
        r = requests.get(url, stream=True, timeout=60)
    except Exception as e:
        return None, str(e)
    if r.status_code != 200:
        return None, f'status={r.status_code}'
    with open(local_name, 'wb') as f:
        for chunk in r.iter_content(1024*16):
            if chunk:
                f.write(chunk)
    h = sha256()
    with open(local_name, 'rb') as f:
        while True:
            b = f.read(8192)
            if not b: break
            h.update(b)
    return {'path': local_name, 'sha256': h.hexdigest()}, None

def build_canonical(record_json, ocid, search_item, portal_info=None, attachments=None, artifacts_dir=None):
    obj = {}
    obj['basic_id'] = search_item.get('title') or search_item.get('id')
    obj['ocid'] = ocid
    obj['source_index'] = {'source':'search_ocds','page':search_item.get('_page',1),'index':search_item.get('_index',0)}
    obj['canonical_metadata'] = record_json
    if portal_info:
        obj['portal_detail'] = {'portal_url': portal_info.get('portal_url'), 'saved_html_path': portal_info.get('saved_html_path')}
    obj['attachments_list'] = attachments or []
    obj['provenance'] = {'record_json_path': artifacts_dir and os.path.join(artifacts_dir, 'record.json')}
    obj['validation_flags'] = {'documents_complete': bool(obj['attachments_list'])}
    return obj

def dryrun_from_search(search_json_path, limit=10):
    search = load_search_page(search_json_path)
    data = search.get('data', [])
    run_id = int(time.time())
    out_run = os.path.join(OUT_DIR, f'dryrun_{run_id}')
    os.makedirs(out_run, exist_ok=True)
    results_file = os.path.join(out_run, 'results.jsonl')
    attachments_dir = os.path.join(out_run, 'attachments')
    with open(results_file, 'w', encoding='utf-8') as outf:
        for i,item in enumerate(data[:limit]):
            ocid = item.get('ocid')
            print(f'[{i+1}] processing ocid={ocid}')
            rec_json = None
            try:
                rec_json, fetched_url = fetch_record(ocid)
                # save record json
                rec_path = os.path.join(out_run, f'record_{i+1}.json')
                with open(rec_path, 'w', encoding='utf-8') as f:
                    json.dump(rec_json, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(' record fetch failed:', e)
                rec_json = None
                rec_path = None

            # try portal detail by testing candidate patterns using ocid and id
            candidate_ids = [ocid, str(item.get('id'))]
            portal = try_portal_detail(ocid, candidate_ids)
            portal_info = None
            attachments = []
            if portal:
                # save html
                html_path = os.path.join(out_run, f'portal_{i+1}.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(portal['html'])
                portal['saved_html_path'] = html_path
                portal_info = portal
                # scan for links
                links = find_attachment_links_from_html(portal['html'], base_url=portal.get('portal_url'))
                print('  found', len(links), 'candidate links in portal HTML')
                # download up to 5
                for idx,l in enumerate(links[:5]):
                    dl_res, err = download_file(l['href'], attachments_dir)
                    if dl_res:
                        attachments.append({'title': l.get('text'), 'url': l.get('href'), 'downloaded': dl_res})
                    else:
                        attachments.append({'title': l.get('text'), 'url': l.get('href'), 'error': err})
            else:
                print('  no portal HTML found for ocid')

            canonical = build_canonical(rec_json, ocid, item, portal_info=portal_info, attachments=attachments, artifacts_dir=out_run)
            outf.write(json.dumps(canonical, ensure_ascii=False) + '\n')
    print('dryrun saved to', out_run)
    return out_run

if __name__ == '__main__':
    # default input path
    inp = os.path.join(OUT_DIR, 'sample_search_2024_software_page1.json')
    if len(sys.argv) > 1:
        inp = sys.argv[1]
    if not os.path.exists(inp):
        print('Input search JSON not found:', inp); sys.exit(2)
    out = dryrun_from_search(inp, limit=10)
    print('Done. outputs in', out)
