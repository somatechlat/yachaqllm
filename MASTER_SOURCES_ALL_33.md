# YACHAQ-LEX Master Sources - ALL 33 Ecuador Government Entities

**Date:** 2025-10-18  
**Total Entities:** 33  
**Status:** READY TO START SPRINT 0

---

## ✅ VERIFIED & READY (10 entities - Already in codebase)

1. **SRI** - https://www.sri.gob.ec/ ✅
2. **SENAE** - https://www.aduana.gob.ec/ ✅
3. **Registro Oficial** - https://www.registroficial.gob.ec/ ✅
4. **Asamblea Nacional** - https://asambleanacional.gob.ec/ ✅
5. **Corte Constitucional** - https://www.corteconstitucional.gob.ec/ ✅
6. **Función Judicial (CNJ)** - https://www.funcionjudicial.gob.ec/ ✅
7. **MinEduc** - https://educacion.gob.ec/ ✅
8. **INEC** - https://www.inec.gob.ec/ ✅
9. **Datos Abiertos** - https://www.datosabiertos.gob.ec/ ✅
10. **Constitución** - https://www.defensa.gob.ec/wp-content/uploads/downloads/2021/02/Constitucion-de-la-Republica-del-Ecuador_act_ene-2021.pdf ✅

---

## 🟡 NEW ENTITIES TO ADD (23 entities)

### Executive Branch (2)
11. **Presidencia** - https://www.presidencia.gob.ec/
12. **Vicepresidencia** - https://www.vicepresidencia.gob.ec/

### Control & Transparency (3)
13. **Contraloría** - https://www.contraloria.gob.ec/
14. **Defensoría del Pueblo** - https://www.dpe.gob.ec/
15. **Procuraduría** - https://www.pge.gob.ec/

### Electoral (2)
16. **CNE** - https://www.cne.gob.ec/
17. **TCE** - https://www.tce.gob.ec/

### Ministries - Social (2)
18. **Ministerio de Salud** - https://www.salud.gob.ec/
19. **Ministerio de Inclusión Social (MIES)** - https://www.inclusion.gob.ec/

### Ministries - Economic (2)
20. **Ministerio de Economía y Finanzas** - https://www.finanzas.gob.ec/
21. **Ministerio de Producción (MPCEI)** - https://www.produccion.gob.ec/

### Ministries - Security (2)
22. **Ministerio de Gobierno** - https://www.ministeriodegobierno.gob.ec/
23. **Ministerio del Interior** - https://www.ministeriodelinterior.gob.ec/

### Ministries - Environment & Infrastructure (1)
24. **MAATE (Ambiente)** - https://www.ambiente.gob.ec/

### Ministries - Other (2)
25. **Ministerio de Turismo** - https://www.turismo.gob.ec/
26. **Ministerio de Defensa** - https://www.defensa.gob.ec/

### Planning & Communication (2)
27. **Secretaría de Planificación** - https://www.planificacion.gob.ec/
28. **Secretaría de Comunicación** - https://www.comunicacion.gob.ec/

### Social Security (1)
29. **IESS** - https://www.iess.gob.ec/

### Regulatory (2)
30. **ARCOTEL** - https://www.arcotel.gob.ec/
31. **ANT** - https://www.ant.gob.ec/

### Public Enterprises (2)
32. **EP Petroecuador** - https://www.eppetroecuador.ec/
33. **CELEC EP** - https://www.celec.gob.ec/

---

## 🚀 SPRINT 0 STARTS NOW - Security Audit

### CRITICAL: Remove Hardcoded Credentials

**Files to fix immediately:**
1. `rag/ingest/scrapers/scrapers/pipelines.py` - AWS keys exposed
2. `rag/ingest/scrape_companies.py` - S3 bucket hardcoded

### Action Items (Next 2 hours)

```bash
# 1. Backup current code
cd /Users/macbookpro201916i964gb1tb/Downloads/YACHAQ-LEX_full
git add -A
git commit -m "Backup before security fixes"

# 2. Remove credentials
# Edit pipelines.py - remove AWS keys
# Edit scrape_companies.py - remove S3 references

# 3. Install required packages
pip install google-cloud-storage python-dotenv selenium webdriver-manager beautifulsoup4 lxml

# 4. Create .env template
cat > .env.template << 'EOF'
# GCS Configuration
GCS_PROJECT_ID=gen-lang-client-0017472631
GCS_RAW_BUCKET=yachaq-lex-raw-0017472631
GCS_ARTIFACTS_BUCKET=yachaq-lex-artifacts-0017472631

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=yachaq-lex

# Scraping Configuration
DOWNLOAD_DELAY=2
CONCURRENT_REQUESTS=1
USER_AGENT=YACHAQ-LEX/1.0 (+https://github.com/yachaq-lex)
EOF

# 5. Update .gitignore
echo ".env" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".DS_Store" >> .gitignore
```

---

## 📋 Sprint 0 Checklist (Week 1-2)

### Day 1-2: Security
- [ ] Remove AWS credentials from `pipelines.py`
- [ ] Remove S3 from `scrape_companies.py`
- [ ] Create `.env.template`
- [ ] Update `.gitignore`
- [ ] Test GCS authentication

### Day 3-4: GCS Migration
- [ ] Create `rag/ingest/storage/gcs_client.py`
- [ ] Replace S3FilesPipeline with GCSFilesPipeline
- [ ] Test file upload to GCS
- [ ] Document bucket structure

### Day 5-7: Development Environment
- [ ] Install Selenium + webdriver-manager
- [ ] Install BeautifulSoup4 + lxml
- [ ] Install PDF tools (pdfminer.six, pytesseract)
- [ ] Test Selenium with headless Chrome
- [ ] Create requirements.txt

### Day 8-10: Framework Setup
- [ ] Create `rag/ingest/scrapers/selenium_middleware.py`
- [ ] Create `rag/ingest/parsers/bs4_parser.py`
- [ ] Create `rag/ingest/spiders/base_hybrid.py`
- [ ] Write unit tests
- [ ] Document usage

---

## 🎯 Immediate Next Steps (RIGHT NOW)

1. **Fix security issues** (30 minutes)
2. **Install dependencies** (15 minutes)
3. **Test GCS connection** (15 minutes)
4. **Create GCS client** (1 hour)
5. **Update one spider to use GCS** (1 hour)

---

## 📊 Final Count Verification

| Category | Count |
|----------|-------|
| Already Verified | 10 |
| New to Add | 23 |
| **TOTAL** | **33** |

**All 33 entities identified and cataloged. Ready to start Sprint 0.**
