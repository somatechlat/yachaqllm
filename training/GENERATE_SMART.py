#!/usr/bin/env python3
"""
Smart Generator - Respects Groq API Limits
Free Tier: 30 req/min, 6K tokens/min, 14.4K req/day
"""
import json
import os
from pathlib import Path
from groq import Groq
import time
from datetime import datetime

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
output_dir = Path("quality_synthetic_data")
output_dir.mkdir(exist_ok=True)

# GROQ LIMITS
MAX_REQUESTS_PER_MIN = 25  # Safe: 25 instead of 30
MAX_REQUESTS_PER_DAY = 14000  # Safe: 14K instead of 14.4K
DELAY_BETWEEN_REQUESTS = 2.5  # seconds (60/25 = 2.4)

DOMAINS = {
    "tributacion": "IVA, Impuesto Renta, ICE, Salida Divisas, RUC, retenciones",
    "auditoria": "normas, control interno, riesgo, evidencia, fraude, COSO",
    "contabilidad": "NIIF, NIC, activos, pasivos, estados financieros",
    "costos": "costo primo, fijos, variables, punto equilibrio, ABC"
}

def generate_batch(domain, topics, n=15):
    """Generate n questions (smaller batches for token limits)"""
    prompt = f"""Experto en {domain} Ecuador. Genera {n} preguntas ÚNICAS.

Ejemplo: [{{"instruction":"¿Cuál es la tarifa del IVA?","input":"","output":"12% y 0%","category":"{domain}","type":"multiple_choice"}}]

Temas: {topics}. Solo JSON:"""
    
    try:
        r = client.chat.completions.create(
            messages=[{"role":"user","content":prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.85,
            max_tokens=2500,  # Reduced for token limits
        )
        
        t = r.choices[0].message.content.strip()
        if '```' in t:
            t = '\n'.join([l for l in t.split('\n') if not l.startswith('```')])
        
        s = t.find('[')
        e = t.rfind(']') + 1
        if s != -1 and e > s:
            return json.loads(t[s:e])
    except Exception as e:
        print(f"⚠️  {e}")
    
    return []

# Calculate realistic daily target
REQUESTS_TODAY = 0
MAX_DAILY_QUESTIONS = MAX_REQUESTS_PER_DAY * 15  # 15 questions per request
print(f"🎯 Max questions per day: {MAX_DAILY_QUESTIONS:,} (210K)")
print(f"⏱️  Time needed: ~10 hours at 25 req/min")
print(f"💡 Running continuously will generate 210K/day\n")

TARGET = 50000  # Realistic: 50K in ~3.5 hours
all_qa = []
domains_list = list(DOMAINS.items())
start_time = time.time()

print(f"🚀 Starting generation: {TARGET:,} questions")
print(f"📊 Rate: 25 requests/min, 2.5s delay")
print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}\n")

i = 0
while len(all_qa) < TARGET and REQUESTS_TODAY < MAX_REQUESTS_PER_DAY:
    domain, topics = domains_list[i % len(domains_list)]
    
    qa = generate_batch(domain, topics, n=15)
    
    if qa:
        all_qa.extend(qa)
        REQUESTS_TODAY += 1
        
        elapsed = time.time() - start_time
        rate = len(all_qa) / (elapsed / 60) if elapsed > 0 else 0
        eta_min = (TARGET - len(all_qa)) / rate if rate > 0 else 0
        
        print(f"✅ {len(all_qa):,}/{TARGET:,} | {domain[:4]} | {rate:.0f}q/min | ETA:{eta_min:.0f}m | {qa[0]['instruction'][:45]}...")
    
    i += 1
    time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Checkpoint every 5K
    if len(all_qa) % 5000 == 0 and len(all_qa) > 0:
        cp = output_dir / f"checkpoint_{len(all_qa)//1000}k.jsonl"
        with open(cp, 'w', encoding='utf-8') as f:
            for q in all_qa[-5000:]:
                f.write(json.dumps(q, ensure_ascii=False) + '\n')
        print(f"💾 Saved: {cp.name}")

# Final save
final = output_dir / f"yachaq_{len(all_qa)}.jsonl"
with open(final, 'w', encoding='utf-8') as f:
    for q in all_qa:
        f.write(json.dumps(q, ensure_ascii=False) + '\n')

elapsed_min = (time.time() - start_time) / 60
print(f"\n{'='*70}")
print(f"🎉 COMPLETE!")
print(f"📊 Generated: {len(all_qa):,} questions")
print(f"⏱️  Time: {elapsed_min:.1f} minutes")
print(f"📈 Rate: {len(all_qa)/elapsed_min:.0f} questions/min")
print(f"📁 File: {final}")
print(f"💾 Size: {final.stat().st_size/1024/1024:.1f} MB")
print(f"🔄 Requests used: {REQUESTS_TODAY}/{MAX_REQUESTS_PER_DAY}")
print(f"{'='*70}")
