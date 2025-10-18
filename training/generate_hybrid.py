#!/usr/bin/env python3
"""
Hybrid Q&A Generator - Generate 1M+ questions NOW
Uses: Exam patterns + Groq API + Ecuadorian legal knowledge
"""
import json
import os
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
import time
from groq import Groq

# Real exam questions as seed
EXAM_SEEDS = [
    {"q": "¿Cuál es la tarifa del IVA en Ecuador?", "domain": "tributacion"},
    {"q": "¿Qué es el Impuesto a la Renta?", "domain": "tributacion"},
    {"q": "¿Quién es el sujeto activo en materia tributaria?", "domain": "tributacion"},
    {"q": "¿Cuál es la tarifa del Impuesto a la Salida de Divisas?", "domain": "tributacion"},
    {"q": "¿Qué productos tienen tarifa 0% de IVA?", "domain": "tributacion"},
    {"q": "¿Cuándo una empresa está obligada a llevar contabilidad?", "domain": "contabilidad"},
    {"q": "¿Qué son las normas de auditoría?", "domain": "auditoria"},
    {"q": "¿Qué es el control interno?", "domain": "auditoria"},
    {"q": "¿Qué es el punto de equilibrio?", "domain": "costos"},
    {"q": "¿Qué es el costeo ABC?", "domain": "costos"},
]

GENERATION_PROMPT = """Eres un experto en derecho tributario, contabilidad y auditoría ecuatoriana.

Genera {num} preguntas y respuestas DIFERENTES sobre {domain} en Ecuador, similares a esta pregunta ejemplo:
"{example_q}"

REQUISITOS:
- Preguntas tipo examen profesional (contador/auditor)
- Respuestas precisas con leyes ecuatorianas (LRTI, Código Tributario, NIIF, etc.)
- Incluye números, porcentajes, artículos cuando sea apropiado
- Varía: opción múltiple, casos prácticos, interpretación legal, cálculos
- TODAS las preguntas deben ser DIFERENTES entre sí

FORMATO JSON (solo el array, sin texto adicional):
[
  {{
    "instruction": "pregunta única aquí",
    "input": "",
    "output": "respuesta detallada con base legal",
    "category": "{domain}",
    "type": "multiple_choice"
  }}
]

Genera {num} preguntas ÚNICAS en JSON:"""

def generate_batch_with_groq(client: Groq, seed: Dict, batch_size: int = 20) -> List[Dict]:
    """Generate batch of Q&A from seed question"""
    
    prompt = GENERATION_PROMPT.format(
        num=batch_size,
        domain=seed["domain"],
        example_q=seed["q"]
    )
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres experto en derecho ecuatoriano. Respondes SOLO con JSON válido."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.9,  # Higher for more variety
            max_tokens=4000,
        )
        
        text = response.choices[0].message.content.strip()
        
        # Clean markdown
        if text.startswith("```"):
            text = '\n'.join(text.split('\n')[1:-1])
        
        # Extract JSON
        start = text.find('[')
        end = text.rfind(']') + 1
        
        if start != -1 and end > start:
            qa_pairs = json.loads(text[start:end])
            return qa_pairs
        
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    return []

def generate_hybrid_dataset(client: Groq, target_count: int = 100000) -> List[Dict]:
    """Generate large dataset using hybrid approach"""
    
    synthetic = []
    batch_size = 20  # Questions per API call
    
    print(f"🎯 Target: {target_count:,} questions")
    print(f"🌱 Using {len(EXAM_SEEDS)} seed questions")
    print(f"🤖 Model: Llama 3.3 70B via Groq")
    
    pbar = tqdm(total=target_count, desc="Generating")
    
    iteration = 0
    while len(synthetic) < target_count:
        # Rotate through seed questions
        seed = EXAM_SEEDS[iteration % len(EXAM_SEEDS)]
        
        # Generate batch
        qa_pairs = generate_batch_with_groq(client, seed, batch_size)
        
        if qa_pairs:
            for qa in qa_pairs:
                if len(synthetic) >= target_count:
                    break
                qa["source"] = f"generated_from_{seed['domain']}"
                synthetic.append(qa)
                pbar.update(1)
        
        iteration += 1
        
        # Rate limit (Groq free tier: 30 req/min)
        time.sleep(2)
        
        # Save checkpoint every 10K
        if len(synthetic) % 10000 == 0 and len(synthetic) > 0:
            checkpoint_file = Path("./quality_synthetic_data") / f"checkpoint_{len(synthetic)}.jsonl"
            checkpoint_file.parent.mkdir(exist_ok=True)
            save_jsonl(synthetic[-10000:], checkpoint_file)
            print(f"\n💾 Checkpoint saved: {len(synthetic):,} questions")
    
    pbar.close()
    return synthetic

def save_jsonl(data: List[Dict], output_file: Path):
    """Save to JSONL"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        print("❌ Set GROQ_API_KEY first!")
        print("   export GROQ_API_KEY='your_key'")
        return
    
    client = Groq(api_key=api_key)
    output_dir = Path("./quality_synthetic_data")
    output_dir.mkdir(exist_ok=True)
    
    # Generate in batches
    batch_size = 50000  # 50K per file
    total_target = 1000000  # 1M total
    
    for batch_num in range(total_target // batch_size):
        print(f"\n{'='*60}")
        print(f"📦 BATCH {batch_num + 1}/{total_target // batch_size}")
        print(f"{'='*60}")
        
        synthetic = generate_hybrid_dataset(client, batch_size)
        
        if not synthetic:
            print("❌ Generation failed")
            break
        
        output_file = output_dir / f"hybrid_batch_{batch_num + 1:02d}.jsonl"
        save_jsonl(synthetic, output_file)
        
        print(f"\n✅ Saved {len(synthetic):,} questions")
        print(f"   File: {output_file}")
        print(f"   Size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
        
        # Show samples
        if synthetic:
            print(f"\n📝 Sample questions:")
            for i, sample in enumerate(synthetic[:3], 1):
                print(f"\n   {i}. Q: {sample['instruction'][:80]}...")
                print(f"      A: {sample['output'][:80]}...")
    
    print(f"\n{'='*60}")
    print(f"🎉 COMPLETE! Generated {total_target:,} questions")
    print(f"📁 Location: {output_dir}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
