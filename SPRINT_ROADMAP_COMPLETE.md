# YACHAQ-LEX Complete Sprint Roadmap
## 32 Government Sources + Training Pipeline

**Timeline:** 26 weeks (6 months)  
**Start Date:** 2025-10-18  
**Training Ready:** Week 26  
**Production:** Week 30

---

## SPRINT 0: Security & Infrastructure (Week 1-2)

### Critical Security Tasks
- [ ] Remove AWS credentials from `pipelines.py`
- [ ] Remove S3 references from `scrape_companies.py`
- [ ] Implement GCS storage with ADC
- [ ] Add `.env` support with `python-dotenv`
- [ ] Audit all code for secrets

### Development Environment
```bash
pip install selenium webdriver-manager
pip install beautifulsoup4 lxml html5lib
pip install pdfminer.six PyPDF2 pytesseract
pip install scrapy-rotating-proxies
pip install google-cloud-storage
```

### GCS Migration
- [ ] Create `rag/ingest/storage/gcs_client.py`
- [ ] Replace S3FilesPipeline with GCSFilesPipeline
- [ ] Test uploads to `yachaq-lex-raw-0017472631`
- [ ] Document bucket structure

**Deliverables:** Zero secrets, GCS operational, all tools installed

---

## SPRINT 1: Hybrid Framework (Week 3-4)

### Selenium Integration
```python
# rag/ingest/scrapers/selenium_middleware.py
# - SeleniumDownloaderMiddleware
# - Headless Chrome
# - Wait strategies
# - Screenshot debugging
```

### BeautifulSoup Parser
```python
# rag/ingest/parsers/bs4_parser.py
# - Robust HTML parsing
# - Fallback selectors
# - Text cleaning
# - Table extraction
```

### Hybrid Base Spider
```python
# rag/ingest/spiders/base_hybrid.py
# - Auto-detect static vs dynamic
# - Route to Scrapy or Selenium
# - BeautifulSoup post-processing
# - Exponential backoff retry
```

**Deliverables:** Selenium middleware, BS4 parser, hybrid base class, unit tests

---

## SPRINT 2: Registro Oficial Production (Week 5-6)

### Spider Enhancement
- [ ] Paginate https://www.registroficial.gob.ec/
- [ ] Extract: issue, date, supplement, PDF URL
- [ ] Download to `gs://yachaq-lex-raw-0017472631/raw/registro_oficial/{year}/{issue}.pdf`
- [ ] Generate JSONL metadata

### PDF Processing
- [ ] pdfminer.six for text
- [ ] Tesseract OCR for scans
- [ ] Extract article numbers
- [ ] Parse RO citations

### Orchestration
```python
# rag/ingest/run_registro_oficial.py
```

**Deliverables:** 5,000+ RO issues, PDF + metadata in GCS, orchestration script, tests

---

## SPRINT 3: High-Priority Ministries Batch 1 (Week 7-8)

### Entities (5)
1. **Ministerio de Salud Pública** (Selenium)
   - https://www.salud.gob.ec/
   - Health regulations, bulletins
   
2. **Ministerio de Economía y Finanzas** (Selenium)
   - https://www.finanzas.gob.ec/
   - Budget, fiscal reports
   
3. **Contraloría General del Estado** (Selenium)
   - https://www.contraloria.gob.ec/
   - Audit reports
   
4. **Procuraduría General del Estado** (Scrapy)
   - https://www.pge.gob.ec/
   - Legal opinions
   
5. **IESS** (Selenium)
   - https://www.iess.gob.ec/
   - Social security regulations

**Deliverables:** 5 new spiders, 2,000+ documents

---

## SPRINT 4: High-Priority Ministries Batch 2 (Week 9-10)

### Entities (5)
6. **Ministerio del Interior** (Selenium)
   - https://www.ministeriodelinterior.gob.ec/
   
7. **Ministerio de Gobierno** (Scrapy)
   - https://www.ministeriodegobierno.gob.ec/
   
8. **MPCEI - Producción** (Scrapy)
   - https://www.produccion.gob.ec/
   
9. **Presidencia** (Selenium)
   - https://www.presidencia.gob.ec/
   
10. **Secretaría de Planificación** (Scrapy)
    - https://www.planificacion.gob.ec/

**Deliverables:** 5 new spiders, 1,500+ documents

---

## SPRINT 5: Regulatory & Control (Week 11-12)

### Entities (5)
11. **ARCOTEL** (Scrapy)
    - https://www.arcotel.gob.ec/
    
12. **ANT** (Selenium)
    - https://www.ant.gob.ec/
    
13. **Defensoría del Pueblo** (Scrapy)
    - https://www.dpe.gob.ec/
    
14. **CNE** (Scrapy)
    - https://www.cne.gob.ec/
    
15. **TCE** (Scrapy)
    - https://www.tce.gob.ec/

**Deliverables:** 5 new spiders, 1,000+ documents

---

## SPRINT 6: Environment & Infrastructure (Week 13-14)

### Entities (4)
16. **MAATE - Ambiente** (Selenium)
    - https://www.ambiente.gob.ec/
    
17. **Ministerio de Agricultura** (Scrapy)
    - https://www.agricultura.gob.ec/
    
18. **Ministerio de Transporte** (Scrapy)
    - https://www.obraspublicas.gob.ec/
    
19. **Ministerio de Energía** (Scrapy)
    - https://www.recursosyenergia.gob.ec/

**Deliverables:** 4 new spiders, 800+ documents

---

## SPRINT 7: Social & Communication (Week 15-16)

### Entities (5)
20. **Ministerio de Inclusión Social** (Scrapy)
    - https://www.inclusion.gob.ec/
    
21. **Ministerio de Telecomunicaciones** (Selenium)
    - https://www.telecomunicaciones.gob.ec/
    
22. **Vicepresidencia** (Scrapy)
    - https://www.vicepresidencia.gob.ec/
    
23. **Secretaría de Comunicación** (Scrapy)
    - https://www.comunicacion.gob.ec/
    
24. **Ministerio de Turismo** (Scrapy)
    - https://www.turismo.gob.ec/

**Deliverables:** 5 new spiders, 600+ documents

---

## SPRINT 8: Defense & Foreign Affairs (Week 17-18)

### Entities (3)
25. **Ministerio de Defensa** (Scrapy)
    - https://www.defensa.gob.ec/
    
26. **Ministerio de Relaciones Exteriores** (Scrapy)
    - https://www.cancilleria.gob.ec/
    
27. **Policía Nacional** (Selenium)
    - Multiple domains

**Deliverables:** 3 new spiders, 500+ documents

---

## SPRINT 9: Public Enterprises (Week 19-20)

### Entities (4)
28. **EP Petroecuador** (Scrapy)
    - https://www.eppetroecuador.ec/
    
29. **CELEC EP** (Scrapy)
    - https://www.celec.gob.ec/
    
30. **CNEL EP** (Scrapy)
    - https://www.cnelep.gob.ec/
    
31. **CNT EP** (Scrapy)
    - https://www.cnt.com.ec/

**Deliverables:** 4 new spiders, 400+ documents

---

## SPRINT 10: PDF Processing Pipeline (Week 21-22)

### PDF Extraction
```python
# rag/ingest/parsers/pdf_parser.py
# - pdfminer.six for digital PDFs
# - Tesseract OCR for scans
# - Article extraction
# - Metadata parsing
```

### Batch Processing
- [ ] Process all 12,000+ downloaded PDFs
- [ ] Extract text + metadata
- [ ] Store in Parquet
- [ ] Upload to GCS

**Deliverables:** 12,000+ PDFs processed, OCR working, structured extraction

---

## SPRINT 11: Incremental Crawling (Week 23-24)

### Incremental Logic
- [ ] Track last crawl timestamp
- [ ] Hash-based change detection
- [ ] Skip unchanged documents
- [ ] Only download new/modified

### Monitoring
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Email alerts

### Scheduling
```bash
# Cron on ingest-runner VM
0 2 * * * run_registro_oficial.py --incremental
0 3 * * 1 run_sri_datasets.py
0 4 * * 1 run_senae_boletines.py
```

**Deliverables:** Incremental crawling, monitoring, automated schedules

---

## SPRINT 12: Corpus Assembly (Week 25-26)

### Statistics
- Total documents: ~15,000
- Total chunks: ~200,000
- Coverage: 32 government entities

### Instruction Dataset
```python
# rag/train/build_dataset.py
# Generate 80k-120k QA pairs
# Mix: 60% synthetic, 30% curated, 10% negative
```

### Training Prep
- [ ] Upload corpus to GCS
- [ ] Validate dataset format
- [ ] Wait for AWS GPU quota

**Deliverables:** 15,000+ docs, 200,000+ chunks, 100k instruction pairs, training ready

---

## SUCCESS METRICS

| Metric | Target | Sprint |
|--------|--------|--------|
| Documents | 15,000 | 12 |
| Entities | 32 | 9 |
| PDF Success | 95% | 10 |
| Crawl Success | 98% | 11 |
| Quality Score | 95% | 11 |
| Instruction Pairs | 100k | 12 |

---

## TECHNOLOGY STACK

```yaml
Scraping:
  - Scrapy: 18 entities
  - Selenium: 12 entities
  - BeautifulSoup: All entities
  - CKAN API: Datos Abiertos

Storage:
  - GCS: Raw + metadata
  - Qdrant: Vectors
  - Parquet: Structured

Processing:
  - pdfminer.six: PDF text
  - Tesseract: OCR
  - pandas: Transform

Monitoring:
  - Prometheus: Metrics
  - Grafana: Dashboards
```

---

**Next Action:** Start Sprint 0 security audit
