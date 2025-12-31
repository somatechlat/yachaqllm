#!/usr/bin/env python3
"""
DATA QUALITY VALIDATOR
======================
Validates the 180K Q&A dataset for training quality metrics.
"""

import json
import random
from collections import defaultdict

INPUT_FILE = "data/instruction_dataset/train.jsonl"

def validate_dataset():
    print("=" * 70)
    print("  DATA QUALITY VALIDATION")
    print("=" * 70)
    
    # Load all data
    print("\n📚 Loading dataset...")
    data = []
    errors = []
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            try:
                item = json.loads(line)
                data.append(item)
            except json.JSONDecodeError as e:
                errors.append((i, str(e)))
    
    print(f"   Total lines: {len(data) + len(errors):,}")
    print(f"   Valid JSON: {len(data):,}")
    print(f"   Parse errors: {len(errors)}")
    
    if errors:
        print(f"   First error at line {errors[0][0]}: {errors[0][1]}")
    
    # Check structure
    print("\n📋 Checking structure...")
    missing_instruction = sum(1 for d in data if not d.get("instruction"))
    missing_output = sum(1 for d in data if not d.get("output"))
    
    print(f"   Missing 'instruction': {missing_instruction}")
    print(f"   Missing 'output': {missing_output}")
    
    # Content length analysis
    print("\n📏 Content length analysis...")
    inst_lengths = [len(d.get("instruction", "")) for d in data]
    out_lengths = [len(d.get("output", "")) for d in data]
    
    print(f"   Instruction length (avg): {sum(inst_lengths)/len(inst_lengths):.0f} chars")
    print(f"   Output length (avg): {sum(out_lengths)/len(out_lengths):.0f} chars")
    print(f"   Instruction length (min/max): {min(inst_lengths)}/{max(inst_lengths)}")
    print(f"   Output length (min/max): {min(out_lengths)}/{max(out_lengths)}")
    
    # Short content check (< 50 chars is suspicious)
    short_inst = sum(1 for l in inst_lengths if l < 20)
    short_out = sum(1 for l in out_lengths if l < 50)
    print(f"   Very short instructions (<20): {short_inst}")
    print(f"   Very short outputs (<50): {short_out}")
    
    # Deduplication check
    print("\n🔍 Checking for duplicates...")
    seen_instructions = set()
    duplicates = 0
    for d in data:
        inst = d.get("instruction", "")
        if inst in seen_instructions:
            duplicates += 1
        seen_instructions.add(inst)
    
    print(f"   Unique instructions: {len(seen_instructions):,}")
    print(f"   Duplicates: {duplicates:,}")
    print(f"   Uniqueness: {len(seen_instructions)/len(data)*100:.1f}%")
    
    # Domain distribution (estimate based on keywords)
    print("\n📊 Estimated domain distribution...")
    domains = defaultdict(int)
    for d in data:
        inst = d.get("instruction", "").lower()
        if "iva" in inst or "impuesto" in inst or "tributar" in inst or "sri" in inst:
            domains["Tributario"] += 1
        elif "laboral" in inst or "despido" in inst or "sueldo" in inst or "contrato" in inst or "iess" in inst:
            domains["Laboral"] += 1
        elif "sercop" in inst or "contratación" in inst or "licitación" in inst:
            domains["SERCOP"] += 1
        elif "penal" in inst or "civil" in inst or "constitución" in inst or "legal" in inst:
            domains["Legal"] += 1
        elif "geografía" in inst or "provincia" in inst or "volcán" in inst or "capital" in inst:
            domains["Geografía"] += 1
        elif "historia" in inst or "independencia" in inst or "colonial" in inst:
            domains["Historia"] += 1
        elif "cultura" in inst or "fiesta" in inst or "patrimonio" in inst:
            domains["Cultura"] += 1
        elif "turismo" in inst or "galápagos" in inst or "playa" in inst:
            domains["Turismo"] += 1
        elif "educación" in inst or "universidad" in inst:
            domains["Educación"] += 1
        elif "salud" in inst or "hospital" in inst:
            domains["Salud"] += 1
        elif "deporte" in inst or "fútbol" in inst:
            domains["Deportes"] += 1
        elif "gastronomía" in inst or "plato" in inst or "comida" in inst:
            domains["Gastronomía"] += 1
        else:
            domains["Otros"] += 1
    
    for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"   {domain}: {count:,} ({count/len(data)*100:.1f}%)")
    
    # Random samples
    print("\n🎲 Random samples (3)...")
    samples = random.sample(data, min(3, len(data)))
    for i, s in enumerate(samples, 1):
        print(f"\n   --- Sample {i} ---")
        print(f"   Q: {s.get('instruction', '')[:80]}...")
        print(f"   A: {s.get('output', '')[:100]}...")
    
    # Quality score
    print("\n" + "=" * 70)
    print("  QUALITY SCORE")
    print("=" * 70)
    
    score = 100
    if len(errors) > 0:
        score -= 20
        print("   ❌ JSON errors (-20)")
    if missing_instruction > 0 or missing_output > 0:
        score -= 20
        print("   ❌ Missing fields (-20)")
    if duplicates / len(data) > 0.1:
        score -= 15
        print("   ⚠️ High duplication (-15)")
    elif duplicates > 0:
        score -= 5
        print("   ⚠️ Some duplicates (-5)")
    if sum(out_lengths)/len(out_lengths) < 200:
        score -= 10
        print("   ⚠️ Short outputs (-10)")
    
    if score == 100:
        print("   ✅ All checks passed!")
    
    print(f"\n   📊 FINAL QUALITY SCORE: {score}/100")
    print("=" * 70)
    
    # Save report
    report = {
        "total_examples": len(data),
        "json_errors": len(errors),
        "missing_instruction": missing_instruction,
        "missing_output": missing_output,
        "avg_instruction_length": sum(inst_lengths)/len(inst_lengths),
        "avg_output_length": sum(out_lengths)/len(out_lengths),
        "duplicates": duplicates,
        "uniqueness_percent": len(seen_instructions)/len(data)*100,
        "quality_score": score,
    }
    
    with open("data_quality_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Report saved to data_quality_report.json")

if __name__ == "__main__":
    validate_dataset()
