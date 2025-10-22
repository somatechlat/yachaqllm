# CAPTCHA SOLUTION ANALYSIS - SERCOP vs SUPERCIAS

**Analysis Date:** 2025  
**Objective:** Understand existing SERCOP captcha solution and adapt for Supercias

---

## 🔍 CURRENT SERCOP CAPTCHA SOLUTION

### **Strategy Identified: HUMAN-IN-THE-LOOP QUEUE SYSTEM**

Based on code analysis, here's how SERCOP captcha is currently "solved":

### **Architecture:**

```
┌─────────────────────────────────────────────────────┐
│  1. CDP Capture (Pydoll)                            │
│     - Renders page with JavaScript                  │
│     - Detects captcha images automatically          │
│     - Downloads captcha to local storage            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  2. Captcha Queue System                            │
│     - Saves captcha image to disk                   │
│     - Creates manifest.jsonl entry with:            │
│       * Session cookies                             │
│       * Form defaults                               │
│       * Captcha image path                          │
│       * Task ID & timestamp                         │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  3. Human Solver (MANUAL STEP)                      │
│     - Human opens captcha images                    │
│     - Transcribes text manually                     │
│     - Updates manifest with solution                │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  4. Harvester Consumes Solutions                    │
│     - Reads manifest with solutions                 │
│     - Reuses saved session cookies                  │
│     - Submits form with captcha answer              │
│     - Extracts data                                 │
└─────────────────────────────────────────────────────┘
```

### **Key Components:**

1. **`pydoll_cdp_discovery.py`**
   - Detects captcha images in rendered page
   - Looks for keywords: "captcha", "recaptcha", "captchaimg"
   - Downloads image (data URI or HTTP)
   - Saves to `{trace_id}-captcha-{n}.png`

2. **`human_adapter.py`**
   - Creates `HumanTask` dataclass
   - Saves captcha image to `rag/ingest/comprehensive_data/sercop_captcha_queue/captchas/`
   - Appends to `manifest.jsonl` with all context needed

3. **`sercop_captcha_queue.py`**
   - CLI tool to batch-create captcha tasks
   - Fetches search form
   - Downloads captcha
   - Saves session state
   - Creates manifest entries

4. **`mock_adapter.py`**
   - For testing only
   - Returns fake solutions

### **Critical Insight:**

**THERE IS NO AUTOMATED CAPTCHA SOLVING!**

The system is designed for:
- **Batch preparation:** Create many captcha tasks at once
- **Human solving:** Someone manually transcribes them
- **Batch consumption:** Harvester uses pre-solved captchas

**TTL:** Captchas expire in ~180 seconds (3 minutes)

---

## 📊 SERCOP CAPTCHA CHARACTERISTICS

From `docs/sercop-discovery.md`:

| Property | Value |
|----------|-------|
| **Type** | Image-based text distortion |
| **Endpoint** | `../exe/generadorCaptcha.php` |
| **Session-bound** | YES (must use same PHPSESSID) |
| **Refresh** | After every successful search |
| **Validation** | Server-side, returns "fallo" on error |
| **Expiry** | Fast (~3 minutes) |
| **Complexity** | Moderate noise, 60-70% OCR accuracy |

**Documented Options (Not Implemented):**
1. ✅ **Human-in-the-loop** (CURRENT)
2. ❌ **OCR + pytesseract** (mentioned, not implemented)
3. ❌ **2Captcha/Anti-Captcha** (mentioned, not implemented)
4. ❌ **API alternative** (doesn't exist)

---

## 🎯 SUPERCIAS CAPTCHA ANALYSIS

### **From Portal Investigation:**

```html
<td><span id="frmBusquedaCompanias:panelCaptcha"></span></td>
```

**Key Findings:**

1. **Dynamic Loading:** Captcha panel is empty initially
2. **AJAX Trigger:** Loaded after company selection via autocomplete
3. **PrimeFaces Integration:** Uses `PrimeFaces.ab()` AJAX calls
4. **Session Management:** JSF ViewState + JSESSIONID

### **Workflow:**

```
User selects search type (Expediente/RUC/Nombre)
         ↓
User types in autocomplete field
         ↓
PrimeFaces AJAX: itemSelect event
         ↓
Server updates: panelCaptcha + btnConsultarCompania
         ↓
Captcha image appears dynamically
         ↓
User enters captcha text
         ↓
Submit button enabled
         ↓
Form submission with captcha validation
```

### **Differences from SERCOP:**

| Aspect | SERCOP | SUPERCIAS |
|--------|--------|-----------|
| **Framework** | PHP + Prototype.js | JSF + PrimeFaces |
| **Loading** | Immediate on page load | Dynamic after selection |
| **Session** | PHPSESSID | JSESSIONID + ViewState |
| **Trigger** | Page load | Autocomplete selection |
| **Validation** | AJAX response | Form submission |

---

## 💡 SOLUTION FOR SUPERCIAS

### **RECOMMENDED: ADAPT SERCOP'S HUMAN-IN-THE-LOOP SYSTEM**

**Why this works:**

1. ✅ **Proven:** Already working for SERCOP
2. ✅ **Flexible:** Works with any captcha type
3. ✅ **Reliable:** 100% accuracy (human)
4. ✅ **Simple:** No external dependencies
5. ✅ **Cost-effective:** No API fees

**Why NOT automated solving:**

1. ❌ **OCR accuracy:** 60-70% = too many retries
2. ❌ **2Captcha cost:** $2.99/1000 captchas = expensive at scale
3. ❌ **Latency:** 15-20 seconds per captcha
4. ❌ **Complexity:** Additional service integration

### **Adaptation Plan:**

```python
# NEW: supercias_captcha_adapter.py

class SuperciasCaptchaAdapter:
    """
    Adapts SERCOP's human-in-the-loop system for Supercias
    """
    
    def __init__(self):
        self.manifest_dir = Path("rag/ingest/comprehensive_data/supercias_captcha_queue")
        self.captcha_dir = self.manifest_dir / "captchas"
    
    def detect_captcha_in_ajax_response(self, ajax_html: str) -> Optional[str]:
        """
        Parse AJAX response for captcha image
        PrimeFaces returns HTML fragment with <img> tag
        """
        # Look for captcha image in panelCaptcha update
        # Extract src attribute
        pass
    
    def create_task(self, session, viewstate, form_data, captcha_src):
        """
        Similar to SERCOP but includes JSF ViewState
        """
        task = {
            'task_id': generate_id(),
            'jsessionid': session.cookies.get('JSESSIONID'),
            'viewstate': viewstate,  # NEW: JSF ViewState
            'form_data': form_data,
            'captcha_path': save_captcha_image(),
            'created_at': now(),
            'ttl_seconds': 180
        }
        append_to_manifest(task)
        return task
```

### **Workflow for Supercias:**

```
1. CDP Capture: Load search page
   ↓
2. Extract ViewState from form
   ↓
3. Trigger autocomplete AJAX (select company)
   ↓
4. Parse AJAX response for captcha panel HTML
   ↓
5. Extract captcha image src
   ↓
6. Download captcha (reuse session)
   ↓
7. Save to queue with ViewState + session
   ↓
8. HUMAN SOLVES (manual step)
   ↓
9. Read solved manifest
   ↓
10. Restore session + ViewState
   ↓
11. Submit form with captcha solution
   ↓
12. Extract company data
```

---

## 🚀 IMPLEMENTATION STEPS

### **Phase 1: Captcha Detection (Week 1)**

**Files to Create:**
- `rag/captcha/supercias_adapter.py`
- `rag/ingest/supercias_captcha_queue.py`

**Tasks:**
1. [ ] Adapt `pydoll_cdp_discovery.py` for JSF
2. [ ] Detect captcha in AJAX response
3. [ ] Extract ViewState tokens
4. [ ] Save captcha + session state

### **Phase 2: Queue System (Week 1)**

**Files to Create:**
- `rag/ingest/comprehensive_data/supercias_captcha_queue/`

**Tasks:**
1. [ ] Create manifest structure (similar to SERCOP)
2. [ ] Add ViewState field to manifest
3. [ ] Test with 10 sample captchas
4. [ ] Validate session preservation

### **Phase 3: Consumption (Week 2)**

**Files to Create:**
- `rag/discovery/supercias_harvester.py`

**Tasks:**
1. [ ] Read solved manifest
2. [ ] Restore JSF session + ViewState
3. [ ] Submit form with captcha
4. [ ] Handle validation errors
5. [ ] Extract company data

### **Phase 4: Batch Processing (Week 2-3)**

**Tasks:**
1. [ ] Create batch captcha generation script
2. [ ] Test with 100 companies
3. [ ] Measure human solving throughput
4. [ ] Optimize workflow

---

## 📊 PERFORMANCE ESTIMATES

### **Human Solving Capacity:**

| Metric | Conservative | Optimistic |
|--------|--------------|------------|
| **Captchas/hour** | 60 | 120 |
| **Captchas/day** | 480 | 960 |
| **Companies/day** | 480 | 960 |

**For 500K companies:**
- **Conservative:** 1,042 days (~3 years)
- **Optimistic:** 521 days (~1.5 years)
- **With 5 solvers:** 104-208 days (~3-7 months)

### **Optimization Strategies:**

1. **Batch Generation:**
   - Generate 100 captchas at once
   - Human solves in one session
   - Consume immediately (before expiry)

2. **Multiple Solvers:**
   - Distribute captcha batches
   - Parallel solving
   - 5x throughput increase

3. **Smart Scheduling:**
   - Generate captchas when solver available
   - Respect 3-minute TTL
   - Minimize waste

---

## 🎯 ALTERNATIVE: EXTERNAL CAPTCHA SERVICE

**If human-in-the-loop is too slow:**

### **2Captcha Integration:**

```python
# NEW: rag/captcha/twocaptcha_adapter.py

import requests

class TwoCaptchaAdapter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://2captcha.com"
    
    def solve(self, captcha_bytes, timeout=120):
        # 1. Submit captcha
        response = requests.post(
            f"{self.base_url}/in.php",
            files={'file': captcha_bytes},
            data={'key': self.api_key, 'method': 'post'}
        )
        captcha_id = response.text.split('|')[1]
        
        # 2. Poll for solution (15-20 seconds)
        for _ in range(timeout):
            result = requests.get(
                f"{self.base_url}/res.php",
                params={'key': self.api_key, 'action': 'get', 'id': captcha_id}
            )
            if result.text.startswith('OK|'):
                return result.text.split('|')[1]
            time.sleep(5)
        
        raise TimeoutError("Captcha solving timeout")
```

**Cost Analysis:**
- **Price:** $2.99 per 1000 captchas
- **500K companies:** $1,495
- **Latency:** 15-20 seconds per captcha
- **Throughput:** 180-240 captchas/hour
- **Total time:** 2,083-2,778 hours (~87-116 days continuous)

---

## 🏆 FINAL RECOMMENDATION

### **START WITH HUMAN-IN-THE-LOOP:**

**Reasons:**
1. ✅ **Proven system** - already works for SERCOP
2. ✅ **Zero cost** - no API fees
3. ✅ **100% accuracy** - no retries
4. ✅ **Quick to implement** - adapt existing code
5. ✅ **Flexible** - works with any captcha changes

**Then Scale:**
1. Test with 1,000 companies (human solving)
2. Measure actual throughput
3. If too slow, integrate 2Captcha
4. Hybrid approach: human for critical, API for bulk

### **Implementation Priority:**

**Week 1:**
- [ ] Adapt SERCOP queue system for Supercias
- [ ] Test with 10 companies manually
- [ ] Validate session + ViewState handling

**Week 2:**
- [ ] Batch process 100 companies
- [ ] Measure human solving rate
- [ ] Decide: continue human or add 2Captcha

**Week 3+:**
- [ ] Scale to 1,000+ companies
- [ ] Optimize workflow
- [ ] Consider automation if needed

---

## 📝 SUMMARY

**SERCOP Solution:** Human-in-the-loop queue system  
**Supercias Adaptation:** Same approach + JSF ViewState handling  
**Timeline:** 2-3 weeks to production-ready  
**Cost:** $0 (human) or $1,500 (2Captcha for 500K)  
**Throughput:** 480-960 companies/day (human) or 4,320 companies/day (2Captcha)

**HONEST ASSESSMENT:** Human-in-the-loop is the RIGHT starting point. Scale with automation only if needed.
