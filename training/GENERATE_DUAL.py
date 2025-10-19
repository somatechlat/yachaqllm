#!/usr/bin/env python3
"""
DUAL API Generator - Uses BOTH Groq + Google AI
Respects rate limits on both services
"""
import json
import os
from pathlib import Path
from groq import Groq
import google.generativeai as genai
import time
from datetime import datetime

# Setup APIs
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
gemini = genai.GenerativeModel('gemini-2.5-flash')

output_dir = Path("quality_synthetic_data")
output_dir.mkdir(exist_ok=True)

# RATE LIMITS (Conservative)
GROQ_RPM = 25  # 30 max, use 25
GROQ_DAILY = 14000  # 14.4K max
GOOGLE_RPM = 14  # 15 max, use 14
GOOGLE_DAILY = 100000  # Very high

GROQ_DELAY = 60 / GROQ_RPM  # 2.4s
GOOGLE_DELAY = 60 / GOOGLE_RPM  # 4.3s

# Counters
groq_count = 0
google_count = 0
groq_last_call = 0
google_last_call = 0

DOMAINS = {
    "tributacion": "IVA, Renta, ICE, Divisas, RUC",
    "auditoria": "normas, control, riesgo, evidencia",
    "contabilidad": "NIIF, activos, pasivos, estados",
    "costos": "fijos, variables, equilibrio, ABC"
}

def generate_groq(domain, topics, n=15):
    """Generate with Groq"""
    global groq_count, groq_last_call
    
    # Rate limit check
    elapsed = time.time() - groq_last_call
    if elapsed < GROQ_DELAY:
        time.sleep(GROQ_DELAY - elapsed)
    
    if groq_count >= GROQ_DAILY:
        return None
    
    prompt = f"""Experto {domain} Ecuador. {n} preguntas ÚNICAS.
JSON: [{{"instruction":"q","input":"","output":"a","category":"{domain}","type":"multiple_choice"}}]
Temas: {topics}. Solo JSON:"""
    
    try:
        r = groq_client.chat.completions.create(
            messages=[{"role":"user","content":prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.85,
            max_tokens=2500,
        )
        
        groq_count += 1
        groq_last_call = time.time()
        
        t = r.choices[0].message.content.strip()
        if '```' in t:
            t = '\n'.join([l for l in t.split('\n') if not l.startswith('```')])
        
        s = t.find('[')
        e = t.rfind(']') + 1
        if s != -1 and e > s:
            return json.loads(t[s:e]), 'groq'
    except Exception as e:
        print(f"⚠️ Groq: {e}")
    
    return None, None

def generate_google(domain, topics, n=15):
    """Generate with Google"""
    global google_count, google_last_call
    
    # Rate limit check
    elapsed = time.time() - google_last_call
    if elapsed < GOOGLE_DELAY:
        time.sleep(GOOGLE_DELAY - elapsed)
    
    if google_count >= GOOGLE_DAILY:
        return None
    
    prompt = f"""Experto {domain} Ecuador. {n} preguntas ÚNICAS.
JSON: [{{"instruction":"q","input":"","output":"a","category":"{domain}","type":"multiple_choice"}}]
Temas: {topics}. Solo JSON:"""
    
    try:
        r = gemini.generate_content(prompt)
        
        google_count += 1
        google_last_call = time.time()
        
        t = r.text.strip()
        if '```' in t:
            t = '\n'.join([l for l in t.split('\n') if not l.startswith('```')])
        
        s = t.find('[')
        e = t.rfind(']') + 1
        if s != -1 and e > s:
            return json.loads(t[s:e]), 'google'
    except Exception as e:
        print(f"⚠️ Google: {e}")
    
    return None, None

# Main generation
TARGET = 100000
all_qa = []
domains_list = list(DOMAINS.items())
start_time = time.time()

print(f"🚀 DUAL API Generator")
print(f"🎯 Target: {TARGET:,} questions")
print(f"⚡ Groq: {GROQ_RPM} RPM, {GROQ_DAILY:,}/day")
print(f"⚡ Google: {GOOGLE_RPM} RPM, {GOOGLE_DAILY:,}/day")
print(f"📊 Combined: ~{GROQ_RPM + GOOGLE_RPM} RPM = ~{(GROQ_RPM + GOOGLE_RPM)*15:,} q/hour")
print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}\n")

i = 0
use_groq = True  # Alternate between APIs

while len(all_qa) < TARGET:
    domain, topics = domains_list[i % len(domains_list)]
    
    # Alternate APIs
    if use_groq and groq_count < GROQ_DAILY:
        qa, api = generate_groq(domain, topics, 15)
        use_groq = False
    elif google_count < GOOGLE_DAILY:
        qa, api = generate_google(domain, topics, 15)
        use_groq = True
    else:
        print("⚠️ Both APIs exhausted!")
        break
    
    if qa:
        all_qa.extend(qa)
        
        elapsed = time.time() - start_time
        rate = len(all_qa) / (elapsed / 60) if elapsed > 0 else 0
        eta_min = (TARGET - len(all_qa)) / rate if rate > 0 else 0
        
        pct = (len(all_qa) / TARGET) * 100
        print(f"✅ {len(all_qa):,}/{TARGET:,} ({pct:.1f}%) | {api:6} | G:{groq_count} Gem:{google_count} | {rate:.0f}q/m | ETA:{eta_min:.0f}m")
    
    i += 1
    
    # Checkpoint every 10K
    if len(all_qa) % 10000 == 0 and len(all_qa) > 0:
        cp = output_dir / f"dual_{len(all_qa)//1000}k.jsonl"
        with open(cp, 'w', encoding='utf-8') as f:
            for q in all_qa[-10000:]:
                f.write(json.dumps(q, ensure_ascii=False) + '\n')
        print(f"💾 Checkpoint: {cp.name}")

# Final save
final = output_dir / f"yachaq_dual_{len(all_qa)}.jsonl"
with open(final, 'w', encoding='utf-8') as f:
    for q in all_qa:
        f.write(json.dumps(q, ensure_ascii=False) + '\n')

elapsed_min = (time.time() - start_time) / 60
print(f"\n{'='*70}")
print(f"🎉 COMPLETE!")
print(f"📊 Generated: {len(all_qa):,} questions")
print(f"⏱️  Time: {elapsed_min:.1f} minutes ({elapsed_min/60:.1f} hours)")
print(f"📈 Rate: {len(all_qa)/elapsed_min:.0f} questions/min")
print(f"🔄 Groq calls: {groq_count}/{GROQ_DAILY}")
print(f"🔄 Google calls: {google_count}/{GOOGLE_DAILY}")
print(f"📁 File: {final}")
print(f"💾 Size: {final.stat().st_size/1024/1024:.1f} MB")
print(f"{'='*70}")
