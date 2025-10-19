#!/usr/bin/env python3
"""
REAL Baseline Test on SageMaker
1. Deploy base Qwen2.5-7B
2. Test 10 questions
3. Save results
4. Delete endpoint
"""
import boto3
import json
import time

QUESTIONS = [
    "¿Cuál es la tarifa del IVA en Ecuador?",
    "¿Quién es el sujeto activo en materia tributaria?",
    "¿Cuál es la tarifa del Impuesto a la Salida de Divisas?",
]

# Get IAM role
sts = boto3.client('sts')
account_id = sts.get_caller_identity()['Account']
role = f"arn:aws:iam::{account_id}:role/service-role/AmazonSageMaker-ExecutionRole"

print(f"Account: {account_id}")
print(f"Role: {role}")
print()

# Use HuggingFace model directly
from sagemaker.huggingface import HuggingFaceModel

model = HuggingFaceModel(
    model_data="s3://huggingface-models/Qwen/Qwen2.5-7B-Instruct",
    role=role,
    transformers_version="4.37",
    pytorch_version="2.1",
    py_version="py310",
)

print("🚀 Deploying base model...")
print("⏱️  Takes ~10 minutes")
print("💰 Cost: ~$0.20 for testing")
print()

predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.xlarge",
    endpoint_name="yachaq-baseline-test"
)

print("✅ Deployed!")
print()

# Test
print("🧪 Testing...")
results = []

for i, q in enumerate(QUESTIONS, 1):
    response = predictor.predict({
        "inputs": q,
        "parameters": {"max_new_tokens": 150}
    })
    
    print(f"{i}. Q: {q}")
    print(f"   A: {response[0]['generated_text'][:100]}...")
    print()
    
    results.append({"question": q, "answer": response[0]['generated_text']})

# Save
with open('baseline_results.json', 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("💾 Saved to baseline_results.json")
print()

# Delete
print("🗑️  Deleting endpoint...")
predictor.delete_endpoint()
print("✅ Done! No more charges.")
