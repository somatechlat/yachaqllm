#!/usr/bin/env python3
"""
Generate Q&A using Claude API (Amazon Q can help!)
Simple batch processor
"""
import json
from pathlib import Path
from typing import List, Dict

def load_real_data(data_dir: Path, limit: int = 100) -> List[Dict]:
    """Load sample of real data"""
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
                            if len(data) >= limit:
                                return data
        except:
            continue
    return data

def create_prompt_for_document(doc: Dict, num_questions: int = 10) -> str:
    """Create prompt for Q&A generation"""
    content = doc.get("content", "")[:3000]
    source = doc.get("source", "documento legal")
    
    prompt = f"""Eres un experto en derecho tributario, contabilidad y auditoría ecuatoriana.

Basándote en este texto legal de {source}, genera {num_questions} preguntas y respuestas de alta calidad.

TEXTO:
{content}

REQUISITOS:
- Preguntas tipo examen de contador/auditor
- Respuestas precisas basadas SOLO en el texto
- Incluye citas cuando sea apropiado
- Categorías: tributacion, auditoria, contabilidad, costos
- Tipos: multiple_choice, interpretation, case_analysis, citation

FORMATO JSON:
[
  {{
    "instruction": "pregunta aquí",
    "input": "",
    "output": "respuesta detallada aquí",
    "category": "tributacion",
    "type": "multiple_choice"
  }}
]

Genera {num_questions} pares en JSON válido:"""
    
    return prompt

def save_prompts_for_batch_processing(data: List[Dict], output_dir: Path):
    """Save prompts to files for manual/batch processing"""
    output_dir.mkdir(exist_ok=True)
    
    prompts_file = output_dir / "prompts_to_process.jsonl"
    
    with open(prompts_file, 'w', encoding='utf-8') as f:
        for i, doc in enumerate(data):
            prompt = create_prompt_for_document(doc, num_questions=10)
            f.write(json.dumps({
                "id": i,
                "source": doc.get("source", "unknown"),
                "prompt": prompt
            }, ensure_ascii=False) + '\n')
    
    print(f"✅ Saved {len(data)} prompts to {prompts_file}")
    print(f"\n📋 Next steps:")
    print(f"1. Use Claude API or Amazon Q to process these prompts")
    print(f"2. Save responses to: {output_dir}/responses/")
    print(f"3. Run merge script to combine into training data")

def main():
    data_dir = Path("../rag/ingest")
    output_dir = Path("./prompts_for_generation")
    
    print("📂 Loading sample documents...")
    data = load_real_data(data_dir, limit=1000)  # Start with 1000 docs
    print(f"✅ Loaded {len(data)} documents")
    
    print(f"\n🎯 Will generate ~{len(data) * 10:,} Q&A pairs")
    print(f"   (10 questions per document)")
    
    save_prompts_for_batch_processing(data, output_dir)
    
    # Show example
    print(f"\n📝 Example prompt:")
    print("=" * 60)
    example_prompt = create_prompt_for_document(data[0], 3)
    print(example_prompt[:500] + "...")

if __name__ == "__main__":
    main()
