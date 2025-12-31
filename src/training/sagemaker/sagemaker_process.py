#!/usr/bin/env python3
"""
YACHAQ LLM EC - SAGEMAKER DATA PROCESSING (boto3 direct)
=========================================================
Launches a SageMaker Processing Job to prepare training data in the cloud.
Uses boto3 directly to avoid SDK version conflicts.

Usage:
    python sagemaker_process.py
"""

import boto3
import json
from datetime import datetime

# Configuration
AWS_REGION = "us-east-1"
S3_BUCKET = "yachaq-lex-raw-0017472631"
S3_OUTPUT = f"s3://{S3_BUCKET}/training"

# NOTE: You need to create an IAM role for SageMaker with:
# - AmazonSageMakerFullAccess
# - S3 read/write access to yachaq-lex-raw-0017472631
SAGEMAKER_ROLE = "arn:aws:iam::302776397208:role/SageMakerExecutionRole"

# Container image - AWS managed sklearn processing (known to exist)
PROCESSING_IMAGE = "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3"

def create_processing_script():
    """Create the processing script that will run inside SageMaker"""
    
    script = '''#!/usr/bin/env python3
"""
Data Preparation Script - Runs inside SageMaker Processing
"""
import os
import json
import subprocess
import boto3
from pathlib import Path
from datetime import datetime

# Install dependencies
subprocess.check_call(["pip", "install", "-q", "tiktoken", "datasets", "pandas"])

import tiktoken
from datasets import Dataset, DatasetDict

S3_BUCKET = "yachaq-lex-raw-0017472631"
S3_OUTPUT_PREFIX = "training"
LOCAL_DATA = Path("/opt/ml/processing/input")
LOCAL_OUTPUT = Path("/opt/ml/processing/output")
ENCODING = "cl100k_base"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def read_file(filepath):
    path = Path(filepath)
    ext = path.suffix.lower()
    try:
        if ext in ['.txt', '.md', '.json', '.csv']:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    except Exception as e:
        log(f"Error reading {path}: {e}")
    return ""

def main():
    log("Starting Yachaq Data Processing on SageMaker")
    
    # Find all downloaded files
    files = list(LOCAL_DATA.rglob("*.*"))
    log(f"Found {len(files)} files to process")
    
    # Read and collect content
    data_items = []
    for f in files:
        content = read_file(f)
        if len(content.strip()) > 100:
            data_items.append({
                "text": content,
                "source": str(f.parent.name)
            })
    
    log(f"Collected {len(data_items)} valid text items")
    
    if not data_items:
        log("ERROR: No data collected!")
        return
    
    # Create HuggingFace Dataset
    dataset = Dataset.from_list(data_items)
    split = dataset.train_test_split(test_size=0.1)
    dataset_dict = DatasetDict({
        'train': split['train'],
        'validation': split['test']
    })
    
    # Save locally first
    LOCAL_OUTPUT.mkdir(parents=True, exist_ok=True)
    output_path = LOCAL_OUTPUT / "hf_dataset"
    dataset_dict.save_to_disk(output_path)
    log(f"Saved HF Dataset locally to {output_path}")
    
    # Upload to S3
    s3 = boto3.client('s3')
    for root, dirs, files in os.walk(output_path):
        for file in files:
            local_file = os.path.join(root, file)
            relative_path = os.path.relpath(local_file, LOCAL_OUTPUT)
            s3_key = f"{S3_OUTPUT_PREFIX}/{relative_path}"
            log(f"Uploading {s3_key}")
            s3.upload_file(local_file, S3_BUCKET, s3_key)
    
    log("DONE - Dataset uploaded to S3")

if __name__ == "__main__":
    main()
'''
    
    # Upload script to S3
    s3 = boto3.client('s3', region_name=AWS_REGION)
    script_key = "scripts/process_data.py"
    s3.put_object(Bucket=S3_BUCKET, Key=script_key, Body=script.encode('utf-8'))
    print(f"Uploaded processing script to s3://{S3_BUCKET}/{script_key}")
    return f"s3://{S3_BUCKET}/{script_key}"

def launch_processing_job():
    """Launch SageMaker Processing Job using boto3"""
    
    # Upload processing script to S3
    script_s3_uri = create_processing_script()
    
    sm = boto3.client('sagemaker', region_name=AWS_REGION)
    
    job_name = f"yachaq-data-prep-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Define the job
    response = sm.create_processing_job(
        ProcessingJobName=job_name,
        ProcessingResources={
            'ClusterConfig': {
                'InstanceCount': 1,
                'InstanceType': 'ml.m5.2xlarge',
                'VolumeSizeInGB': 100
            }
        },
        StoppingCondition={
            'MaxRuntimeInSeconds': 86400  # 24 hours
        },
        AppSpecification={
            'ImageUri': PROCESSING_IMAGE,
            'ContainerEntrypoint': ['python3', '/opt/ml/processing/input/code/process_data.py']
        },
        RoleArn=SAGEMAKER_ROLE,
        ProcessingInputs=[
            {
                'InputName': 'code',
                'S3Input': {
                    'S3Uri': script_s3_uri,
                    'LocalPath': '/opt/ml/processing/input/code',
                    'S3DataType': 'S3Prefix',
                    'S3InputMode': 'File'
                }
            },
            {
                'InputName': 'data-asamblea',
                'S3Input': {
                    'S3Uri': f's3://{S3_BUCKET}/asamblea/',
                    'LocalPath': '/opt/ml/processing/input/asamblea',
                    'S3DataType': 'S3Prefix',
                    'S3InputMode': 'File'
                }
            },
            {
                'InputName': 'data-sri',
                'S3Input': {
                    'S3Uri': f's3://{S3_BUCKET}/sri/',
                    'LocalPath': '/opt/ml/processing/input/sri',
                    'S3DataType': 'S3Prefix',
                    'S3InputMode': 'File'
                }
            },
            {
                'InputName': 'data-tributario',
                'S3Input': {
                    'S3Uri': f's3://{S3_BUCKET}/tributario/',
                    'LocalPath': '/opt/ml/processing/input/tributario',
                    'S3DataType': 'S3Prefix',
                    'S3InputMode': 'File'
                }
            },
            {
                'InputName': 'data-contratacion',
                'S3Input': {
                    'S3Uri': f's3://{S3_BUCKET}/contratacion/',
                    'LocalPath': '/opt/ml/processing/input/contratacion',
                    'S3DataType': 'S3Prefix',
                    'S3InputMode': 'File'
                }
            },
            {
                'InputName': 'data-datos_abiertos',
                'S3Input': {
                    'S3Uri': f's3://{S3_BUCKET}/datos_abiertos/',
                    'LocalPath': '/opt/ml/processing/input/datos_abiertos',
                    'S3DataType': 'S3Prefix',
                    'S3InputMode': 'File'
                }
            }
        ],
        ProcessingOutputConfig={
            'Outputs': [
                {
                    'OutputName': 'training-data',
                    'S3Output': {
                        'S3Uri': S3_OUTPUT,
                        'LocalPath': '/opt/ml/processing/output',
                        'S3UploadMode': 'EndOfJob'
                    }
                }
            ]
        },
        Tags=[
            {'Key': 'Project', 'Value': 'Yachaq-LLM-EC'},
            {'Key': 'Purpose', 'Value': 'Data-Preparation'}
        ]
    )
    
    print(f"\\n{'='*60}")
    print(f"PROCESSING JOB LAUNCHED: {job_name}")
    print(f"{'='*60}")
    print(f"Monitor at: https://console.aws.amazon.com/sagemaker/home?region={AWS_REGION}#/processing-jobs/{job_name}")
    print(f"\\nThis job will:")
    print(f"  1. Download data from s3://{S3_BUCKET}/")
    print(f"  2. Process and tokenize all text data")
    print(f"  3. Create HuggingFace Dataset")
    print(f"  4. Upload to {S3_OUTPUT}")
    
    return job_name

if __name__ == "__main__":
    try:
        job_name = launch_processing_job()
    except Exception as e:
        print(f"ERROR: {e}")
        print("\\nMake sure you have:")
        print("  1. AWS credentials configured")
        print("  2. SageMaker execution role created")
        print("  3. Proper IAM permissions")
