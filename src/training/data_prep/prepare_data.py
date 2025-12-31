#!/usr/bin/env python3
"""
YACHAQ TRAINING DATA PREPARATION
================================
Prepares Ecuador data for LLM training on SageMaker.
Supports both nanoGPT (binary) and HuggingFace (Arrow) formats.

Usage:
    python prepare_data.py --format hf --upload    # Prepare and upload to S3 for SageMaker
    python prepare_data.py --sample                # Test with small sample
"""

import os
import json
import glob
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import numpy as np

try:
    import tiktoken
    from datasets import Dataset, DatasetDict
except ImportError:
    print("Installing requirements...")
    subprocess.check_call(["pip", "install", "tiktoken", "datasets", "pandas", "boto3"])
    import tiktoken
    from datasets import Dataset, DatasetDict

import boto3

# Configuration
# Default local paths (can be overridden)
REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"
LOCAL_CACHE = REPO_ROOT / "data" / "cache"

# S3 Configuration
S3_BUCKET = "yachaq-lex-raw-0017472631"
S3_RAW_PREFIX = ""  # Root of bucket
S3_TRAIN_PREFIX = "training"

# Tokenizer
ENCODING = "cl100k_base"  # GPT-4 / Llama 3 tokenizer

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

class YachaqDataPreparer:
    """Prepare Ecuador data for LLM training"""
    
    def __init__(self, sample_mode: bool = False):
        self.enc = tiktoken.get_encoding(ENCODING)
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = LOCAL_CACHE
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.sample_mode = sample_mode
        self.s3_client = boto3.client('s3')
        
    def download_from_s3(self, categories: List[str]) -> List[str]:
        """Download training data from S3"""
        all_files = []
        
        for category in categories:
            log(f"Downloading category: {category}")
            local_cat_dir = self.cache_dir / category
            local_cat_dir.mkdir(parents=True, exist_ok=True)
            
            if self.sample_mode:
                # In sample mode, valid S3 list is needed.
                # Use paginator to get just a few files
                paginator = self.s3_client.get_paginator('list_objects_v2')
                pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=f"{category}/", PaginationConfig={'MaxItems': 10})
                
                for page in pages:
                    if 'Contents' not in page:
                        continue
                    for obj in page['Contents']:
                        key = obj['Key']
                        if key.endswith(('.txt', '.md', '.json', '.csv')):
                            local_path = self.cache_dir / key
                            local_path.parent.mkdir(parents=True, exist_ok=True)
                            if not local_path.exists():
                                self.s3_client.download_file(S3_BUCKET, key, str(local_path))
                            all_files.append(str(local_path))
            else:
                # Full sync
                cmd = [
                    "aws", "s3", "sync",
                    f"s3://{S3_BUCKET}/{category}",
                    str(local_cat_dir),
                    "--exclude", "*.zip",
                    "--exclude", "*.pdf"
                ]
                subprocess.run(cmd, check=True)
                all_files.extend(list(local_cat_dir.rglob("*.*")))
                
        return [str(f) for f in all_files if str(f).endswith(('.txt', '.md', '.json', '.csv'))]
    
    def read_file(self, filepath: str) -> str:
        """Read content from various file types"""
        path = Path(filepath)
        ext = path.suffix.lower()
        
        try:
            if ext in ['.txt', '.md']:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            
            elif ext == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return "\n\n".join(str(item) for item in data)
                    elif isinstance(data, dict):
                        return json.dumps(data, ensure_ascii=False)
                    return str(data)
            
            elif ext == '.csv':
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            
            return ""
        except Exception as e:
            log(f"Error reading {path}: {e}")
            return ""
    
    def prepare_dataset(self, categories: List[str] = None) -> List[Dict]:
        """Prepare dataset in memory (list of dicts)"""
        if categories is None:
            categories = [
                "asamblea", "sri", "tributario", 
                "contratacion", "datos_abiertos"
            ]
        
        files = self.download_from_s3(categories)
        log(f"Processing {len(files)} files...")
        
        data_items = []
        for filepath in files:
            content = self.read_file(filepath)
            if len(content.strip()) > 100:
                data_items.append({
                    "text": content,
                    "source": str(filepath).split("/")[-2] # Rough category
                })
        
        log(f"Collected {len(data_items)} valid text items")
        return data_items

    def save_hf_dataset(self, data_items: List[Dict]):
        """Save as HuggingFace Dataset (Arrow format)"""
        if not data_items:
            log("No data to save!")
            return
            
        dataset = Dataset.from_list(data_items)
        
        # Split
        split_dataset = dataset.train_test_split(test_size=0.1)
        dataset_dict = DatasetDict({
            'train': split_dataset['train'],
            'validation': split_dataset['test']
        })
        
        save_path = self.data_dir / "hf_dataset"
        dataset_dict.save_to_disk(save_path)
        log(f"Saved HF Dataset to {save_path}")
        return save_path

    def upload_to_s3(self, local_path: Path):
        """Upload prepared data to S3 training prefix"""
        if not local_path.exists():
            log(f"Path does not exist: {local_path}")
            return
            
        s3_dest = f"s3://{S3_BUCKET}/{S3_TRAIN_PREFIX}"
        log(f"Uploading {local_path} to {s3_dest}")
        
        subprocess.run([
            "aws", "s3", "sync",
            str(local_path),
            s3_dest,
            "--delete"
        ], check=True)
        log("Upload complete")

    def run(self, format_type: str = "hf", upload: bool = False):
        log("Starting Data Preparation...")
        if self.sample_mode:
            log("Running in SAMPLE MODE (10 files max)")
            
        data = self.prepare_dataset()
        
        saved_path = None
        if format_type == "hf":
            saved_path = self.save_hf_dataset(data)
        else:
            log("NanoGPT binary format not fully implemented in this update.")
        
        if upload and saved_path:
            self.upload_to_s3(saved_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yachaq Data Preparation")
    parser.add_argument("--sample", action="store_true", help="Run with small sample")
    parser.add_argument("--format", type=str, default="hf", choices=["hf", "bin"], help="Output format")
    parser.add_argument("--upload", action="store_true", help="Upload to S3")
    
    args = parser.parse_args()
    
    preparer = YachaqDataPreparer(sample_mode=args.sample)
    preparer.run(format_type=args.format, upload=args.upload)
