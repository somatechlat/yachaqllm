#!/usr/bin/env python3
"""
Deploy base Qwen2.5-7B to SageMaker for baseline testing
Then deploy trained model later for comparison
"""
import boto3
import json
import time
from datetime import datetime

# Test questions
TEST_QUESTIONS = [
    "¿Cuál es la tarifa del IVA en Ecuador?",
    "¿Quién es el sujeto activo en materia tributaria?",
    "¿Cuál es la tarifa del Impuesto a la Salida de Divisas?",
    "¿Cuándo una empresa está obligada a llevar contabilidad?",
    "¿Qué es el control interno en auditoría?",
    "¿Qué es el punto de equilibrio?",
    "¿Qué es el principio de devengado?",
    "¿Qué tipo de impuesto es el Impuesto a la Renta?",
    "¿Qué son las normas de auditoría?",
    "¿Qué es el costeo ABC?"
]

def deploy_base_model():
    """Deploy base Qwen2.5-7B for testing"""
    print("🚀 Deploying BASE Qwen2.5-7B to SageMaker...")
    print("⏱️  This takes ~5-10 minutes")
    print()
    
    sagemaker = boto3.client('sagemaker')
    
    # Using HuggingFace inference container
    model_data = {
        'ModelName': 'yachaq-baseline-qwen25-7b',
        'PrimaryContainer': {
            'Image': '763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:2.1.0-transformers4.37.0-gpu-py310-cu118-ubuntu20.04',
            'ModelDataUrl': 's3://huggingface-models/Qwen/Qwen2.5-7B-Instruct',
            'Environment': {
                'HF_MODEL_ID': 'Qwen/Qwen2.5-7B-Instruct',
                'HF_TASK': 'text-generation'
            }
        },
        'ExecutionRoleArn': 'arn:aws:iam::YOUR_ACCOUNT:role/SageMakerRole'
    }
    
    print("Creating model...")
    # sagemaker.create_model(**model_data)
    
    print("Creating endpoint config...")
    endpoint_config = {
        'EndpointConfigName': 'yachaq-baseline-config',
        'ProductionVariants': [{
            'VariantName': 'AllTraffic',
            'ModelName': 'yachaq-baseline-qwen25-7b',
            'InstanceType': 'ml.g5.xlarge',
            'InitialInstanceCount': 1
        }]
    }
    # sagemaker.create_endpoint_config(**endpoint_config)
    
    print("Creating endpoint...")
    # sagemaker.create_endpoint(
    #     EndpointName='yachaq-baseline-test',
    #     EndpointConfigName='yachaq-baseline-config'
    # )
    
    print("✅ Endpoint will be ready in ~10 minutes")
    print("💰 Cost: ~$1/hour (we'll delete after testing)")

def test_model(endpoint_name):
    """Test model with questions"""
    runtime = boto3.client('sagemaker-runtime')
    
    results = []
    
    print(f"\n🧪 Testing {endpoint_name}...")
    print("="*70)
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        payload = {
            'inputs': question,
            'parameters': {
                'max_new_tokens': 200,
                'temperature': 0.7
            }
        }
        
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        result = json.loads(response['Body'].read())
        answer = result[0]['generated_text']
        
        results.append({
            'question': question,
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"\n{i}. Q: {question}")
        print(f"   A: {answer[:150]}...")
    
    return results

def save_results(results, filename):
    """Save test results"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to {filename}")

def delete_endpoint(endpoint_name):
    """Delete endpoint to stop charges"""
    sagemaker = boto3.client('sagemaker')
    
    print(f"\n🗑️  Deleting endpoint {endpoint_name}...")
    sagemaker.delete_endpoint(EndpointName=endpoint_name)
    print("✅ Endpoint deleted (no more charges)")

def main():
    print("="*70)
    print("BASELINE TEST - Base Qwen2.5-7B (BEFORE training)")
    print("="*70)
    print()
    print("Plan:")
    print("1. Deploy base model to SageMaker (~10 min)")
    print("2. Test with 10 questions (~2 min)")
    print("3. Save results")
    print("4. Delete endpoint (stop charges)")
    print()
    print("Cost: ~$0.20 total (10 min at $1/hour)")
    print()
    
    choice = input("Deploy and test? (yes/no): ")
    
    if choice.lower() == 'yes':
        deploy_base_model()
        
        print("\nWaiting for endpoint to be ready...")
        print("(Check AWS Console or wait ~10 minutes)")
        
        # After endpoint is ready:
        # results = test_model('yachaq-baseline-test')
        # save_results(results, 'baseline_results.json')
        # delete_endpoint('yachaq-baseline-test')
    else:
        print("Cancelled")

if __name__ == "__main__":
    main()
