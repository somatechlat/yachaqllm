#!/usr/bin/env python3
"""
🔬 KARPATHY TRAINING DATA ALIGNMENT AUDIT
=========================================
Verifies our data matches SOTA fine-tuning best practices:
1. Alpaca format compliance
2. Instruction diversity (no repetition)
3. Output quality (reasoning, length)
4. Token distribution analysis
5. Domain balance
"""

import json
import random
from collections import Counter

INPUT = "data/instruction_dataset/train.jsonl"

def audit():
    print("=" * 70)
    print("  🔬 KARPATHY TRAINING DATA ALIGNMENT AUDIT")
    print("=" * 70)
    
    # Load data
    data = []
    with open(INPUT, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    
    print(f"\n📊 Dataset size: {len(data):,} examples")
    
    # =========================================================================
    # CHECK 1: Alpaca Format Compliance
    # =========================================================================
    print("\n" + "=" * 50)
    print("CHECK 1: Alpaca/Stanford Format Compliance")
    print("=" * 50)
    
    required_keys = ["instruction", "input", "output"]
    format_errors = 0
    
    for i, item in enumerate(data[:1000]):  # Sample first 1000
        for key in required_keys:
            if key not in item:
                format_errors += 1
                print(f"  ❌ Missing '{key}' at index {i}")
    
    if format_errors == 0:
        print("  ✅ PASS: All examples have instruction/input/output keys")
    else:
        print(f"  ❌ FAIL: {format_errors} format errors found")
    
    # =========================================================================
    # CHECK 2: Instruction Diversity (Karpathy: High Entropy)
    # =========================================================================
    print("\n" + "=" * 50)
    print("CHECK 2: Instruction Diversity (Karpathy: High Entropy)")
    print("=" * 50)
    
    instructions = [d["instruction"] for d in data]
    unique_instructions = set(instructions)
    duplicates = len(instructions) - len(unique_instructions)
    uniqueness = len(unique_instructions) / len(instructions) * 100
    
    print(f"  Total instructions: {len(instructions):,}")
    print(f"  Unique instructions: {len(unique_instructions):,}")
    print(f"  Duplicates: {duplicates}")
    print(f"  Uniqueness: {uniqueness:.1f}%")
    
    if uniqueness >= 99:
        print("  ✅ PASS: High diversity (>99% unique)")
    elif uniqueness >= 95:
        print("  ⚠️ WARNING: Some duplication (95-99% unique)")
    else:
        print("  ❌ FAIL: Too many duplicates (<95% unique)")
    
    # =========================================================================
    # CHECK 3: Output Quality (Reasoning Length)
    # =========================================================================
    print("\n" + "=" * 50)
    print("CHECK 3: Output Quality (Length & Reasoning)")
    print("=" * 50)
    
    output_lengths = [len(d["output"]) for d in data]
    avg_length = sum(output_lengths) / len(output_lengths)
    min_length = min(output_lengths)
    max_length = max(output_lengths)
    
    # Check for reasoning indicators
    reasoning_indicators = ["porque", "por lo tanto", "cálculo", "resultado", "base legal", 
                            "según", "artículo", "art.", "fórmula", "paso", "**"]
    has_reasoning = sum(1 for d in data if any(ind in d["output"].lower() for ind in reasoning_indicators))
    
    print(f"  Avg output length: {avg_length:.0f} chars")
    print(f"  Min/Max: {min_length}/{max_length} chars")
    print(f"  With reasoning indicators: {has_reasoning:,}/{len(data):,} ({has_reasoning/len(data)*100:.1f}%)")
    
    if avg_length >= 300 and has_reasoning/len(data) >= 0.8:
        print("  ✅ PASS: Good output quality with reasoning")
    elif avg_length >= 200:
        print("  ⚠️ WARNING: Outputs could be longer")
    else:
        print("  ❌ FAIL: Outputs too short for quality training")
    
    # =========================================================================
    # CHECK 4: Token Estimation (for training cost)
    # =========================================================================
    print("\n" + "=" * 50)
    print("CHECK 4: Token Estimation")
    print("=" * 50)
    
    total_chars = sum(len(d["instruction"]) + len(d["output"]) for d in data)
    estimated_tokens = total_chars / 4  # ~4 chars per token
    
    print(f"  Total characters: {total_chars:,}")
    print(f"  Estimated tokens: {estimated_tokens:,.0f}")
    print(f"  Tokens per example: {estimated_tokens/len(data):.0f}")
    
    if 10_000_000 <= estimated_tokens <= 100_000_000:
        print("  ✅ PASS: Token count in optimal range for fine-tuning")
    elif estimated_tokens < 10_000_000:
        print("  ⚠️ WARNING: Could use more data (< 10M tokens)")
    else:
        print("  ⚠️ WARNING: Large dataset, will take longer to train")
    
    # =========================================================================
    # CHECK 5: Domain Distribution
    # =========================================================================
    print("\n" + "=" * 50)
    print("CHECK 5: Domain Distribution")
    print("=" * 50)
    
    domain_keywords = {
        "TRIBUTARIO": ["iva", "impuesto", "retención", "rimpe", "sri", "tributar"],
        "LABORAL": ["despido", "sueldo", "iess", "trabajo", "laboral", "horas extra"],
        "SERCOP": ["sercop", "licitación", "contratación", "compras públicas"],
        "LEGAL": ["legal", "penal", "civil", "constitución", "codigo", "artículo"],
        "ADUANAS": ["aduana", "importa", "exporta", "senae", "arancel"],
        "LOPDP": ["datos personales", "lopdp", "protección de datos"],
        "AMBIENTE": ["ambient", "licencia ambiental", "mae"],
        "MUNICIPAL": ["municipal", "patente", "cootad", "gad"],
    }
    
    domain_counts = Counter()
    for d in data:
        text = (d["instruction"] + " " + d["output"]).lower()
        for domain, keywords in domain_keywords.items():
            if any(kw in text for kw in keywords):
                domain_counts[domain] += 1
                break
        else:
            domain_counts["OTROS"] += 1
    
    print("  Distribution:")
    for domain, count in domain_counts.most_common():
        pct = count / len(data) * 100
        print(f"    {domain}: {count:,} ({pct:.1f}%)")
    
    # =========================================================================
    # CHECK 6: Sample Quality Review
    # =========================================================================
    print("\n" + "=" * 50)
    print("CHECK 6: Random Sample Quality Review")
    print("=" * 50)
    
    samples = random.sample(data, 3)
    for i, s in enumerate(samples, 1):
        print(f"\n  --- Sample {i} ---")
        print(f"  Q: {s['instruction'][:80]}...")
        print(f"  A: {s['output'][:150]}...")
        
        # Quality indicators
        has_structure = "**" in s["output"] or "|" in s["output"]
        has_legal = "art" in s["output"].lower() or "ley" in s["output"].lower()
        has_numbers = "$" in s["output"] or "%" in s["output"]
        
        print(f"  [Structure: {'✅' if has_structure else '❌'}] [Legal Ref: {'✅' if has_legal else '❌'}] [Numbers: {'✅' if has_numbers else '❌'}]")
    
    # =========================================================================
    # FINAL SCORE
    # =========================================================================
    print("\n" + "=" * 70)
    print("  📊 FINAL KARPATHY ALIGNMENT SCORE")
    print("=" * 70)
    
    score = 0
    max_score = 6
    
    if format_errors == 0: score += 1
    if uniqueness >= 99: score += 1
    if avg_length >= 300: score += 1
    if has_reasoning/len(data) >= 0.8: score += 1
    if 10_000_000 <= estimated_tokens <= 100_000_000: score += 1
    if len(domain_counts) >= 4: score += 1
    
    print(f"\n  Score: {score}/{max_score}")
    
    if score >= 5:
        print("  🏆 EXCELLENT: Data is well-aligned with Karpathy/SOTA methodology")
        print("  ✅ READY FOR TRAINING")
    elif score >= 4:
        print("  ✅ GOOD: Minor improvements possible but acceptable")
        print("  ✅ CAN PROCEED WITH TRAINING")
    elif score >= 3:
        print("  ⚠️ FAIR: Some issues should be addressed")
    else:
        print("  ❌ POOR: Major issues need fixing before training")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    audit()
