#!/usr/bin/env python3
"""
Deploy YACHAQ-LEX to SageMaker
"""
import boto3
import sagemaker
from sagemaker.huggingface import HuggingFace
from sagemaker.inputs import TrainingInput
from pathlib import Path

# Configuration
REGION = "us-east-1"  # Change to your region
ROLE = "arn:aws:iam::YOUR_ACCOUNT:role/SageMakerRole"  # Update this
BUCKET = "yachaq-lex-data"  # Your S3 bucket

# Training config
INSTANCE_TYPE = "ml.g5.2xlarge"  # A10G 24GB
USE_SPOT = True
MAX_RUN = 100000  # ~28 hours max

def upload_data_to_s3(local_dir: str, s3_prefix: str):
    """Upload training data to S3"""
    print(f"📤 Uploading {local_dir} to s3://{BUCKET}/{s3_prefix}")
    
    s3 = boto3.client('s3')
    local_path = Path(local_dir)
    
    for file in local_path.glob("*.jsonl"):
        s3_key = f"{s3_prefix}/{file.name}"
        s3.upload_file(str(file), BUCKET, s3_key)
        print(f"   ✅ {file.name}")
    
    return f"s3://{BUCKET}/{s3_prefix}"

def create_training_job():
    """Create SageMaker training job"""
    print("🚀 Creating SageMaker training job...")
    
    # Session
    sess = sagemaker.Session()
    
    # Upload data
    train_s3 = upload_data_to_s3("./synthetic_data", "training/data")
    
    # Estimator
    huggingface_estimator = HuggingFace(
        entry_point="train_sagemaker.py",
        source_dir="./",
        instance_type=INSTANCE_TYPE,
        instance_count=1,
        role=ROLE,
        transformers_version="4.36",
        pytorch_version="2.1",
        py_version="py310",
        use_spot_instances=USE_SPOT,
        max_run=MAX_RUN,
        max_wait=MAX_RUN + 3600 if USE_SPOT else None,
        hyperparameters={
            "model_id": "Qwen/Qwen2.5-7B-Instruct",
            "num_train_epochs": 3,
            "per_device_train_batch_size": 4,
            "learning_rate": 2e-4,
        },
    )
    
    # Start training
    print(f"🏋️  Starting training on {INSTANCE_TYPE}")
    print(f"   Spot instances: {USE_SPOT}")
    print(f"   Data: {train_s3}")
    
    huggingface_estimator.fit({"train": train_s3})
    
    print("✅ Training job submitted!")
    print(f"   Job name: {huggingface_estimator.latest_training_job.name}")
    
    return huggingface_estimator

def deploy_endpoint(estimator):
    """Deploy model to SageMaker endpoint"""
    print("🚀 Deploying endpoint...")
    
    predictor = estimator.deploy(
        initial_instance_count=1,
        instance_type="ml.g5.xlarge",
        endpoint_name="yachaq-lex-v1",
    )
    
    print("✅ Endpoint deployed!")
    print(f"   Endpoint: {predictor.endpoint_name}")
    
    return predictor

def test_endpoint(predictor):
    """Test the deployed endpoint"""
    print("🧪 Testing endpoint...")
    
    test_question = {
        "inputs": "¿Cuál es la tarifa del IVA en Ecuador?",
        "parameters": {
            "max_new_tokens": 256,
            "temperature": 0.7,
        }
    }
    
    response = predictor.predict(test_question)
    print(f"\n📝 Response:\n{response}")

def main():
    print("=" * 60)
    print("YACHAQ-LEX SageMaker Deployment")
    print("=" * 60)
    
    # Step 1: Create training job
    estimator = create_training_job()
    
    # Step 2: Deploy (after training completes)
    # Uncomment after training is done:
    # predictor = deploy_endpoint(estimator)
    # test_endpoint(predictor)

if __name__ == "__main__":
    main()
