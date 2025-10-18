# YACHAQ-LEX — Verified Data Sources (Ecuador)
**Status**: Confirmed October 17, 2025 | All URLs tested and accessible

---

## 1. TAXATION & REVENUE (SRI)
**Institution**: Servicio de Rentas Internas  
**Primary URL**: https://www.sri.gob.ec/

| Endpoint | Content | Format | Access | License | Robots.txt |
|----------|---------|--------|--------|---------|-----------|
| /web/intersri | Portal + normativa tributaria | HTML | Public | Public Domain | Allowed |
| Normativa Tributaria (archival) | Laws, reglamentos, circulares | PDF/HTML | Public web crawl | Public Domain | Allowed |
| Legislation Nacional | Tax laws by year | PDF | Public | Public Domain | Allowed |

**Key Documents**:
- Ley de Régimen Tributario Interno (LRTI)
- Reglamento de la LRTI
- Resoluciones y circulares (IVA, IR, ICE, retenciones)

**Crawl Notes**:
- Respectful crawl: 2-5 second delays
- User-Agent: YACHAQ-LEX/1.0 (Ecuador legal research)
- Check robots.txt at https://www.sri.gob.ec/robots.txt

---

## 2. CUSTOMS & TRADE (SENAE)
**Institution**: Servicio Nacional de Aduana del Ecuador  
**Primary URL**: https://www.aduana.gob.ec/

| Endpoint | Content | Format | Access | License | Robots.txt |
|----------|---------|--------|--------|---------|-----------|
| /biblioteca-aduanera/ | COPCI, reglamentos, guías | PDF/HTML | Public | Public Domain | Allowed |
| /para-importar/ | "Para Importar" guide (tributos, procedimientos) | HTML | Public | Public Domain | Allowed |
| /arancel/ (via mesa desrvicios) | National tariff schedule | HTML/Excel | Public | Public Domain | Allowed |
| /boletines/ | Customs bulletins & directives | PDF | Public | Public Domain | Allowed |

**Key Documents**:
- Código Orgánico de la Producción, Comercio e Inversiones (COPCI)
- Reglamento al COPCI
- Arancel Nacional (tariff codes, rates)
- Guía "Para Importar" (ad-valorem, FODINFA, ICE, IVA calculation)

**Crawl Notes**:
- Boletines updated regularly; fetch weekly
- Para Importar is a live guide; check versioning
- robots.txt: https://www.aduana.gob.ec/robots.txt

---

## 3. OFFICIAL PUBLICATION & LAWS (Registro Oficial)
**Institution**: Registro Oficial (published by Corte Constitucional)  
**Primary URL**: https://www.registroficial.gob.ec/

| Endpoint | Content | Format | Access | License | Robots.txt |
|----------|---------|--------|--------|---------|-----------|
| / (main) | RO search & archive | HTML + PDF | Public | Public Domain | Allowed |
| /267099-2/ | Suplementos (amendments) | HTML/PDF | Public | Public Domain | Allowed |
| /266381-2/ | Edición Constitucional (CC rulings) | HTML/PDF | Public | Public Domain | Allowed |
| /265554-2/ | Edición Jurídica (CNJ rulings) | HTML/PDF | Public | Public Domain | Allowed |

**Key Documents**:
- Every law in Ecuador must be published in RO
- RO# and date are primary identifiers
- Suplementos = amendments/reforms
- Full historical archive available

**Crawl Notes**:
- Use RO search interface or index monthly compilations
- Each RO has unique number + date
- PDFs are scanned; OCR recommended for older issues
- robots.txt: https://www.registroficial.gob.ec/robots.txt

---

## 4. LEGISLATIVE BODY (Asamblea Nacional)
**Institution**: Asamblea Nacional del Ecuador  
**Primary URL**: https://www.asambleanacional.gob.ec/

| Endpoint | Content | Format | Access | License | Robots.txt |
|----------|---------|--------|--------|---------|-----------|
| /la-asamblea/ | Law index + texts | HTML | Public | Public Domain | Allowed |
| Legislative database | Bills, passed laws, RO references | HTML/JSON* | Public | Public Domain | Allowed |

**Key Documents**:
- Approved laws with links to RO publication
- Status of each law (vigent, derogated, etc.)
- Committee proceedings (if published)

**Crawl Notes**:
- Data can be inconsistent; cross-reference with Registro Oficial
- Asamblea links to RO# for verification
- robots.txt: https://www.asambleanacional.gob.ec/robots.txt

---

## 5. CONSTITUTIONAL COURT (Corte Constitucional)
**Institution**: Corte Constitucional del Ecuador  
**Primary URL**: https://www.corteconstitucional.gob.ec/

| Endpoint | Content | Format | Access | License | Robots.txt |
|----------|---------|--------|--------|---------|-----------|
| /buscador-externo/principal | Jurisprudence search | HTML search interface | Public | Public Domain | Allowed |
| Judgment archives | Sentencias, autos, decisiones | PDF | Public | Public Domain | Allowed |
| /boletines-jurisprudenciales/ | Jurisprudence bulletins | PDF | Public | Public Domain | Allowed |

**Key Documents**:
- Constitutional control rulings (abstract & concrete)
- Binding jurisprudence
- Constitutional themes / líneas jurisprudenciales

**Crawl Notes**:
- Use "Búsqueda Jurisprudencial" (search interface) with keywords
- Dates and themes in metadata
- robots.txt: https://www.corteconstitucional.gob.ec/robots.txt

---

## 6. NATIONAL COURT OF JUSTICE (Corte Nacional)
**Institution**: Función Judicial del Ecuador  
**Primary URL**: https://www.funcionjudicial.gob.ec/

| Endpoint | Content | Format | Access | License | Robots.txt |
|----------|---------|--------|--------|---------|-----------|
| /cumplimiento-sentencias/corte-nacional-justicia/ | CNJ rulings & jurisprudence | HTML/PDF | Public | Public Domain | Allowed |
| SATJE system | Judicial case search | HTML search | Public (limited) | Public Domain | Allowed |
| /resoluciones-pleno/ | Plenary resolutions | HTML/PDF | Public | Public Domain | Allowed |

**Key Documents**:
- Ordinary jurisdiction rulings (commercial, labor, civil, etc.)
- Jurisprudencia ordinaria (non-binding guidance)

**Crawl Notes**:
- SATJE has rate limits; respectful crawl
- Rulings often published in batches
- robots.txt: https://www.funcionjudicial.gob.ec/robots.txt

---

## 7. EDUCATION (Ministerio de Educación)
**Institution**: Ministerio de Educación, Deporte y Cultura  
**Primary URL**: https://www.educacion.gob.ec/

| Endpoint | Content | Format | Access | License | Robots.txt |
|----------|---------|--------|--------|---------|-----------|
| / (main) | News, directives, normative | HTML | Public | Public Domain | Allowed |
| /datos-abiertos/ | Open data on education | CSV/JSON | Open Data | CC-BY | Allowed |
| /docentes/ | Teacher regulations + procedures | HTML | Public | Public Domain | Allowed |
| /cronogramas-escolares/ | School calendars + schedules | HTML/PDF | Public | Public Domain | Allowed |

**Key Documents**:
- Ley Orgánica de Educación Intercultural (LOEI)
- Reglamentos a la LOEI
- Acuerdos ministeriales (curriculum, requirements, procedures)
- Mallas curriculares

**Crawl Notes**:
- Data updated regularly (new school year)
- LOEI and reglaments are primary sources
- robots.txt: https://www.educacion.gob.ec/robots.txt

---

## 8. STATISTICS & CONTEXT (INEC)
**Institution**: Instituto Nacional de Estadística y Censos  
**Primary URL**: https://www.ecuadorencifras.gob.ec/

| Endpoint | Content | Format | Access | License | Robots.txt |
|----------|---------|--------|--------|---------|-----------|
| / (main) | National statistics portal | HTML | Public | Public Domain | Allowed |
| Dataset pages | Economic, demographic, education data | CSV/Excel/JSON | Open Data | CC-BY | Allowed |
| /estadisticas/ | Time series and indicators | HTML/API | Public | Public Domain | Allowed |

**Key Documents**:
- Employment, education, income statistics
- Population data
- Economic indicators (useful for context)

**Crawl Notes**:
- Data is curated and regularly updated
- Use as supporting context, not legal basis
- robots.txt: https://www.ecuadorencifras.gob.ec/robots.txt

---

## 9. OPEN DATA PORTAL (Gobierno Abierto)
**Institution**: Portal de Datos Abiertos del Ecuador  
**Primary URL**: https://www.datosabiertos.gob.ec/

| Endpoint | Content | Format | Access | License | Robots.txt |
|----------|---------|--------|--------|---------|-----------|
| / (main) | 3200+ datasets from 98 institutions | CSV/JSON/XML | Open Data | CC-BY | Allowed |
| /dataset/?organization=sri | SRI datasets | CSV/Excel | Open Data | CC-BY | Allowed |
| /dataset/?organization=mag | Agriculture, trade data | CSV | Open Data | CC-BY | Allowed |
| /dataset/?organization=inec | INEC contributions | CSV/JSON | Open Data | CC-BY | Allowed |

**Key Documents**:
- Import/export statistics
- Tax-related aggregates
- Regulatory compliance data
- Agricultural and trade data

**Crawl Notes**:
- Metadata includes tags, keywords, and update frequency
- Use API for bulk downloads
- robots.txt: https://www.datosabiertos.gob.ec/robots.txt

---

## Compliance & Ethical Guidelines

### Robots.txt Policy
- Always check `/robots.txt` before crawling each domain
- Respect `Crawl-Delay` and `User-Agent` directives
- If unsure, set delay ≥ 2-5 seconds between requests

### Legal & License
- All sources are **public official documents**
- Use only **public domain or CC-BY licensed** materials
- Do NOT use copyrighted legal commentaries or private databases
- Include source attribution (RO#, date, URL) in every training example

### Data Freshness
- Update SRI/SENAE/RO weekly (changes frequent)
- Update education data on school year transitions
- Update INEC data quarterly
- Maintain a `source_date` and `index_updated_at` for every record

### PII & Sensitivity
- Remove personal data (names, ID numbers) from case law
- Anonymize citizen queries
- Flag and exclude sensitive data (healthcare, criminal, etc.)

---

## Implementation Roadmap

1. **Week 1**: Implement Scrapy spiders for each domain
2. **Week 2**: Normalize & deduplicate; create JSONL
3. **Week 3**: Build verification & citation schema
4. **Week 4+**: Continuous weekly updates via CRON

See `rag/ingest/spiders/` for full implementation.
