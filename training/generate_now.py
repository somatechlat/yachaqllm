#!/usr/bin/env python3
"""Quick generator - Start generating NOW"""
import json
import os
from pathlib import Path
from groq import Groq
import time

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SEEDS = [
    {"q": "¿Cuál es la tarifa del IVA?", "d": "tributacion"},
    {"q": "¿Qué es el Impuesto a la Renta?", "d": "tributacion"},
    {"q": "¿Quién es el sujeto activo?", "d": "tributacion"},
    {"q": "¿Qué es el control interno?", "d": "auditoria"},
    {"q": "¿Qué son las normas de auditoría?", "d": "auditoria"},
    {"q": "¿Cuándo llevar contabilidad?", "d": "contabilidad"},
    {"q": "¿Qué es el punto de equilibrio?", "d": "costos"},
]

def gen(seed, n=15):
    prompt = f"""Genera {n} preguntas DIFERENTES sobre {seed['d']} Ecuador, similares a: {seed['q']}

JSON: [{{"instruction":"pregunta","input":"","output":"respuesta","category":"{seed['d']}","type":"multiple_choice"}}]

Solo JSON:"""
    
    try:
        r = client.chat.completions.create(
            messages=[
                {"role":"system","content":"JSON válido solo"},
                {"role":"user","content":prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.9,
            max_tokens=3000,
        )
        
        t = r.choices[0].message.content.strip()
        if '```' in t:
            t = '\n'.join(t.split('\n')[1:-1])
        
        s = t.find('[')
        e = t.rfind(']') + 1
        if s != -1 and e > s:
            return json.loads(t[s:e])
    except:
        pass
    return []

# Generate
output_dir = Path("quality_synthetic_data")
output_dir.mkdir(exist_ok=True)

target = 10000  # Start with 10K
all_qa = []

print(f"🎯 Generating {target:,} questions...")
print(f"🤖 Using Groq API\n")

i = 0
while len(all_qa) < target:
    seed = SEEDS[i % len(SEEDS)]
    
    qa = gen(seed, 15)
    if qa:
        all_qa.extend(qa)
        print(f"✅ {len(all_qa):,}/{target:,} - Last: {qa[0]['instruction'][:60]}...")
    
    i += 1
    time.sleep(1)  # Rate limit
    
    # Save checkpoint every 1000
    if len(all_qa) % 1000 == 0 and len(all_qa) > 0:
        f = output_dir / f"batch_{len(all_qa)//1000:03d}.jsonl"
        with open(f, 'w') as file:
            for q in all_qa[-1000:]:
                file.write(json.dumps(q, ensure_ascii=False) + '\n')
        print(f"💾 Saved checkpoint: {f.name}")

# Final save
final = output_dir / "yachaq_10k.jsonl"
with open(final, 'w') as f:
    for q in all_qa[:target]:
        f.write(json.dumps(q, ensure_ascii=False) + '\n')

print(f"\n🎉 Done! {len(all_qa[:target]):,} questions")
print(f"📁 {final}")
print(f"📊 Size: {final.stat().st_size/1024/1024:.1f} MB")
