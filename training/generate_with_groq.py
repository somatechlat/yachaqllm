#!/usr/bin/env python3
"""
High-Quality Q&A Generator using Groq API
Fast and free tier available!
"""
import json
import os
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
import time

try:
    from groq import Groq
except ImportError:
    print("Installing groq...")
    os.system("pip install groq -q")
    from groq import Groq

GENERATION_PROMPT = """Eres un experto en derecho tributario, contabilidad y auditoría ecuatoriana.

Basándote en el siguiente texto legal ecuatoriano, genera {num_questions} preguntas y respuestas de alta calidad en español.

TEXTO LEGAL:
{legal_text}

INSTRUCCIONES:
1. Las preguntas deben ser similares a exámenes de contadores y auditores
2. Incluye preguntas sobre: tributación, auditoría, contabilidad, costos
3. Las respuestas deben ser precisas y basadas SOLO en el texto proporcionado
4. Incluye citas legales cuando sea apropiado
5. Varía los tipos: opción múltiple, interpretación legal, casos prácticos

FORMATO DE SALIDA (JSON válido):
[
  {{
    "instruction": "¿Cuál es la tarifa del IVA en Ecuador?",
    "input": "",
    "output": "Respuesta detallada basada en el texto...",
    "category": "tributacion",
    "type": "multiple_choice"
  }}
]

Genera EXACTAMENTE {num_questions} pares en formato JSON válido (solo el array JSON, sin texto adicional):"""

def load_real_data(data_dir: Path) -> List[Dict]:
    """Load all JSONL files with content"""
    data = []
    for jsonl_file in data_dir.glob("*.jsonl"):
        if jsonl_file.stat().st_size == 0:
            continue
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        if item.get("content") and len(item["content"]) > 200:
                            data.append(item)
        except Exception as e:
            continue
    return data

def generate_qa_with_groq(client: Groq, legal_text: str, num_questions: int = 5) -> List[Dict]:
    """Generate Q&A pairs using Groq API"""
    
    prompt = GENERATION_PROMPT.format(
        num_questions=num_questions,
        legal_text=legal_text[:4000]  # Limit context
    )
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto en derecho ecuatoriano. Respondes SOLO con JSON válido."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",  # Latest Llama model
            temperature=0.7,
            max_tokens=4000,
        )
        
        response_text = chat_completion.choices[0].message.content
        
        # Extract JSON from response
        response_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])
        
        # Find JSON array
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        
        if start != -1 and end > start:
            json_str = response_text[start:end]
            qa_pairs = json.loads(json_str)
            return qa_pairs
        else:
            print(f"⚠️  No JSON found in response")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def generate_quality_dataset(
    client: Groq,
    real_data: List[Dict], 
    target_count: int = 10000,
    questions_per_doc: int = 5
) -> List[Dict]:
    """Generate high-quality Q&A dataset"""
    
    synthetic = []
    docs_needed = (target_count // questions_per_doc) + 100  # Extra buffer
    
    print(f"🎯 Target: {target_count:,} questions")
    print(f"📄 Processing documents...")
    print(f"🤖 Using: Groq API (Llama 3.1 70B)")
    
    # Process documents
    import random
    random.shuffle(real_data)
    
    pbar = tqdm(total=target_count, desc="Generating Q&A")
    
    for doc in real_data[:docs_needed]:
        if len(synthetic) >= target_count:
            break
            
        content = doc.get("content", "")
        if len(content) < 200:
            continue
        
        # Generate Q&A pairs for this document
        qa_pairs = generate_qa_with_groq(client, content, questions_per_doc)
        
        if qa_pairs:
            for qa in qa_pairs:
                if len(synthetic) >= target_count:
                    break
                qa["source"] = doc.get("source", "unknown")
                synthetic.append(qa)
                pbar.update(1)
        
        # Rate limiting (Groq free tier)
        time.sleep(0.1)
    
    pbar.close()
    return synthetic[:target_count]

def save_jsonl(data: List[Dict], output_file: Path):
    """Save data to JSONL"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    # Get API key from environment
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        print("❌ GROQ_API_KEY not set!")
        print("   Run: export GROQ_API_KEY='your_key_here'")
        return
    
    # Initialize client
    client = Groq(api_key=api_key)
    
    data_dir = Path("../rag/ingest")
    output_dir = Path("./quality_synthetic_data")
    output_dir.mkdir(exist_ok=True)
    
    # Load real data
    print("\n📂 Loading real data...")
    real_data = load_real_data(data_dir)
    print(f"✅ Loaded {len(real_data):,} documents with content")
    
    if len(real_data) < 10:
        print("❌ Not enough data. Need at least 10 documents.")
        return
    
    # Generate in batches
    batch_size = 10000  # 10K per batch
    total_target = 100000  # 100K total (can scale to 1M+)
    
    for batch_num in range(total_target // batch_size):
        print(f"\n📦 Batch {batch_num + 1}/{total_target // batch_size}")
        
        synthetic = generate_quality_dataset(
            client,
            real_data,
            target_count=batch_size,
            questions_per_doc=5
        )
        
        if not synthetic:
            print("❌ No questions generated.")
            break
        
        output_file = output_dir / f"quality_batch_{batch_num + 1:02d}.jsonl"
        save_jsonl(synthetic, output_file)
        
        print(f"✅ Saved {len(synthetic):,} questions to {output_file}")
        print(f"   File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
        
        # Show sample
        if synthetic:
            print(f"\n📝 Sample question:")
            sample = synthetic[0]
            print(f"   Q: {sample['instruction'][:100]}...")
            print(f"   A: {sample['output'][:100]}...")
    
    print(f"\n🎉 Complete! Generated {min(len(synthetic) * (batch_num + 1), total_target):,} questions")

if __name__ == "__main__":
    main()
