#!/usr/bin/env python3
"""
YACHAQ LLM EC - AWS SAGEMAKER TRAINING
======================================
Fine-tune Llama 3.1 8B using AWS SageMaker

Uses:
- SageMaker Training Jobs
- S3 for data storage
- QLoRA for efficient fine-tuning

Usage:
    python sagemaker_train.py
"""

import boto3
import sagemaker
from sagemaker.huggingface import HuggingFace
from datetime import datetime
import json

# Configuration
AWS_REGION = "us-east-1"
S3_BUCKET = "yachaq-lex-raw-0017472631"
S3_DATA_PATH = f"s3://{S3_BUCKET}/training"
S3_OUTPUT_PATH = f"s3://{S3_BUCKET}/models"

# Model Configuration
MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"  # HuggingFace model
# Alternative: "Equall/Saul-7B-Base" for legal-specialized

# Training Configuration
TRAINING_CONFIG = {
    # Model
    "model_name": MODEL_ID,
    "use_qlora": True,
    "lora_r": 16,
    "lora_alpha": 32,
    "lora_dropout": 0.05,
    
    # Training
    "epochs": 3,
    "batch_size": 4,
    "gradient_accumulation_steps": 4,
    "learning_rate": 2e-5,
    "max_seq_length": 2048,
    "warmup_ratio": 0.1,
    
    # Data
    "dataset_path": S3_DATA_PATH,
}

def create_training_script():
    """Create the training script that runs on SageMaker"""
    
    script = '''
import os
import torch
from datasets import load_from_disk
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import json

def train():
    # Load config
    config = json.loads(os.environ.get("TRAINING_CONFIG", "{}"))
    
    # QLoRA configuration
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        config["model_name"],
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    
    # Prepare for LoRA
    model = prepare_model_for_kbit_training(model)
    
    lora_config = LoraConfig(
        r=config.get("lora_r", 16),
        lora_alpha=config.get("lora_alpha", 32),
        lora_dropout=config.get("lora_dropout", 0.05),
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )
    
    model = get_peft_model(model, lora_config)
    
    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config["model_name"])
    tokenizer.pad_token = tokenizer.eos_token
    
    # Load dataset
    dataset = load_from_disk(os.environ["SM_CHANNEL_TRAIN"])
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=os.environ["SM_MODEL_DIR"],
        num_train_epochs=config.get("epochs", 3),
        per_device_train_batch_size=config.get("batch_size", 4),
        gradient_accumulation_steps=config.get("gradient_accumulation_steps", 4),
        learning_rate=config.get("learning_rate", 2e-5),
        warmup_ratio=config.get("warmup_ratio", 0.1),
        logging_steps=10,
        save_strategy="epoch",
        fp16=True,
        optim="paged_adamw_8bit",
        report_to="none",
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )
    
    # Train
    trainer.train()
    
    # Save
    trainer.save_model()
    tokenizer.save_pretrained(os.environ["SM_MODEL_DIR"])

if __name__ == "__main__":
    train()
'''
    
    script_path = "/Users/macbookpro201916i964gb1tb/Downloads/1x/yachaq/training/scripts/train_sagemaker.py"
    with open(script_path, 'w') as f:
        f.write(script)
    
    return script_path


def launch_training_job():
    """Launch SageMaker training job"""
    
    # Initialize
    session = sagemaker.Session()
    role = sagemaker.get_execution_role()  # Or specify IAM role ARN
    
    # Create training script
    script_path = create_training_script()
    
    # HuggingFace Estimator
    huggingface_estimator = HuggingFace(
        entry_point="train_sagemaker.py",
        source_dir="/Users/macbookpro201916i964gb1tb/Downloads/1x/yachaq/training/scripts",
        
        # Instance
        instance_type="ml.g5.2xlarge",  # 1x A10G (24GB)
        instance_count=1,
        
        # Runtime
        transformers_version="4.36",
        pytorch_version="2.1",
        py_version="py310",
        
        # Resources
        volume_size=100,  # GB
        
        # Config
        hyperparameters={
            "model_name": MODEL_ID,
            "epochs": 3,
            "batch_size": 4,
        },
        
        # Environment
        environment={
            "TRAINING_CONFIG": json.dumps(TRAINING_CONFIG),
            "HF_TOKEN": "YOUR_HF_TOKEN",  # For gated models
        },
        
        # Output
        output_path=S3_OUTPUT_PATH,
        
        # Role
        role=role,
        
        # Tags
        tags=[
            {"Key": "Project", "Value": "Yachaq-LLM-EC"},
            {"Key": "Model", "Value": "Llama-3.1-8B"},
        ],
    )
    
    # Launch
    job_name = f"yachaq-llm-ec-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    huggingface_estimator.fit(
        inputs={
            "train": S3_DATA_PATH,
        },
        job_name=job_name,
        wait=False,  # Don't block
    )
    
    print(f"Training job launched: {job_name}")
    print(f"Monitor at: https://console.aws.amazon.com/sagemaker/home?region={AWS_REGION}#/jobs/{job_name}")
    
    return job_name


def check_job_status(job_name: str):
    """Check training job status"""
    sm = boto3.client('sagemaker', region_name=AWS_REGION)
    
    response = sm.describe_training_job(TrainingJobName=job_name)
    
    status = response['TrainingJobStatus']
    print(f"Job: {job_name}")
    print(f"Status: {status}")
    
    if status == 'Completed':
        print(f"Model: {response['ModelArtifacts']['S3ModelArtifacts']}")
    
    return status


if __name__ == "__main__":
    print("=" * 60)
    print("YACHAQ LLM EC - SAGEMAKER TRAINING")
    print("=" * 60)
    
    # This will be run to launch training
    # job_name = launch_training_job()
    # check_job_status(job_name)
    
    print("Ready to launch training.")
    print(f"Data: {S3_DATA_PATH}")
    print(f"Model: {MODEL_ID}")
    print("Run launch_training_job() when ready.")
