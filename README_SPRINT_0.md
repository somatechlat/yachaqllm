# YACHAQ-LEX Sprint 0 - Data Extraction from 33 Ecuador Government Sources

**Project Goal:** Train Ecuador's first sovereign LLM for legal, tax, customs, and education intelligence

**Current Phase:** Sprint 0 - Data Collection Infrastructure  
**Status:** 🟢 Day 1 Complete - 13/33 spiders operational

---

## 🚀 Quick Start

```bash
# Navigate to project
cd /Users/macbookpro201916i964gb1tb/Downloads/YACHAQ-LEX_full

# Test the 3 new spiders added today
chmod +x TEST_NEW_SPIDERS.sh
./TEST_NEW_SPIDERS.sh

# Run individual spider
cd rag/ingest
scrapy crawl presidencia -o presidencia_output.jsonl

# List all available spiders
scrapy list
```

---

## 📊 Current Status (Day 1)

### Spiders Operational: 13/33 (39%)

**✅ Original 10 (Already in codebase):**
1. SRI - Tax authority
2. SENAE - Customs
3. Registro Oficial - Legal publications
4. Asamblea Nacional - Laws
5. SRI Datasets - Tax statistics
6. MinEduc - Education
7. Corte Constitucional - Constitutional rulings
8. Datos Abiertos - Open data API
9. Función Judicial - Case law
10. Constitución - Constitution PDF

**🆕 Added Today (3):**
11. Presidencia - Executive decrees
12. Ministerio de Salud - Health regulations
13. Ministerio de Economía - Budget & fiscal

**⏳ Next (20 remaining):**
- 5 tomorrow: Contraloría, Procuraduría, IESS, Interior, Gobierno
- 15 over next 2 weeks

---

## 📁 Key Documents

### Planning & Roadmap
- `MASTER_SOURCES_ALL_33.md` - Complete entity catalog
- `SPRINT_ROADMAP_COMPLETE.md` - 12-sprint execution plan
- `SPRINT_0_START_NOW.md` - Immediate action items

### Progress Tracking
- `PROGRESS_TRACKER.md` - Daily progress updates
- `SPRINT_0_DAY_1_SUMMARY.md` - Today's accomplishments

### Source Documentation
- `REAL_URLS_VERIFIED.md` - Original 10 verified sources
- `ECUADOR_GOVERNMENT_SOURCES_COMPLETE.md` - All 33 entities detailed

---

## 🎯 Sprint 0 Goals (2 weeks)

### Week 1
- [x] Day 1: Add 3 spiders (Presidencia, Salud, Economía) ✅
- [ ] Day 2: Add 5 spiders (Contraloría, Procuraduría, IESS, Interior, Gobierno)
- [ ] Day 3-5: Add 10 more spiders
- [ ] Target: 18 spiders by end of week

### Week 2
- [ ] Day 6-10: Add remaining 15 spiders
- [ ] Day 11-12: Test all spiders
- [ ] Day 13-14: Fix issues, optimize
- [ ] Target: 33 spiders operational

---

## 🛠️ Technology Stack

### Scraping Tools
- **Scrapy** - Fast, efficient crawling (18 entities)
- **Selenium** - JavaScript-heavy sites (12 entities)
- **BeautifulSoup** - Robust HTML parsing (all entities)

### Storage
- **S3/GCS** - Raw documents & metadata
- **Qdrant** - Vector embeddings
- **Parquet** - Structured data

### Processing
- **pdfminer.six** - PDF text extraction
- **Tesseract** - OCR for scanned documents
- **pandas** - Data transformation

---

## 📈 Expected Outcomes

### By End of Sprint 0 (Week 2)
- ✅ 33 spiders operational
- ✅ ~15,000 documents scraped
- ✅ ~200,000 text chunks indexed
- ✅ All entities covered

### By End of Sprint 12 (Week 26)
- ✅ 100k instruction pairs generated
- ✅ QLoRA training complete
- ✅ Model quantized (AWQ 4-bit)
- ✅ vLLM serving operational
- ✅ RAG pipeline integrated

---

## 🔧 Development Commands

### Spider Development
```bash
# Create new spider (use template)
# Edit: rag/ingest/spiders/yachaq_spiders.py

# Test spider
cd rag/ingest
scrapy crawl spider_name -o test_output.jsonl -s CLOSESPIDER_PAGECOUNT=5

# Run spider in production
scrapy crawl spider_name -o output.jsonl
```

### Testing
```bash
# Test all new spiders
./TEST_NEW_SPIDERS.sh

# Validate JSONL output
cat output.jsonl | jq '.' | head -20

# Count documents
wc -l output.jsonl
```

### Monitoring
```bash
# Check spider list
scrapy list

# Count spiders
scrapy list | wc -l

# View logs
tail -f scrapy.log
```

---

## 📋 Spider Template

```python
class NewEntitySpider(BaseYachaqSpider):
    name = 'entity_name'
    allowed_domains = ['entity.gob.ec']
    start_urls = ['https://www.entity.gob.ec/']
    source_name = 'Entity Name'
    
    custom_settings = {'DOWNLOAD_DELAY': 3}
    
    def parse(self, response):
        # Extract document links
        links = response.css('a::attr(href)').getall()
        for link in links:
            if 'keyword' in link.lower():
                yield response.follow(link, callback=self.parse_document)
    
    def parse_document(self, response):
        title = response.css('h1::text').get()
        text = ' '.join(response.css('p::text').getall()).strip()
        
        if len(text) < 100:
            return
        
        yield self.enrich_metadata({
            'url': response.url,
            'title': title,
            'text': text,
            'authority': 'Type',
            'ro_number': None,
            'ro_date': None,
            'article': None,
        })
```

---

## 🎓 Best Practices

### Scraping Ethics
- ✅ Respect robots.txt
- ✅ Use delays (3-5 seconds)
- ✅ Limit concurrent requests (1 per domain)
- ✅ Identify user agent properly
- ✅ Handle errors gracefully

### Data Quality
- ✅ Validate JSONL schema
- ✅ Check minimum text length (100 chars)
- ✅ Extract metadata (RO#, date, authority)
- ✅ Generate unique hash for deduplication
- ✅ Log all errors

### Code Quality
- ✅ Follow existing patterns
- ✅ Document spider purpose
- ✅ Add error handling
- ✅ Test before committing
- ✅ Update progress tracker

---

## 🚨 Troubleshooting

### Spider Not Finding Links
```python
# Debug: Print all links
def parse(self, response):
    links = response.css('a::attr(href)').getall()
    self.logger.info(f"Found {len(links)} links")
    for link in links[:10]:
        self.logger.info(f"Link: {link}")
```

### Rate Limiting
```python
# Increase delay
custom_settings = {
    'DOWNLOAD_DELAY': 5,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
}
```

### JavaScript Content
```python
# Use Selenium (add later)
# For now, check if content loads without JS
```

---

## 📞 Support

### Documentation
- See `docs/` folder for comprehensive manuals
- Check `PROGRESS_TRACKER.md` for current status
- Review `SPRINT_ROADMAP_COMPLETE.md` for full plan

### Issues
- Document in progress tracker
- Note spider name and error
- Include sample URL
- Propose solution

---

## 🏆 Success Metrics

### Sprint 0 Complete When:
- [ ] All 33 spiders implemented
- [ ] Each spider extracts ≥10 documents
- [ ] Total documents ≥15,000
- [ ] All JSONL validates
- [ ] No critical errors
- [ ] Documentation complete

**Current Progress:** 39% (13/33 spiders)

---

## 📅 Timeline

- **Day 1 (Today):** ✅ 13 spiders
- **Day 2:** Target 18 spiders
- **Week 1:** Target 18 spiders
- **Week 2:** Target 33 spiders
- **Sprint 0 End:** All 33 operational

---

**Last Updated:** 2025-10-18  
**Next Review:** 2025-10-19 (Day 2)  
**Sprint 0 Target:** 2025-11-01

🚀 **Let's build Ecuador's sovereign LLM!**
