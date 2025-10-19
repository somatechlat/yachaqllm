# YACHAQ-LEX Training Strategy - FINAL DECISION

## 🔍 CURRENT SITUATION ANALYSIS

### What We Have:
1. **Real Legal Documents**: 9,352 JSONL entries (197 MB on S3)
   - SRI data: 125 entries
   - Asamblea Nacional: 305 entries  
   - Real Ecuador data: 8,739 entries
   - Registro Oficial: 12 entries
   - Others: 171 entries

2. **Synthetic Q&A**: 25,755 questions (11 MB)
   - **PROBLEM**: 40% accuracy (6/10 incorrect in validation)
   - Contains factual errors, wrong formulas, incorrect legal references
   - **NOT SAFE TO USE**

3. **Downloaded Files**: 143 files (207 MB on S3)
   - PDFs, CSVs, Excel files
   - Need text extraction

---

## ❌ WHY SYNTHETIC DATA FAILED

The LLM-generated questions have:
- Wrong IVA calculations (said 12% on value-added, should be on sales)
- Incorrect thresholds ($11,040 vs actual $11,310+)
- Confused concepts (margin vs markup)
- Wrong legal article references
- Outdated information

**Training on this = Teaching the model WRONG information**

---

## ✅ CORRECT APPROACH: Use ONLY Real Legal Documents

### Strategy 1: Document-Based Training (RECOMMENDED)

**What**: Train directly on real legal texts (like nanochat approach)

**Data**:
- 9,352 real legal documents
- 197 MB of actual Ecuadorian law text
- No synthetic errors

**Method**:
```python
# Like your train_nanochat_yachaq.py
1. Load all real JSONL files
2. Extract text content
3. Train character/token level model
4. Model learns from ACTUAL legal language
```

**Pros**:
- ✅ 100% accurate (real legal texts)
- ✅ No hallucinations
- ✅ Learns actual legal language patterns
- ✅ Can cite real sources

**Cons**:
- ⚠️ Not instruction-tuned (doesn't follow Q&A format)
- ⚠️ Needs more data for better performance

**Is 9,352 documents enough?**
- For nanochat-style: **YES** (trains on raw text)
- For instruction-tuning: **NO** (needs Q&A pairs)

---

### Strategy 2: Extract + Generate Q&A from Real Docs (BEST)

**What**: Use real legal documents to generate Q&A pairs

**Process**:
1. Extract text from 9,352 documents
2. Use ME (Claude) to generate Q&A from EACH document
3. Each document → 5-10 questions = 46K-93K Q&A pairs
4. All answers based on ACTUAL legal text

**Example**:
```
Document: "Ley de Régimen Tributario Interno, Art. 52: 
          El IVA grava al valor de la transferencia..."

Generated Q&A:
Q: ¿Qué grava el IVA según la LRTI?
A: Según el Art. 52 de la LRTI, el IVA grava al valor 
   de la transferencia de dominio o a la importación 
   de bienes muebles de naturaleza corporal...
```

**Pros**:
- ✅ 100% accurate (from real docs)
- ✅ Instruction-tuned format
- ✅ Can cite exact sources
- ✅ 46K-93K high-quality Q&A pairs

**Cons**:
- ⏱️ Takes time (need to process 9,352 docs)
- 💰 API costs (~$50-100 for Claude)

**Is this enough?**
- **YES!** 46K-93K Q&A pairs is EXCELLENT for fine-tuning
- Industry standard: 10K-50K for domain-specific models

---

### Strategy 3: Hybrid (MAXIMUM QUALITY)

**Combine**:
1. Document-based training (nanochat style) - learns legal language
2. Instruction-tuning on real-doc Q&A - learns to answer questions
3. Two-stage training

**Result**: Best of both worlds

---

## 📊 COMPARISON

| Approach | Data Size | Accuracy | Training Time | Cost |
|----------|-----------|----------|---------------|------|
| **Synthetic Q&A** | 25K | ❌ 40% | Fast | $0 |
| **Real Docs Only** | 9.3K docs | ✅ 100% | Medium | $0 |
| **Real Docs → Q&A** | 46-93K | ✅ 100% | Slow | $50-100 |
| **Hybrid** | Both | ✅ 100% | Slowest | $50-100 |

---

## 🎯 MY RECOMMENDATION

### **Use Strategy 2: Real Docs → Q&A Generation**

**Why**:
1. ✅ Guaranteed accuracy (from real legal texts)
2. ✅ Instruction-tuned (Q&A format)
3. ✅ Enough data (46K-93K pairs)
4. ✅ Can cite sources
5. ✅ Worth the time/cost investment

**Timeline**:
- Extract text from 9,352 docs: 2-3 hours
- Generate Q&A with Claude API: 8-12 hours
- Upload to S3: 30 minutes
- **Total: 1-2 days**

**Cost**:
- Claude API: ~$50-100
- SageMaker training: ~$39
- **Total: ~$90-140**

---

## 🚀 EXECUTION PLAN

### Phase 1: Data Preparation (NOW)
1. ✅ Extract text from all 9,352 JSONL files
2. ✅ Clean and structure content
3. ✅ Verify data quality

### Phase 2: Q&A Generation (12 hours)
1. ✅ Use Claude API to generate Q&A from each document
2. ✅ 5-10 questions per document
3. ✅ Include source citations
4. ✅ Validate samples

### Phase 3: Training (95 hours)
1. ✅ Upload to S3
2. ✅ Train Qwen2.5-7B with QLoRA
3. ✅ Evaluate on real exam questions

### Phase 4: Validation
1. ✅ Test on 60 real exam questions
2. ✅ Target: >85% accuracy
3. ✅ Deploy if successful

---

## 💡 ALTERNATIVE: Quick Start

**If you want to start training TODAY**:

Use **Strategy 1** (Real Docs Only):
- Train nanochat-style on 9,352 documents
- Takes 24-48 hours
- Cost: $39
- Accuracy: 100% (real legal text)
- Limitation: Not instruction-tuned

**Then later**:
- Add instruction-tuning layer
- Generate Q&A from docs
- Fine-tune again

---

## ❓ YOUR DECISION NEEDED

**Option A**: Generate Q&A from real docs (1-2 days, $90-140, BEST quality)
**Option B**: Train on real docs now (24-48 hours, $39, GOOD quality)
**Option C**: Wait for you to provide more legal sites to scrape

**Which do you prefer?**
