# Ecuador Government Sources - Complete Catalog (32 Entities)

**Last Updated:** 2025-10-18  
**Status:** Comprehensive mapping of all government branches and key institutions  
**Total Entities:** 32 (Executive, Legislative, Judicial, Electoral, Control, Regulatory, Public Enterprises)

---

## 🏛️ EXECUTIVE BRANCH

### 1. Presidencia de la República
- **Domain:** https://www.presidencia.gob.ec/
- **Gob.ec:** https://www.gob.ec/pr
- **Priority:** HIGH
- **Scraping Tool:** Selenium (JavaScript-heavy)
- **Data Types:** Decrees, executive orders, official communications
- **Robots.txt:** ✅ Check required

### 2. Vicepresidencia
- **Domain:** https://www.vicepresidencia.gob.ec/
- **Priority:** MEDIUM
- **Scraping Tool:** Scrapy
- **Data Types:** Official statements, initiatives
- **Robots.txt:** ✅ Check required

---

## 🏛️ LEGISLATIVE BRANCH

### 3. Asamblea Nacional ✅ VERIFIED
- **Domain:** https://asambleanacional.gob.ec/
- **Gob.ec:** https://www.gob.ec/an
- **Priority:** HIGH
- **Scraping Tool:** Scrapy + BeautifulSoup
- **Data Types:** Approved laws, RO citations, legislative history
- **Key URLs:**
  - Laws: https://www.asambleanacional.gob.ec/es/leyes-aprobadas
  - Historical: https://www.asambleanacional.gob.ec/es/noticia/asamblea_nacional_leyes_aprobadas_y_publicadas_en_el_registro_oficial
- **Robots.txt:** ✅ Allowed
- **Status:** Spider exists in codebase

---

## ⚖️ JUDICIAL BRANCH

### 4. Función Judicial / Consejo de la Judicatura ✅ VERIFIED
- **Domain:** https://www.funcionjudicial.gob.ec/
- **Gob.ec:** https://www.gob.ec/cj
- **Priority:** HIGH
- **Scraping Tool:** Selenium (SATJE system)
- **Data Types:** Case law, judicial rulings, procedural documents
- **Key URLs:**
  - SATJE: https://satje.funcionjudicial.gob.ec/
- **Robots.txt:** ✅ Allowed
- **Status:** Spider exists in codebase

### 5. Corte Constitucional ✅ VERIFIED
- **Domain:** https://www.corteconstitucional.gob.ec/
- **Priority:** HIGH
- **Scraping Tool:** Selenium (search forms)
- **Data Types:** Constitutional rulings, precedents, thematic lines
- **Key URLs:**
  - Search: https://buscador.corteconstitucional.gob.ec/buscador-externo/principal
- **Robots.txt:** ✅ Allowed
- **Status:** Spider exists in codebase

---

## 🔍 TRANSPARENCY & CONTROL

### 6. Contraloría General del Estado
- **Domain:** https://www.contraloria.gob.ec/
- **Gob.ec:** https://www.gob.ec/cge
- **Priority:** HIGH
- **Scraping Tool:** Selenium
- **Data Types:** Audit reports, financial oversight, public procurement audits
- **Robots.txt:** ✅ Check required

### 7. Defensoría del Pueblo
- **Domain:** https://www.dpe.gob.ec/
- **Gob.ec:** https://www.gob.ec/dpe
- **Priority:** MEDIUM
- **Scraping Tool:** Scrapy
- **Data Types:** Human rights reports, citizen complaints, recommendations
- **Robots.txt:** ✅ Check required

### 8. Procuraduría General del Estado
- **Domain:** https://www.pge.gob.ec/
- **Gob.ec:** https://www.gob.ec/pge
- **Priority:** HIGH
- **Scraping Tool:** Scrapy
- **Data Types:** Legal opinions, state representation cases, jurisprudence
- **Robots.txt:** ✅ Check required

---

## 🗳️ ELECTORAL FUNCTION

### 9. Consejo Nacional Electoral (CNE)
- **Domain:** https://www.cne.gob.ec/
- **Gob.ec:** https://www.gob.ec/cne
- **Priority:** MEDIUM
- **Scraping Tool:** Scrapy
- **Data Types:** Electoral regulations, results, voter registration data
- **Robots.txt:** ✅ Check required

### 10. Tribunal Contencioso Electoral (TCE)
- **Domain:** https://www.tce.gob.ec/
- **Gob.ec:** https://www.gob.ec/tce
- **Priority:** MEDIUM
- **Scraping Tool:** Scrapy
- **Data Types:** Electoral dispute rulings, resolutions
- **Robots.txt:** ✅ Check required

---

## 🏥 MINISTRIES - SOCIAL SECTOR

### 11. Ministerio de Salud Pública
- **Domain:** https://www.salud.gob.ec/
- **Gob.ec:** https://www.gob.ec/msp
- **Priority:** HIGH
- **Scraping Tool:** Selenium (forms, dynamic content)
- **Data Types:** Health regulations, epidemiological bulletins, medical protocols
- **Robots.txt:** ✅ Check required

### 12. Ministerio de Educación, Deporte y Cultura ✅ VERIFIED
- **Domain:** https://educacion.gob.ec/
- **Gob.ec:** https://www.gob.ec/minedec
- **Priority:** HIGH
- **Scraping Tool:** Scrapy
- **Data Types:** LOEI, curricula, ministerial agreements, educational statistics
- **Key URLs:**
  - Open Data: https://www.datosabiertos.gob.ec/dataset/ (filter MinEduc)
- **Robots.txt:** ✅ Allowed
- **Status:** Spider exists in codebase

---

## 💰 MINISTRIES - ECONOMIC SECTOR

### 13. Ministerio de Economía y Finanzas
- **Domain:** https://www.finanzas.gob.ec/
- **Gob.ec:** https://www.gob.ec/mef
- **Priority:** HIGH
- **Scraping Tool:** Selenium (budget portals)
- **Data Types:** National budget, fiscal reports, public debt data, economic indicators
- **Robots.txt:** ✅ Check required

### 14. Ministerio de Producción, Comercio Exterior e Inversiones (MPCEI)
- **Domain:** https://www.produccion.gob.ec/
- **Gob.ec:** https://www.gob.ec/mpcei
- **Priority:** HIGH
- **Scraping Tool:** Scrapy
- **Data Types:** Trade policies, investment regulations, industrial development
- **Robots.txt:** ✅ Check required

---

## 🛡️ MINISTRIES - SECURITY & GOVERNANCE

### 15. Ministerio de Gobierno
- **Domain:** https://www.ministeriodegobierno.gob.ec/
- **Gob.ec:** https://www.gob.ec/mdg
- **Priority:** HIGH
- **Scraping Tool:** Scrapy
- **Data Types:** Internal governance, civil society regulations, public order
- **Robots.txt:** ✅ Check required

### 16. Ministerio del Interior
- **Domain:** https://www.ministeriodelinterior.gob.ec/
- **Gob.ec:** https://www.gob.ec/mdi
- **Priority:** HIGH
- **Scraping Tool:** Selenium
- **Data Types:** Security policies, crime statistics, emergency management
- **Robots.txt:** ✅ Check required

---

## 🌳 MINISTRIES - ENVIRONMENT & INFRASTRUCTURE

### 17. Ministerio del Ambiente, Agua y Transición Ecológica (MAATE)
- **Domain:** https://www.ambiente.gob.ec/
- **Gob.ec:** https://www.gob.ec/maae
- **Priority:** MEDIUM
- **Scraping Tool:** Selenium
- **Data Types:** Environmental regulations, water management, conservation policies
- **Note:** 2025 fusion of multiple ministries
- **Robots.txt:** ✅ Check required

---

## 🏖️ MINISTRIES - TOURISM & CULTURE

### 18. Ministerio de Turismo
- **Domain:** https://www.turismo.gob.ec/
- **Gob.ec:** https://www.gob.ec/mintur
- **Priority:** LOW
- **Scraping Tool:** Scrapy
- **Data Types:** Tourism regulations, statistics, promotional materials
- **Robots.txt:** ✅ Check required

---

## 📊 PLANNING & COMMUNICATION

### 19. Secretaría Nacional de Planificación
- **Domain:** https://www.planificacion.gob.ec/
- **Gob.ec:** https://www.gob.ec/snp
- **Priority:** HIGH
- **Scraping Tool:** Scrapy
- **Data Types:** National development plans, strategic planning documents
- **Robots.txt:** ✅ Check required

### 20. Secretaría General de Comunicación
- **Domain:** https://www.comunicacion.gob.ec/
- **Priority:** LOW
- **Scraping Tool:** Scrapy
- **Data Types:** Official communications, press releases
- **Robots.txt:** ✅ Check required

---

## 💼 TAX & SOCIAL SECURITY

### 21. Servicio de Rentas Internas (SRI) ✅ VERIFIED
- **Domain:** https://www.sri.gob.ec/
- **Priority:** HIGH
- **Scraping Tool:** Scrapy (static files)
- **Data Types:** Tax regulations, RUC data, revenue statistics, tax forms
- **Key URLs:**
  - Datasets: https://www.sri.gob.ec/datasets
  - Downloads: https://descargas.sri.gob.ec/download/datosAbiertos/
- **Robots.txt:** ✅ Allowed
- **Status:** Spider exists in codebase

### 22. Instituto Ecuatoriano de Seguridad Social (IESS)
- **Domain:** https://www.iess.gob.ec/
- **Priority:** HIGH
- **Scraping Tool:** Selenium (member portals)
- **Data Types:** Social security regulations, contribution tables, benefits
- **Robots.txt:** ✅ Check required

---

## 🚢 CUSTOMS & TRADE

### 23. SENAE (Servicio Nacional de Aduanas) ✅ VERIFIED
- **Domain:** https://www.aduana.gob.ec/
- **Gob.ec:** https://www.gob.ec/senae
- **Priority:** HIGH
- **Scraping Tool:** Scrapy
- **Data Types:** COPCI, tariffs, import/export guides, customs bulletins
- **Key URLs:**
  - Bulletins: https://www.aduana.gob.ec/boletines/
  - Import Guide: https://www.aduana.gob.ec/para-importar/
  - Tariff: https://www.aduana.gob.ec/arancel/
- **Robots.txt:** ✅ Allowed
- **Status:** Spider exists in codebase

---

## 📡 REGULATORY AGENCIES

### 24. ARCOTEL (Agencia de Regulación y Control de las Telecomunicaciones)
- **Domain:** https://www.arcotel.gob.ec/
- **Gob.ec:** https://www.gob.ec/arcotel
- **Priority:** MEDIUM
- **Scraping Tool:** Scrapy
- **Data Types:** Telecom regulations, spectrum management, licensing
- **Robots.txt:** ✅ Check required

### 25. ANT (Agencia Nacional de Tránsito)
- **Domain:** https://www.ant.gob.ec/
- **Gob.ec:** https://www.gob.ec/ant
- **Priority:** MEDIUM
- **Scraping Tool:** Selenium
- **Data Types:** Traffic regulations, vehicle registration, driver licensing
- **Robots.txt:** ✅ Check required

---

## 📰 OFFICIAL PUBLICATIONS

### 26. Registro Oficial ✅ VERIFIED
- **Domain:** https://www.registroficial.gob.ec/
- **Priority:** HIGH
- **Scraping Tool:** Scrapy + PDF extraction
- **Data Types:** Official legal publications, laws, decrees, RO supplements
- **Robots.txt:** ✅ Allowed
- **Status:** Spider exists in codebase

---

## 🏭 PUBLIC ENTERPRISES

### 27. EP Petroecuador
- **Domain:** https://www.eppetroecuador.ec/
- **Gob.ec:** https://www.gob.ec/ep
- **Priority:** MEDIUM
- **Scraping Tool:** Scrapy
- **Data Types:** Oil production data, contracts, regulations
- **Robots.txt:** ✅ Check required

### 28. CELEC EP (Corporación Eléctrica del Ecuador)
- **Domain:** https://www.celec.gob.ec/
- **Gob.ec:** https://www.gob.ec/celec-ep
- **Priority:** MEDIUM
- **Scraping Tool:** Scrapy
- **Data Types:** Energy generation data, regulations, tariffs
- **Robots.txt:** ✅ Check required

### 29. CNEL EP (Corporación Nacional de Electricidad)
- **Domain:** https://www.cnelep.gob.ec/
- **Priority:** MEDIUM
- **Scraping Tool:** Scrapy
- **Data Types:** Electricity distribution, outage reports, tariffs
- **Robots.txt:** ✅ Check required

### 30. CNT EP (Corporación Nacional de Telecomunicaciones)
- **Domain:** https://www.cnt.com.ec/
- **Gob.ec:** https://www.gob.ec/cnt
- **Priority:** LOW
- **Scraping Tool:** Scrapy
- **Data Types:** Telecom services, coverage maps
- **Robots.txt:** ✅ Check required

---

## 👮 SECURITY FORCES

### 31. Policía Nacional
- **Domain:** Multiple (check gob.ec directory)
- **Gob.ec:** https://www.gob.ec/instituciones (search "Policía")
- **Priority:** MEDIUM
- **Scraping Tool:** Selenium
- **Data Types:** Crime statistics, regulations, public safety bulletins
- **Robots.txt:** ✅ Check required

---

## 📊 STATISTICS & OPEN DATA

### 32. INEC (Instituto Nacional de Estadísticas y Censos) ✅ VERIFIED
- **Domain:** https://www.ecuadorencifras.gob.ec/ (may redirect to https://www.inec.gob.ec/)
- **Priority:** HIGH
- **Scraping Tool:** API-first (via Datos Abiertos)
- **Data Types:** Census, employment, prices, vital statistics
- **Key URLs:**
  - Via Datos Abiertos: https://www.datosabiertos.gob.ec/dataset/ (filter INEC)
- **Robots.txt:** ✅ Allowed (API preferred)
- **Status:** Covered via Datos Abiertos spider

### 33. Datos Abiertos (Central Hub) ✅ VERIFIED
- **Domain:** https://www.datosabiertos.gob.ec/
- **Priority:** HIGH
- **Scraping Tool:** CKAN API
- **Data Types:** 1,513 datasets from 98+ organizations
- **Key URLs:**
  - API: https://www.datosabiertos.gob.ec/api/3/
  - Catalog: https://www.datosabiertos.gob.ec/dataset/
- **Robots.txt:** ✅ Allowed (API-first)
- **Status:** Spider exists in codebase

---

## 📋 SUMMARY STATISTICS

### Coverage Status
| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Verified & Spider Exists | 10 | 30% |
| 🟡 Identified, Needs Spider | 22 | 67% |
| 🔴 Unknown/Variable Domain | 1 | 3% |
| **TOTAL** | **33** | **100%** |

### By Priority
| Priority | Count | Focus |
|----------|-------|-------|
| HIGH | 18 | Legal, tax, customs, health, education, finance, security |
| MEDIUM | 12 | Regulatory, public enterprises, planning |
| LOW | 3 | Tourism, communication, telecom services |

### By Scraping Tool Required
| Tool | Count | Use Case |
|------|-------|----------|
| Scrapy | 18 | Static HTML, pagination, bulk downloads |
| Selenium | 12 | JavaScript, forms, dynamic content, AJAX |
| API | 3 | CKAN (Datos Abiertos), structured data |
| Mixed | 0 | Hybrid approach |

---

## 🎯 IMPLEMENTATION PRIORITY MATRIX

### Phase 1 (Sprints 0-2): Foundation - CURRENT
- ✅ Registro Oficial
- ✅ SRI
- ✅ SENAE
- ✅ Asamblea Nacional
- ✅ Corte Constitucional
- ✅ Función Judicial
- ✅ MinEduc
- ✅ INEC (via Datos Abiertos)
- ✅ Datos Abiertos API
- ✅ Constitución

### Phase 2 (Sprints 3-5): High-Priority Expansion
- 🟡 Ministerio de Salud Pública
- 🟡 Ministerio de Economía y Finanzas
- 🟡 Ministerio del Interior
- 🟡 Contraloría General del Estado
- 🟡 Procuraduría General del Estado
- 🟡 IESS
- 🟡 Ministerio de Gobierno
- 🟡 MPCEI (Producción)

### Phase 3 (Sprints 6-8): Medium-Priority Expansion
- 🟡 Presidencia
- 🟡 Secretaría de Planificación
- 🟡 MAATE (Ambiente)
- 🟡 ANT
- 🟡 ARCOTEL
- 🟡 Defensoría del Pueblo
- 🟡 CNE
- 🟡 TCE

### Phase 4 (Sprints 9-10): Public Enterprises & Remaining
- 🟡 EP Petroecuador
- 🟡 CELEC EP
- 🟡 CNEL EP
- 🟡 CNT EP
- 🟡 Policía Nacional
- 🟡 Vicepresidencia
- 🟡 Ministerio de Turismo
- 🟡 Secretaría de Comunicación

---

## 🔧 TECHNICAL REQUIREMENTS BY ENTITY

### Selenium Required (12 entities)
```yaml
High_JavaScript_Sites:
  - Presidencia: Dynamic news feeds
  - Ministerio_Salud: Form submissions, bulletins
  - Ministerio_Economia: Budget portals, dashboards
  - Ministerio_Interior: Security dashboards
  - MAATE: Environmental data portals
  - Corte_Constitucional: Search forms (already implemented)
  - Función_Judicial: SATJE system (already implemented)
  - IESS: Member portals
  - ANT: Vehicle/driver queries
  - Ministerio_Telecomunicaciones: Spectrum data
  - Policía_Nacional: Crime statistics
  - Superintendencia_Compañías: CAPTCHA handling
```

### Scrapy Sufficient (18 entities)
```yaml
Static_HTML_Sites:
  - SRI: Datasets page (already implemented)
  - SENAE: Bulletins (already implemented)
  - Registro_Oficial: PDF archive (already implemented)
  - Asamblea_Nacional: Laws table (already implemented)
  - MinEduc: Documents (already implemented)
  - Ministerio_Trabajo: Regulations
  - Ministerio_Agricultura: Policies
  - Ministerio_Transporte: Infrastructure
  - Ministerio_Inclusion: Social programs
  - Ministerio_Energia: Energy policies
  - Ministerio_Turismo: Tourism data
  - Ministerio_Defensa: Public documents
  - Ministerio_Relaciones_Exteriores: Treaties
  - Procuraduría: Legal opinions
  - Defensoría: Reports
  - CNE: Electoral data
  - TCE: Rulings
  - Public_Enterprises: Reports, contracts
```

### API-First (3 entities)
```yaml
Structured_APIs:
  - Datos_Abiertos: CKAN API (already implemented)
  - INEC: Via Datos Abiertos (already implemented)
  - Potential: Some ministries may expose APIs
```

---

## 📝 NEXT STEPS

### Immediate (Sprint 0-1)
1. Verify robots.txt for all 22 new entities
2. Test accessibility of each domain
3. Identify JavaScript requirements
4. Document authentication needs (if any)

### Short-term (Sprint 2-4)
1. Build spiders for 8 high-priority entities
2. Implement Selenium middleware
3. Test PDF extraction on new sources
4. Validate data quality

### Medium-term (Sprint 5-8)
1. Complete all 22 remaining spiders
2. Implement incremental crawling
3. Set up monitoring for all sources
4. Generate comprehensive corpus statistics

---

## ✅ VALIDATION CHECKLIST

For each new entity, verify:
- [ ] Domain accessible
- [ ] Robots.txt allows crawling
- [ ] Identify primary data types
- [ ] Determine scraping tool (Scrapy/Selenium/API)
- [ ] Test sample extraction
- [ ] Document RO citation patterns (if applicable)
- [ ] Implement spider
- [ ] Write tests with fixtures
- [ ] Add to orchestration
- [ ] Schedule automated crawls

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-18  
**Next Review:** After Sprint 2 completion  
**Maintainer:** YACHAQ-LEX Engineering Team
