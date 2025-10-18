# SPRINT 0 - START NOW: Expand Scraping to All 33 Entities

**Date:** 2025-10-18  
**Goal:** Add 23 new government sources to existing 10  
**Timeline:** 2 weeks

---

## ✅ What We Have (10 spiders in codebase)

1. SRI - Tax data
2. SENAE - Customs
3. Registro Oficial - Legal publications
4. Asamblea Nacional - Laws
5. Corte Constitucional - Constitutional rulings
6. Función Judicial - Case law
7. MinEduc - Education
8. INEC - Statistics
9. Datos Abiertos - Open data API
10. Constitución - Constitution PDF

---

## 🚀 What We're Adding NOW (23 new spiders)

### Batch 1: High Priority (8 entities) - THIS WEEK

11. **Presidencia** - https://www.presidencia.gob.ec/
12. **Ministerio de Salud** - https://www.salud.gob.ec/
13. **Ministerio de Economía** - https://www.finanzas.gob.ec/
14. **Contraloría** - https://www.contraloria.gob.ec/
15. **Procuraduría** - https://www.pge.gob.ec/
16. **IESS** - https://www.iess.gob.ec/
17. **Ministerio del Interior** - https://www.ministeriodelinterior.gob.ec/
18. **Ministerio de Gobierno** - https://www.ministeriodegobierno.gob.ec/

### Batch 2: Medium Priority (8 entities) - NEXT WEEK

19. **MPCEI (Producción)** - https://www.produccion.gob.ec/
20. **Secretaría Planificación** - https://www.planificacion.gob.ec/
21. **ARCOTEL** - https://www.arcotel.gob.ec/
22. **ANT** - https://www.ant.gob.ec/
23. **Defensoría** - https://www.dpe.gob.ec/
24. **CNE** - https://www.cne.gob.ec/
25. **TCE** - https://www.tce.gob.ec/
26. **MAATE (Ambiente)** - https://www.ambiente.gob.ec/

### Batch 3: Lower Priority (7 entities) - WEEK 3

27. **Vicepresidencia** - https://www.vicepresidencia.gob.ec/
28. **Ministerio Turismo** - https://www.turismo.gob.ec/
29. **Ministerio Defensa** - https://www.defensa.gob.ec/
30. **Secretaría Comunicación** - https://www.comunicacion.gob.ec/
31. **EP Petroecuador** - https://www.eppetroecuador.ec/
32. **CELEC EP** - https://www.celec.gob.ec/
33. **MIES (Inclusión Social)** - https://www.inclusion.gob.ec/

---

## 📝 Spider Template for New Entities

```python
class PresidenciaSpider(BaseYachaqSpider):
    name = 'presidencia'
    allowed_domains = ['presidencia.gob.ec']
    start_urls = ['https://www.presidencia.gob.ec/']
    source_name = 'Presidencia'
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }
    
    def parse(self, response):
        # Extract decree/executive order links
        links = response.css('a[href*="decreto"]::attr(href)').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_document)
    
    def parse_document(self, response):
        title = response.css('h1::text').get()
        text = ' '.join(response.css('p::text').getall())
        
        item = {
            'url': response.url,
            'title': title,
            'text': text,
            'source': self.source_name,
            'authority': 'Decreto Ejecutivo',
            'ro_number': self._extract_ro_number(text),
            'ro_date': self._extract_date(text),
        }
        yield self.enrich_metadata(item)
```

---

## 🎯 TODAY'S TASKS (Next 4 hours)

### Task 1: Add Presidencia Spider (1 hour)
```bash
# Edit: rag/ingest/spiders/yachaq_spiders.py
# Add PresidenciaSpider class after existing spiders
```

### Task 2: Add Ministerio de Salud Spider (1 hour)
```bash
# Add MinisterioSaludSpider class
# Focus on: regulations, health bulletins, COVID data
```

### Task 3: Add Ministerio de Economía Spider (1 hour)
```bash
# Add MinisterioEconomiaSpider class
# Focus on: budget documents, fiscal reports, economic indicators
```

### Task 4: Test All 3 New Spiders (1 hour)
```bash
cd /Users/macbookpro201916i964gb1tb/Downloads/YACHAQ-LEX_full/rag/ingest

# Test Presidencia
scrapy crawl presidencia -o test_presidencia.jsonl

# Test Salud
scrapy crawl ministerio_salud -o test_salud.jsonl

# Test Economía
scrapy crawl ministerio_economia -o test_economia.jsonl
```

---

## 📊 Success Metrics for Today

- [ ] 3 new spiders added to codebase
- [ ] Each spider extracts at least 10 documents
- [ ] All documents have: title, text, url, source
- [ ] JSONL output validates
- [ ] No crashes or errors

---

## 🔧 Tools We're Using

**Scrapy** (for most sites):
- Fast, efficient
- Built-in retry logic
- Respects robots.txt

**Selenium** (only if needed):
- JavaScript-heavy sites
- Dynamic content
- Will add later if required

**BeautifulSoup** (for parsing):
- Robust HTML parsing
- Fallback selectors
- Already imported in base spider

---

## 📈 Progress Tracking

| Entity | Status | Documents | Notes |
|--------|--------|-----------|-------|
| Presidencia | 🟡 Starting | 0 | Decrees, executive orders |
| Min. Salud | 🟡 Starting | 0 | Health regulations |
| Min. Economía | 🟡 Starting | 0 | Budget, fiscal reports |
| Contraloría | ⏸️ Next | 0 | Audit reports |
| Procuraduría | ⏸️ Next | 0 | Legal opinions |
| IESS | ⏸️ Next | 0 | Social security |
| Min. Interior | ⏸️ Next | 0 | Security policies |
| Min. Gobierno | ⏸️ Next | 0 | Governance |

---

## 🚀 LET'S START!

**Right now:** Open `rag/ingest/spiders/yachaq_spiders.py` and add the first 3 spiders.

**Goal for today:** 13 total spiders (10 existing + 3 new)

**Goal for this week:** 18 total spiders (10 + 8 new)

**Goal for Sprint 0:** 33 total spiders (ALL entities covered)
