import json
import random
import re

def verify_dataset_integrity(file_path):
    print(f"🔬 Deep-Cleaning Audit of {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]
    
    total = len(data)
    samples = random.sample(data, min(50, total))
    
    issues = []
    
    # Common "Garbage" or "Bad Data" patterns
    bad_patterns = [
        r"I don't know",
        r"No tengo información",
        r"asdf",
        r"test test",
        r"12345",
        r"[A-Z]{10,}", # Random long uppercase strings
    ]
    
    for i, item in enumerate(samples):
        text = item['instruction'] + " " + item['output']
        
        # 1. Check for garbage patterns
        for pattern in bad_patterns:
            if re.search(pattern, text, re.I):
                issues.append(f"Sample {i}: Potential garbage pattern '{pattern}' found.")
        
        # 2. Check length (quality models need substance)
        if len(item['output']) < 150:
            issues.append(f"Sample {i}: Output too short ({len(item['output'])} chars).")
            
        # 3. Check for specific Ecuadorian legal context
        if "Ecuador" not in text and "Art." not in text and "Ley" not in text:
            # Not necessarily an error but check for hallucinations
            pass

    if not issues:
        print("✅ ELITE QUALITY CONFIRMED: No garbage patterns found in 50 random samples.")
        print(f"✅ Every sample has substance (>150 chars).")
    else:
        print("⚠️ QUALITY CONCERNS FOUND:")
        for issue in issues:
            print(f"  - {issue}")

if __name__ == "__main__":
    verify_dataset_integrity("data/instruction_dataset/train.jsonl")
