#!/usr/bin/env python3
"""
YACHAQ TRAINING - Inspired by Karpathy's nanoGPT
=================================================
Training setup for Yachaq LLM EC using Ecuador data

Based on: https://github.com/karpathy/nanoGPT
Adapted for: Ecuador-specific fine-tuning

Usage:
    1. python prepare_data.py  # Prepare training data
    2. python train.py         # Train/fine-tune model
    3. python sample.py        # Generate samples
"""

import os
import json
import glob
from pathlib import Path
from typing import List, Dict
import tiktoken
import numpy as np
from datetime import datetime

# Configuration
DATA_DIR = "/Users/macbookpro201916i964gb1tb/Downloads/1x/yachaq/training/data"
S3_BUCKET = "s3://yachaq-lex-raw-0017472631"
LOCAL_CACHE = "/tmp/yachaq_training_data"

# Tokenizer
ENCODING = "cl100k_base"  # GPT-4 tokenizer

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

class YachaqDataPreparer:
    """Prepare Ecuador data for LLM training (nanoGPT style)"""
    
    def __init__(self):
        self.enc = tiktoken.get_encoding(ENCODING)
        self.data_dir = Path(DATA_DIR)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def download_from_s3(self, prefix: str = "") -> List[str]:
        """Download training data from S3"""
        import subprocess
        
        local_dir = Path(LOCAL_CACHE) / prefix
        local_dir.mkdir(parents=True, exist_ok=True)
        
        log(f"Downloading from S3: {S3_BUCKET}/{prefix}")
        
        result = subprocess.run([
            "aws", "s3", "sync",
            f"{S3_BUCKET}/{prefix}",
            str(local_dir),
            "--exclude", "*.zip"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            files = list(local_dir.rglob("*.*"))
            log(f"Downloaded {len(files)} files")
            return [str(f) for f in files]
        else:
            log(f"Error: {result.stderr}")
            return []
    
    def read_file(self, filepath: str) -> str:
        """Read content from various file types"""
        ext = Path(filepath).suffix.lower()
        
        try:
            if ext in ['.txt', '.md']:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            
            elif ext == '.json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return "\n\n".join(str(item) for item in data)
                    elif isinstance(data, dict):
                        return json.dumps(data, ensure_ascii=False, indent=2)
                    return str(data)
            
            elif ext == '.csv':
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            
            else:
                return ""
                
        except Exception as e:
            log(f"Error reading {filepath}: {e}")
            return ""
    
    def prepare_corpus(self, categories: List[str] = None) -> str:
        """Prepare full training corpus from S3 data"""
        
        if categories is None:
            categories = [
                "asamblea",      # Legal documents
                "sri",           # Tax data
                "tributario",    # Tax regulations
                "contratacion",  # SERCOP
                "datos_abiertos", # Open data
                "cultura_turismo", # Culture & tourism
                "libros_ecuador", # Books
                "gobierno",      # Government
            ]
        
        all_text = []
        
        for category in categories:
            log(f"Processing category: {category}")
            files = self.download_from_s3(category)
            
            for filepath in files[:1000]:  # Limit per category
                content = self.read_file(filepath)
                if len(content) > 100:
                    all_text.append(content)
        
        corpus = "\n\n---\n\n".join(all_text)
        log(f"Total corpus size: {len(corpus):,} characters")
        
        return corpus
    
    def tokenize(self, text: str) -> np.ndarray:
        """Tokenize text using tiktoken"""
        tokens = self.enc.encode(text)
        return np.array(tokens, dtype=np.uint32)
    
    def save_binary(self, tokens: np.ndarray, name: str):
        """Save tokenized data as binary file (nanoGPT format)"""
        filepath = self.data_dir / f"{name}.bin"
        tokens.tofile(filepath)
        log(f"Saved: {filepath} ({len(tokens):,} tokens)")
    
    def prepare(self, train_ratio: float = 0.9):
        """Full preparation pipeline"""
        log("=" * 60)
        log("YACHAQ DATA PREPARATION")
        log("=" * 60)
        
        # Get corpus
        corpus = self.prepare_corpus()
        
        if not corpus:
            log("ERROR: No data to prepare")
            return
        
        # Tokenize
        log("Tokenizing corpus...")
        tokens = self.tokenize(corpus)
        log(f"Total tokens: {len(tokens):,}")
        
        # Split train/val
        split_idx = int(len(tokens) * train_ratio)
        train_tokens = tokens[:split_idx]
        val_tokens = tokens[split_idx:]
        
        log(f"Train tokens: {len(train_tokens):,}")
        log(f"Val tokens: {len(val_tokens):,}")
        
        # Save
        self.save_binary(train_tokens, "train")
        self.save_binary(val_tokens, "val")
        
        # Save metadata
        meta = {
            "vocab_size": self.enc.n_vocab,
            "encoding": ENCODING,
            "train_tokens": len(train_tokens),
            "val_tokens": len(val_tokens),
            "created": datetime.now().isoformat(),
            "source": "Yachaq LLM EC - Ecuador Public Data"
        }
        
        with open(self.data_dir / "meta.json", 'w') as f:
            json.dump(meta, f, indent=2)
        
        log("=" * 60)
        log("DATA PREPARATION COMPLETE")
        log(f"Output: {self.data_dir}")
        log("=" * 60)


if __name__ == "__main__":
    preparer = YachaqDataPreparer()
    preparer.prepare()
