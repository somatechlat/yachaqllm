#!/usr/bin/env python3
"""
SageMaker Training Script for YACHAQ-LEX
Fine-tune Qwen2.5-7B-Instruct on Ecuadorian legal data
"""
import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

@dataclass
class Config:
    # Model
    model_id: str = "Qwen/Qwen2.5-7B-Instruct"
    max_seq_length: int = 2048
    
    # LoRA
    lora_r: int = 64
    lora_alpha: int = 128
    lora_dropout: float = 0.05
    
    # Training
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.03
    
    # Paths (SageMaker sets these)
    train_dir: str = os.environ.get("SM_CHANNEL_TRAIN", "./synthetic_data")
    model_dir: str = os.environ.get("SM_MODEL_DIR", "./output")
    output_dir: str = os.environ.get("SM_OUTPUT_DATA_DIR", "./checkpoints")

def format_instruction(example):
    """Format data for instruction tuning"""
    if example.get("input"):
        prompt = f"""### Instrucción:
{example['instruction']}

### Entrada:
{example['input']}

### Respuesta:
{example['output']}"""
    else:
        prompt = f"""### Instrucción:
{example['instruction']}

### Respuesta:
{example['output']}"""
    
    return {"text": prompt}

def load_training_data(data_dir: str):
    """Load all JSONL files from directory"""
    data_files = list(Path(data_dir).glob("*.jsonl"))
    
    if not data_files:
        raise ValueError(f"No JSONL files found in {data_dir}")
    
    print(f"📂 Loading {len(data_files)} data files...")
    
    dataset = load_dataset(
        "json",
        data_files=[str(f) for f in data_files],
        split="train"
    )
    
    print(f"✅ Loaded {len(dataset):,} training examples")
    
    # Format for instruction tuning
    dataset = dataset.map(format_instruction, remove_columns=dataset.column_names)
    
    return dataset

def setup_model_and_tokenizer(config: Config):
    """Setup model with QLoRA"""
    print(f"🤖 Loading model: {config.model_id}")
    
    # Quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        config.model_id,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
    )
    
    # Prepare for k-bit training
    model = prepare_model_for_kbit_training(model)
    
    # LoRA config
    peft_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", 
                       "gate_proj", "up_proj", "down_proj"],
        bias="none",
        task_type="CAUSAL_LM",
    )
    
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_id,
        trust_remote_code=True,
    )
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    return model, tokenizer

def train(config: Config):
    """Main training function"""
    print("🚀 Starting YACHAQ-LEX training...")
    print(f"   Model: {config.model_id}")
    print(f"   Train dir: {config.train_dir}")
    print(f"   Output dir: {config.output_dir}")
    
    # Load data
    dataset = load_training_data(config.train_dir)
    
    # Split train/eval
    dataset = dataset.train_test_split(test_size=0.05, seed=42)
    train_dataset = dataset["train"]
    eval_dataset = dataset["test"]
    
    print(f"📊 Train: {len(train_dataset):,} | Eval: {len(eval_dataset):,}")
    
    # Setup model
    model, tokenizer = setup_model_and_tokenizer(config)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_train_epochs,
        per_device_train_batch_size=config.per_device_train_batch_size,
        per_device_eval_batch_size=config.per_device_train_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        lr_scheduler_type="cosine",
        warmup_ratio=config.warmup_ratio,
        logging_steps=100,
        eval_steps=1000,
        save_steps=5000,
        save_total_limit=3,
        bf16=True,
        optim="paged_adamw_8bit",
        gradient_checkpointing=True,
        max_grad_norm=1.0,
        weight_decay=0.01,
        report_to="none",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
    )
    
    # Trainer
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        max_seq_length=config.max_seq_length,
        dataset_text_field="text",
        packing=False,
    )
    
    # Train
    print("\n🏋️  Training started...")
    trainer.train()
    
    # Save
    print(f"\n💾 Saving model to {config.model_dir}")
    trainer.save_model(config.model_dir)
    tokenizer.save_pretrained(config.model_dir)
    
    # Save metrics
    metrics = trainer.evaluate()
    with open(Path(config.model_dir) / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    print("✅ Training complete!")
    print(f"   Final eval loss: {metrics.get('eval_loss', 'N/A')}")

if __name__ == "__main__":
    config = Config()
    train(config)
