# SUPERCIAS HARVESTER - KANBAN BOARD

## 📌 BACKLOG

- [ ] Research authentication requirements for protected endpoints
- [ ] Document all JSF form parameters
- [ ] Create test dataset (100 sample RUCs)
- [ ] Set up monitoring dashboard
- [ ] Create data validation scripts

---

## 🔄 TO DO (Next Sprint)

### **CRITICAL PATH:**
1. [ ] **Create `supercias_cdp_discovery.py`** (3 days)
   - Copy from `sercop_cdp_harvester.py`
   - Adapt for JSF/PrimeFaces
   - Handle ViewState extraction
   
2. [ ] **Test single company search** (2 days)
   - Manual workflow documentation
   - Capture all network requests
   - Identify captcha trigger point

3. [ ] **Implement captcha queue** (2 days)
   - Adapt `sercop_captcha_queue.py`
   - Test with Supercias captcha format

---

## 🏗️ IN PROGRESS

### **Currently Working On:**
- [x] **Portal discovery** ✅ COMPLETE
  - Found 22 data sources
  - Documented technology stack
  - Identified captcha requirements

---

## ✅ DONE

- [x] Analyze Supercias portal structure
- [x] Identify all data sources (22 endpoints)
- [x] Document JSF/PrimeFaces architecture
- [x] Create implementation plan
- [x] Estimate data volumes
- [x] Define success metrics

---

## 🎯 MILESTONES

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Discovery Complete | ✅ TODAY | DONE |
| Prototype Working | Week 2 | PENDING |
| Single Company Extraction | Week 3 | PENDING |
| Batch Processing (100 companies) | Week 5 | PENDING |
| Multi-Source Integration | Week 7 | PENDING |
| Production Ready | Week 10 | PENDING |

---

## 🚨 BLOCKERS

1. **Authentication Credentials**
   - ❓ Do we have login credentials for protected portals?
   - **Action:** User to provide if needed

2. **Captcha Solving Capacity**
   - ⚠️ Need human solver availability
   - **Action:** Confirm human solver schedule

3. **Rate Limiting Unknown**
   - ❓ Don't know if there are rate limits
   - **Action:** Test with small batch first

---

## 📊 METRICS

### **Current Progress:**
- **Discovery:** 100% ✅
- **Prototype:** 0%
- **Core Harvester:** 0%
- **Multi-Source:** 0%
- **Production:** 0%

### **Data Sources Mapped:**
- **Total Sources:** 22
- **Analyzed:** 22
- **Prototyped:** 0
- **Production:** 0

---

## 🔥 PRIORITY QUEUE

### **P0 - CRITICAL (Start Immediately):**
1. Get authentication credentials (if needed)
2. Create CDP discovery prototype
3. Test captcha workflow

### **P1 - HIGH (This Week):**
4. Implement session management
5. Build company search function
6. Test with 10 companies

### **P2 - MEDIUM (Next Week):**
7. Add pagination support
8. Implement document downloader
9. Create progress tracker

### **P3 - LOW (Future):**
10. Optimize performance
11. Add monitoring
12. Create dashboard

---

## 💬 NOTES

**Key Decisions:**
- Using SERCOP architecture as template ✅
- Human-in-the-loop for captchas ✅
- Pydoll/CDP for browser automation ✅
- S3 for storage ✅

**Risks:**
- Captcha solving speed will be bottleneck
- JSF complexity may require more time
- Large data volume = long collection time

**Dependencies:**
- Pydoll library installed
- Chrome/Chromium available
- S3 bucket access
- Human captcha solver available
