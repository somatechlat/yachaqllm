#!/usr/bin/env python3
"""
Synthetic Question Generator for YACHAQ-LEX
Generates 3-4M training questions from scraped Ecuadorian legal data
"""
import json
import random
import re
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

# Question templates based on exam patterns
TEMPLATES = {
    "multiple_choice": [
        "¿Cuál es {concept} según {source}?",
        "¿Qué establece {source} sobre {concept}?",
        "Según {source}, ¿cuál es {concept}?",
        "¿Cómo se define {concept} en {source}?",
        "De acuerdo a {source}, {concept} es:",
    ],
    "legal_interpretation": [
        "Explica el concepto de {concept} según la legislación ecuatoriana",
        "¿Qué significa {concept} en el contexto de {domain}?",
        "Define {concept} conforme a {source}",
        "Interpreta el artículo que trata sobre {concept}",
    ],
    "case_analysis": [
        "Una empresa {scenario}. ¿{question}?",
        "Un contribuyente {scenario}. ¿Cuál es {question}?",
        "En el caso de {scenario}, ¿qué establece {source}?",
        "Si {scenario}, ¿cuál sería {question}?",
    ],
    "citation": [
        "¿Qué artículo de {source} regula {concept}?",
        "¿En qué normativa se encuentra {concept}?",
        "Cita la base legal de {concept}",
        "¿Cuál es el fundamento legal de {concept}?",
    ],
    "calculation": [
        "Calcula {concept} si {scenario}",
        "¿Cuál es el valor de {concept} cuando {scenario}?",
        "Determina {concept} en el siguiente caso: {scenario}",
    ],
    "comparison": [
        "¿Cuál es la diferencia entre {concept1} y {concept2}?",
        "Compara {concept1} con {concept2}",
        "¿En qué se diferencian {concept1} y {concept2}?",
    ],
    "procedure": [
        "¿Cuál es el procedimiento para {concept}?",
        "¿Cómo se realiza {concept}?",
        "Describe los pasos para {concept}",
        "¿Qué requisitos se necesitan para {concept}?",
    ]
}

# Domain-specific concepts
CONCEPTS = {
    "tributacion": [
        "la tarifa del IVA", "el Impuesto a la Renta", "el sujeto activo",
        "el sujeto pasivo", "la base imponible", "el hecho generador",
        "las retenciones en la fuente", "el crédito tributario",
        "la declaración de impuestos", "el RUC", "las exenciones tributarias",
        "los impuestos directos", "los impuestos indirectos",
        "el Impuesto a la Salida de Divisas", "el ICE",
        "la obligación de llevar contabilidad", "las infracciones tributarias",
        "las sanciones tributarias", "el proceso de determinación",
    ],
    "auditoria": [
        "las normas de auditoría", "el riesgo de auditoría", "la evidencia",
        "los papeles de trabajo", "el control interno", "la materialidad",
        "el muestreo de auditoría", "el informe de auditoría",
        "la planificación de auditoría", "los procedimientos analíticos",
        "el fraude", "el gobierno corporativo", "la evaluación de riesgos",
    ],
    "contabilidad": [
        "el principio de devengado", "los activos", "los pasivos",
        "el patrimonio", "los ingresos", "los gastos", "la depreciación",
        "la amortización", "el estado de situación financiera",
        "el estado de resultados", "el flujo de efectivo",
        "las NIIF", "las NIC", "el plan de cuentas",
    ],
    "costos": [
        "el costo primo", "el costo de conversión", "los costos fijos",
        "los costos variables", "el punto de equilibrio", "el margen de contribución",
        "el costeo por órdenes", "el costeo por procesos", "el costeo ABC",
        "los costos estándar", "las variaciones", "el costo de producción",
    ]
}

SOURCES = [
    "la Ley de Régimen Tributario Interno",
    "el Código Tributario",
    "el Reglamento de Aplicación LRTI",
    "la Ley Orgánica de Régimen Tributario Interno",
    "las Normas Internacionales de Información Financiera",
    "el Registro Oficial",
    "la Superintendencia de Compañías",
    "el Servicio de Rentas Internas",
]

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
                        data.append(json.loads(line))
        except Exception as e:
            print(f"Error loading {jsonl_file}: {e}")
    return data

def extract_concepts_from_text(text: str) -> List[str]:
    """Extract key concepts from legal text"""
    # Simple keyword extraction
    keywords = []
    patterns = [
        r'artículo\s+\d+',
        r'impuesto\s+\w+',
        r'tarifa\s+del?\s+\d+%',
        r'\$\s*[\d,]+',
    ]
    for pattern in patterns:
        keywords.extend(re.findall(pattern, text.lower()))
    return keywords[:5]

def generate_multiple_choice(data_item: Dict) -> Dict:
    """Generate multiple choice question"""
    template = random.choice(TEMPLATES["multiple_choice"])
    domain = random.choice(list(CONCEPTS.keys()))
    concept = random.choice(CONCEPTS[domain])
    source = random.choice(SOURCES)
    
    question = template.format(concept=concept, source=source)
    
    # Use real data as answer context
    answer = data_item.get("content", "")[:500]
    if not answer:
        answer = f"Según {source}, {concept} se define como un elemento fundamental en {domain}."
    
    return {
        "instruction": question,
        "input": "",
        "output": answer,
        "source": data_item.get("source", "unknown"),
        "category": domain,
        "type": "multiple_choice"
    }

def generate_legal_interpretation(data_item: Dict) -> Dict:
    """Generate legal interpretation question"""
    template = random.choice(TEMPLATES["legal_interpretation"])
    domain = random.choice(list(CONCEPTS.keys()))
    concept = random.choice(CONCEPTS[domain])
    source = random.choice(SOURCES)
    
    question = template.format(concept=concept, domain=domain, source=source)
    answer = data_item.get("content", "")[:600]
    
    return {
        "instruction": question,
        "input": "",
        "output": answer,
        "source": data_item.get("source", "unknown"),
        "category": domain,
        "type": "interpretation"
    }

def generate_case_analysis(data_item: Dict) -> Dict:
    """Generate case analysis question"""
    scenarios = [
        "tiene ventas anuales de $120,000 y gastos de $90,000",
        "realiza exportaciones por $50,000 mensuales",
        "importa bienes por valor de $200,000",
        "tiene empleados en relación de dependencia",
        "es una PYME con capital de $80,000",
    ]
    questions = [
        "está obligada a llevar contabilidad",
        "debe declarar el IVA",
        "aplica retención en la fuente",
        "qué tarifa de IVA aplica",
        "debe pagar Impuesto a la Renta",
    ]
    
    scenario = random.choice(scenarios)
    question_text = random.choice(questions)
    
    question = f"Una empresa {scenario}. ¿{question_text}?"
    answer = data_item.get("content", "")[:500]
    
    return {
        "instruction": question,
        "input": "",
        "output": answer,
        "source": data_item.get("source", "unknown"),
        "category": "casos_practicos",
        "type": "case_analysis"
    }

def generate_citation(data_item: Dict) -> Dict:
    """Generate citation question"""
    template = random.choice(TEMPLATES["citation"])
    domain = random.choice(list(CONCEPTS.keys()))
    concept = random.choice(CONCEPTS[domain])
    source = random.choice(SOURCES)
    
    question = template.format(concept=concept, source=source)
    answer = f"El {concept} se encuentra regulado en {source}, específicamente en los artículos relacionados con {domain}."
    
    return {
        "instruction": question,
        "input": "",
        "output": answer,
        "source": data_item.get("source", "unknown"),
        "category": domain,
        "type": "citation"
    }

def generate_synthetic_questions(real_data: List[Dict], target_count: int = 100000) -> List[Dict]:
    """Generate synthetic questions from real data"""
    synthetic = []
    generators = [
        generate_multiple_choice,
        generate_legal_interpretation,
        generate_case_analysis,
        generate_citation,
    ]
    
    print(f"Generating {target_count:,} synthetic questions...")
    
    for i in tqdm(range(target_count)):
        data_item = random.choice(real_data)
        generator = random.choice(generators)
        
        try:
            question = generator(data_item)
            synthetic.append(question)
        except Exception as e:
            continue
    
    return synthetic

def save_jsonl(data: List[Dict], output_file: Path):
    """Save data to JSONL format"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    # Paths
    data_dir = Path("../rag/ingest")
    output_dir = Path("./synthetic_data")
    output_dir.mkdir(exist_ok=True)
    
    # Load real data
    print("Loading real data...")
    real_data = load_real_data(data_dir)
    print(f"Loaded {len(real_data):,} real data items")
    
    if len(real_data) < 100:
        print("⚠️  Not enough real data. Need at least 100 items.")
        return
    
    # Generate batches
    batch_size = 100000
    total_target = 1000000  # Start with 1M, can scale to 3-4M
    
    for batch_num in range(total_target // batch_size):
        print(f"\n📦 Generating batch {batch_num + 1}/{total_target // batch_size}")
        
        synthetic = generate_synthetic_questions(real_data, batch_size)
        
        output_file = output_dir / f"synthetic_batch_{batch_num + 1:02d}.jsonl"
        save_jsonl(synthetic, output_file)
        
        print(f"✅ Saved {len(synthetic):,} questions to {output_file}")
        print(f"   File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    print(f"\n🎉 Complete! Generated {total_target:,} synthetic questions")
    print(f"📁 Output directory: {output_dir}")

if __name__ == "__main__":
    main()
