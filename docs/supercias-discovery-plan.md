# SUPERCIAS Data Harvesting - Discovery & Implementation Plan

**Target:** Superintendencia de Compañías, Valores y Seguros (SUPERCIAS)  
**Goal:** Extract ALL company data for LLM training  
**Date:** 2025  
**Status:** PLANNING PHASE

---

## 🎯 DISCOVERED DATA SOURCES

### **PRIMARY PORTALS** (22 endpoints discovered)

#### 1. **Company Search & Information**
- `https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf`
  - **Type:** JSF/PrimeFaces application
  - **Search by:** Expediente (file number), RUC, Company Name
  - **Has Captcha:** YES (dynamically loaded)
  - **Auth Required:** NO (public)
  - **Data:** Company registry, legal status, financial info

#### 2. **Financial Statements by Sector**
- `https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/estadosFinancierosPorRamo.jsf`
  - **Data:** Balance sheets, income statements by industry sector
  - **Format:** Likely tabular/downloadable

#### 3. **Corporate Investment**
- `https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/inversionSocietaria.jsf`
  - **Data:** Shareholding structures, corporate investments

#### 4. **Company Directory**
- `https://mercadodevalores.supercias.gob.ec/reportes/directorioCompanias.jsf`
  - **Data:** Complete directory of registered companies
  - **Potential:** Bulk export capability

#### 5. **Company Rankings**
- `https://appscvsmovil.supercias.gob.ec/ranking/reporte.html`
  - **Data:** Company rankings by revenue, assets, sector

#### 6. **Company Statistics**
- `https://appscvsmovil.supercias.gob.ec/portaldeinformacion/reporteCias.zul`
  - **Data:** Statistical reports on companies

#### 7. **Foreign Companies**
- `https://mercadodevalores.supercias.gob.ec/reportes/companiasExtranjeras.jsf`
- `https://mercadodevalores.supercias.gob.ec/sociedadesextranjeras/consultaPortalInformacion.jsf`
  - **Data:** Foreign companies operating in Ecuador

#### 8. **Mixed Economy Companies**
- `https://mercadodevalores.supercias.gob.ec/reportes/companiasEconomiaMixta.jsf`
  - **Data:** Public-private partnerships

#### 9. **External Auditors**
- `https://mercadodevalores.supercias.gob.ec/reportes/auditoresExternos.jsf`
  - **Data:** Registered auditors and their clients

#### 10. **Certified Appraisers**
- `https://appscvsmovil.supercias.gob.ec/portaldeinformacion/peritos_calificados.zul`
  - **Data:** Qualified appraisers registry

#### 11. **Share Transfers/Assignments**
- `https://appscvsmovil.supercias.gob.ec/portaldeinformacion/consulta_transf_ces_acciones.zul`
  - **Data:** Stock transfer records

#### 12. **Company Publications/Extracts**
- `https://publico.supercias.gob.ec/publicacionesCompanias/menuPublicaciones.jsf`
  - **Data:** Official company publications, legal notices

#### 13. **Name Reservations**
- `https://appscvs1.supercias.gob.ec/reservaDenominacion/consultar_reserva.zul`
- `https://appscvs1.supercias.gob.ec/reservaDenominacion/consulta_denominaciones.zul`
  - **Data:** Reserved company names

#### 14. **Person/Shareholder Lookup**
- `https://appscvs1.supercias.gob.ec/consultaPersona/consulta_cia_param.zul`
- `https://appscvs1.supercias.gob.ec/consultaPersona/consulta_noacc_param.zul`
  - **Data:** Individual shareholders, directors, legal representatives

#### 15. **Certificate Verification**
- `https://appscvsmovil.supercias.gob.ec/portaldeinformacion/verificar_certificado.zul`
  - **Data:** Verify authenticity of issued certificates

#### 16. **Procedures Portal**
- `https://iib.supercias.gob.ec/PortalTramitesSCVS/inicio_st.zul`
  - **Data:** Administrative procedures, requirements

#### 17. **Documentation (PDF)**
- `https://reporteria.supercias.gob.ec/portal/files/Presentacion_Consultas_Societarias.pdf`
  - **Data:** User guides, query documentation

---

## 🔍 TECHNICAL ANALYSIS

### **Technology Stack Detected:**

1. **JSF (JavaServer Faces) + PrimeFaces 6.2**
   - Modern Java web framework
   - AJAX-heavy interactions
   - ViewState management (stateful)

2. **ZK Framework**
   - `.zul` files = ZK UI markup
   - Event-driven architecture
   - Server-side rendering

3. **Session Management:**
   - `JSESSIONID` cookies
   - `javax.faces.ViewState` tokens
   - Must maintain session across requests

4. **Captcha System:**
   - Dynamically loaded via AJAX
   - Panel ID: `frmBusquedaCompanias:panelCaptcha`
   - Triggered after company selection

---

## 🚧 CHALLENGES IDENTIFIED

### **1. Captcha Enforcement**
- ✅ **Confirmed:** Captcha required for company searches
- **Location:** Loaded dynamically into `panelCaptcha`
- **Trigger:** After selecting a company from autocomplete
- **Solution:** Same as SERCOP - human-in-the-loop queue

### **2. Stateful Sessions**
- JSF ViewState must be preserved
- Each interaction updates ViewState
- Cannot parallelize without session isolation

### **3. AJAX Complexity**
- PrimeFaces uses complex AJAX calls
- Must reverse-engineer `PrimeFaces.ab()` calls
- Network inspection required for each endpoint

### **4. Authentication (Some Endpoints)**
- Some portals may require login
- Need to verify which are public vs. authenticated

---

## 📋 IMPLEMENTATION PLAN (KANBAN)

### **PHASE 1: RECONNAISSANCE** ✅ DONE
- [x] Discover all Supercias portals
- [x] Identify data sources
- [x] Analyze technology stack
- [x] Document captcha requirements

### **PHASE 2: PROTOTYPE (Week 1-2)**
- [ ] **Task 2.1:** Create `supercias_cdp_discovery.py`
  - Copy SERCOP's Pydoll/CDP architecture
  - Adapt for JSF/PrimeFaces
  - Capture ViewState tokens
  
- [ ] **Task 2.2:** Implement session management
  - Handle JSESSIONID cookies
  - Preserve ViewState across requests
  - Test session persistence

- [ ] **Task 2.3:** Captcha detection & queuing
  - Detect captcha panel loading
  - Extract captcha image
  - Queue for human solving (reuse SERCOP queue)

- [ ] **Task 2.4:** Test single company lookup
  - Search by RUC (simplest)
  - Solve captcha manually
  - Extract company detail page
  - Validate data extraction

### **PHASE 3: CORE HARVESTER (Week 3-4)**
- [ ] **Task 3.1:** Build `supercias_harvester.py`
  - Main orchestration script
  - Based on `sercop_cdp_harvester.py` pattern
  
- [ ] **Task 3.2:** Implement search strategies
  - **Strategy A:** RUC enumeration (if feasible)
  - **Strategy B:** Name-based search with pagination
  - **Strategy C:** Directory bulk export (if available)

- [ ] **Task 3.3:** Detail page scraping
  - Parse company information
  - Extract financial statements
  - Download attached documents
  - Handle multiple tabs/sections

- [ ] **Task 3.4:** Pagination handling
  - Detect result pagination
  - Navigate through pages
  - Track progress

### **PHASE 4: MULTI-SOURCE INTEGRATION (Week 5-6)**
- [ ] **Task 4.1:** Financial statements harvester
  - Target: `estadosFinancierosPorRamo.jsf`
  - Extract by sector/year
  
- [ ] **Task 4.2:** Directory harvester
  - Target: `directorioCompanias.jsf`
  - Bulk company list extraction

- [ ] **Task 4.3:** Rankings harvester
  - Target: `ranking/reporte.html`
  - Extract ranking data

- [ ] **Task 4.4:** Publications harvester
  - Target: `publicacionesCompanias`
  - Download legal notices, extracts

- [ ] **Task 4.5:** Foreign companies harvester
  - Target: `companiasExtranjeras.jsf`
  - Separate pipeline for foreign entities

### **PHASE 5: SCALE & OPTIMIZE (Week 7-8)**
- [ ] **Task 5.1:** Implement rate limiting
  - Respect server load
  - Human-like pacing
  
- [ ] **Task 5.2:** Error handling & retry logic
  - Session expiry recovery
  - Network failure handling
  - Captcha failure retry

- [ ] **Task 5.3:** Progress tracking
  - Database of scraped companies
  - Deduplication
  - Resume capability

- [ ] **Task 5.4:** S3 integration
  - Stream data to S3
  - Organize by source/date
  - Metadata tagging

### **PHASE 6: VALIDATION & DEPLOYMENT (Week 9-10)**
- [ ] **Task 6.1:** Data quality validation
  - Completeness checks
  - Format validation
  - Sample audits

- [ ] **Task 6.2:** Documentation
  - API documentation
  - Runbook creation
  - Troubleshooting guide

- [ ] **Task 6.3:** Monitoring setup
  - CloudWatch metrics
  - Alert configuration
  - Dashboard creation

- [ ] **Task 6.4:** Production deployment
  - Schedule automated runs
  - Set up captcha solving workflow
  - Monitor first production run

---

## 🎯 DATA VOLUME ESTIMATES

Based on Ecuador's business registry:
- **Active Companies:** ~500,000+
- **Financial Statements:** Multiple years per company
- **Documents per Company:** 5-20 (avg)
- **Total Documents:** 2.5M - 10M files

**Storage Estimate:** 500GB - 2TB (compressed)

---

## 🔧 TECHNICAL APPROACH

### **Architecture (Based on SERCOP Pattern):**

```
┌─────────────────────────────────────────────────┐
│  supercias_harvester.py (Main Orchestrator)    │
└─────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────────┐   ┌──────────────────┐
│ Pydoll/CDP       │   │ Captcha Queue    │
│ Discovery        │   │ (Human Solver)   │
└──────────────────┘   └──────────────────┘
        │                       │
        └───────────┬───────────┘
                    ▼
        ┌───────────────────────┐
        │  BeautifulSoup        │
        │  HTML Parser          │
        └───────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────────┐   ┌──────────────────┐
│ Crawl4AI         │   │ Document         │
│ Post-processor   │   │ Downloader       │
└──────────────────┘   └──────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  S3 Storage           │
        │  yachaq-lex-raw-*     │
        └───────────────────────┘
```

### **Key Components:**

1. **`supercias_cdp_discovery.py`**
   - Pydoll/CDP wrapper for JSF apps
   - ViewState extraction
   - Session management

2. **`supercias_harvester.py`**
   - Main harvesting logic
   - Multi-source coordination
   - Progress tracking

3. **`supercias_captcha_queue.py`**
   - Reuse SERCOP's queue system
   - Adapt for Supercias captcha format

4. **`supercias_parsers.py`**
   - Company detail parser
   - Financial statement parser
   - Document link extractor

---

## ⚠️ CRITICAL REQUIREMENTS

### **Before Starting:**
1. ✅ Confirm if login credentials are needed
2. ✅ Test captcha solving workflow
3. ✅ Verify rate limits (if any)
4. ✅ Check robots.txt compliance

### **During Development:**
1. Test with small batches (10-50 companies)
2. Validate data quality continuously
3. Monitor for IP blocking
4. Keep human solver available for captchas

---

## 📊 SUCCESS METRICS

- **Coverage:** >95% of active companies
- **Data Quality:** <2% parsing errors
- **Completeness:** All available documents downloaded
- **Performance:** 100-500 companies/day (captcha-limited)

---

## 🚀 NEXT IMMEDIATE STEPS

1. **Confirm authentication requirements** - Do you have login credentials?
2. **Test manual workflow** - Manually search 1 company, document all steps
3. **Create prototype** - Build `supercias_cdp_discovery.py`
4. **Test captcha** - Capture and solve 1 captcha manually

---

## 💡 HONEST ASSESSMENT

**What's Achievable:**
- ✅ Full company registry data
- ✅ Financial statements (all years available)
- ✅ Corporate structure data
- ✅ Legal documents and publications

**Challenges:**
- ⚠️ Captcha will slow us down (human-dependent)
- ⚠️ JSF complexity requires careful reverse-engineering
- ⚠️ Large volume = weeks/months of continuous harvesting
- ⚠️ Some endpoints may require authentication

**Timeline:**
- **Prototype:** 1-2 weeks
- **Full harvester:** 4-6 weeks
- **Complete data collection:** 2-6 months (depending on captcha solving speed)

**This is REAL, ACHIEVABLE, but REQUIRES PATIENCE and RESOURCES.**
