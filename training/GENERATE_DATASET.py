#!/usr/bin/env python3
"""
YACHAQ-LEX Dataset Generator
Generates 100K+ high-quality Q&A pairs for training
"""
import json
import os
from pathlib import Path
from groq import Groq
import time

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
output_dir = Path("quality_synthetic_data")
output_dir.mkdir(exist_ok=True)

PROMPT_TEMPLATE = """Eres experto en {domain} ecuatoriana. Genera {n} preguntas ÚNICAS y respuestas detalladas.

Ejemplo:
[{{"instruction": "pregunta aquí", "input": "", "output": "respuesta detallada", "category": "{domain}", "type": "multiple_choice"}}]

Temas: {topics}

Genera {n} preguntas DIFERENTES. Solo JSON:"""

DOMAINS = {
    "tributacion": "IVA, Impuesto a la Renta, ICE, Impuesto Salida Divisas, RUC, retenciones, declaraciones, LRTI, Código Tributario",
    "auditoria": "normas auditoría, control interno, riesgo, evidencia, papeles trabajo, fraude, COSO, procedimientos analíticos",
    "contabilidad": "NIIF, NIC, devengado, activos, pasivos, patrimonio, estados financieros, depreciación, amortización",
    "costos": "costo primo, conversión, fijos, variables, punto equilibrio, costeo ABC, órdenes, procesos, estándares"
}

def generate_batch(domain, topics, n=20):
    prompt = PROMPT_TEMPLATE.format(domain=domain, n=n, topics=topics)
    
    try:
        r = client.chat.completions.create(
            messages=[{"role":"user","content":prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.85,
            max_tokens=4000,
        )
        
        t = r.choices[0].message.content.strip()
        if '```' in t:
            t = '\n'.join([l for l in t.split('\n') if not l.startswith('```')])
        
        s = t.find('[')
        e = t.rfind(']') + 1
        if s != -1 and e > s:
            return json.loads(t[s:e])
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    return []

# Main generation
TARGET = 100000
all_qa = []
domains_list = list(DOMAINS.items())

print(f"🚀 YACHAQ-LEX Dataset Generation")
print(f"🎯 Target: {TARGET:,} questions")
print(f"📚 Domains: {len(domains_list)}")
print(f"🤖 Model: Llama 3.3 70B\n")

i = 0
while len(all_qa) < TARGET:
    domain, topics = domains_list[i % len(domains_list)]
    
    qa = generate_batch(domain, topics, n=20)
    
    if qa:
        all_qa.extend(qa)
        pct = (len(all_qa) / TARGET) * 100
        print(f"✅ {len(all_qa):,}/{TARGET:,} ({pct:.1f}%) | {domain} | {qa[0]['instruction'][:50]}...")
    else:
        print(f"⚠️  Failed batch {i}")
    
    i += 1
    time.sleep(1.5)  # Rate limit
    
    # Checkpoint every 10K
    if len(all_qa) % 10000 == 0 and len(all_qa) > 0:
        checkpoint = output_dir / f"checkpoint_{len(all_qa)//1000}k.jsonl"
        with open(checkpoint, 'w', encoding='utf-8') as f:
            for q in all_qa[-10000:]:
                f.write(json.dumps(q, ensure_ascii=False) + '\n')
        print(f"💾 Checkpoint: {checkpoint.name}")

# Final save
final_file = output_dir / f"yachaq_lex_{len(all_qa)}.jsonl"
with open(final_file, 'w', encoding='utf-8') as f:
    for q in all_qa[:TARGET]:
        f.write(json.dumps(q, ensure_ascii=False) + '\n')

print(f"\n{'='*60}")
print(f"🎉 COMPLETE!")
print(f"📊 Generated: {len(all_qa[:TARGET]):,} questions")
print(f"📁 File: {final_file}")
print(f"💾 Size: {final_file.stat().st_size/1024/1024:.1f} MB")
print(f"{'='*60}")
