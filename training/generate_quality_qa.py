#!/usr/bin/env python3
"""
High-Quality Q&A Generator for YACHAQ-LEX
Uses LLM to generate matched question-answer pairs from real legal data
"""
import json
import random
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
import anthropic
import os

# Question types based on exam patterns
QUESTION_TYPES = [
    "multiple_choice",
    "legal_interpretation", 
    "case_analysis",
    "citation",
    "calculation",
    "comparison",
    "procedure"
]

GENERATION_PROMPT = """Eres un experto en derecho tributario, contabilidad y auditoría ecuatoriana.

Basándote en el siguiente texto legal ecuatoriano, genera {num_questions} preguntas y respuestas de alta calidad en español.

TEXTO LEGAL:
{legal_text}

INSTRUCCIONES:
1. Las preguntas deben ser similares a exámenes de contadores y auditores
2. Incluye preguntas sobre: tributación, auditoría, contabilidad, costos
3. Las respuestas deben ser precisas y basadas SOLO en el texto proporcionado
4. Incluye citas legales cuando sea apropiado
5. Varía los tipos: opción múltiple, interpretación legal, casos prácticos, cálculos

FORMATO DE SALIDA (JSON):
[
  {{
    "instruction": "¿Cuál es la tarifa del IVA en Ecuador?",
    "input": "",
    "output": "En Ecuador, el Impuesto al Valor Agregado (IVA) tiene dos tarifas: 12% para bienes y servicios gravados, y 0% para productos básicos como alimentos, medicinas y libros, según la Ley de Régimen Tributario Interno.",
    "category": "tributacion",
    "type": "multiple_choice"
  }}
]

Genera exactamente {num_questions} pares de pregunta-respuesta en formato JSON válido:"""

def load_real_data(data_dir: Path) -> List[Dict]:
    """Load all JSONL files"""
    data = []
    for jsonl_file in data_dir.glob("*.jsonl"):
        if jsonl_file.stat().st_size == 0:
            continue
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        if item.get("content"):  # Only items with content
                            data.append(item)
        except Exception as e:
            print(f"Error loading {jsonl_file}: {e}")
    return data

def generate_qa_with_llm(legal_text: str, num_questions: int = 5, use_api: bool = False) -> List[Dict]:
    """Generate Q&A pairs using LLM"""
    
    if use_api:
        # Use Claude API
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("⚠️  ANTHROPIC_API_KEY not set. Set it with: export ANTHROPIC_API_KEY=your_key")
            return []
        
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = GENERATION_PROMPT.format(
            num_questions=num_questions,
            legal_text=legal_text[:3000]  # Limit context
        )
        
        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Extract JSON from response
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                qa_pairs = json.loads(json_str)
                return qa_pairs
            
        except Exception as e:
            print(f"API Error: {e}")
            return []
    
    else:
        # Fallback: Use local Ollama (if available)
        try:
            import requests
            
            prompt = GENERATION_PROMPT.format(
                num_questions=num_questions,
                legal_text=legal_text[:2000]
            )
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:7b",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Extract JSON
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                if start != -1 and end > start:
                    json_str = response_text[start:end]
                    qa_pairs = json.loads(json_str)
                    return qa_pairs
                    
        except Exception as e:
            print(f"Local LLM Error: {e}")
            return []
    
    return []

def generate_quality_dataset(
    real_data: List[Dict], 
    target_count: int = 100000,
    questions_per_doc: int = 5,
    use_api: bool = False
) -> List[Dict]:
    """Generate high-quality Q&A dataset"""
    
    synthetic = []
    docs_needed = target_count // questions_per_doc
    
    print(f"🎯 Target: {target_count:,} questions")
    print(f"📄 Processing ~{docs_needed:,} documents")
    print(f"🤖 Using: {'Claude API' if use_api else 'Local Ollama'}")
    
    # Sample documents
    sampled_docs = random.sample(real_data, min(docs_needed, len(real_data)))
    
    for doc in tqdm(sampled_docs, desc="Generating Q&A"):
        content = doc.get("content", "")
        if len(content) < 100:
            continue
        
        # Generate Q&A pairs for this document
        qa_pairs = generate_qa_with_llm(content, questions_per_doc, use_api)
        
        if qa_pairs:
            for qa in qa_pairs:
                qa["source"] = doc.get("source", "unknown")
                synthetic.append(qa)
        
        if len(synthetic) >= target_count:
            break
    
    return synthetic[:target_count]

def save_jsonl(data: List[Dict], output_file: Path):
    """Save data to JSONL"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    data_dir = Path("../rag/ingest")
    output_dir = Path("./quality_synthetic_data")
    output_dir.mkdir(exist_ok=True)
    
    # Check for API key
    use_api = bool(os.environ.get("ANTHROPIC_API_KEY"))
    
    if not use_api:
        print("⚠️  No ANTHROPIC_API_KEY found. Will try local Ollama.")
        print("   To use Claude API: export ANTHROPIC_API_KEY=your_key")
        print("   To use Ollama: Install from https://ollama.ai and run: ollama pull qwen2.5:7b")
    
    # Load real data
    print("\n📂 Loading real data...")
    real_data = load_real_data(data_dir)
    print(f"✅ Loaded {len(real_data):,} documents with content")
    
    if len(real_data) < 10:
        print("❌ Not enough data. Need at least 10 documents.")
        return
    
    # Generate in batches
    batch_size = 10000  # 10K per batch
    total_target = 100000  # Start with 100K
    
    for batch_num in range(total_target // batch_size):
        print(f"\n📦 Batch {batch_num + 1}/{total_target // batch_size}")
        
        synthetic = generate_quality_dataset(
            real_data,
            target_count=batch_size,
            questions_per_doc=5,
            use_api=use_api
        )
        
        if not synthetic:
            print("❌ No questions generated. Check LLM setup.")
            break
        
        output_file = output_dir / f"quality_batch_{batch_num + 1:02d}.jsonl"
        save_jsonl(synthetic, output_file)
        
        print(f"✅ Saved {len(synthetic):,} questions to {output_file}")
        print(f"   File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    print(f"\n🎉 Complete!")

if __name__ == "__main__":
    main()
