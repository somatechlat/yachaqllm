#!/usr/bin/env python3
"""
YACHAQ-LEX Training - nanochat style
Minimal, efficient, single-file training for Ecuador government data
"""
import torch
import torch.nn as nn
from torch.nn import functional as F
from dataclasses import dataclass
import json
import math
from pathlib import Path

@dataclass
class Config:
    # Model
    vocab_size: int = 50304
    n_layer: int = 12
    n_head: int = 12
    n_embd: int = 768
    block_size: int = 1024
    dropout: float = 0.1
    
    # Training
    batch_size: int = 8
    learning_rate: float = 3e-4
    max_iters: int = 10000
    eval_interval: int = 500
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Data
    data_dir: str = '../rag/ingest'

class GPT(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        self.transformer = nn.ModuleDict(dict(
            wte = nn.Embedding(config.vocab_size, config.n_embd),
            wpe = nn.Embedding(config.block_size, config.n_embd),
            drop = nn.Dropout(config.dropout),
            h = nn.ModuleList([Block(config) for _ in range(config.n_layer)]),
            ln_f = nn.LayerNorm(config.n_embd),
        ))
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)
        
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
    
    def forward(self, idx, targets=None):
        b, t = idx.size()
        pos = torch.arange(0, t, dtype=torch.long, device=idx.device)
        
        tok_emb = self.transformer.wte(idx)
        pos_emb = self.transformer.wpe(pos)
        x = self.transformer.drop(tok_emb + pos_emb)
        
        for block in self.transformer.h:
            x = block(x)
        
        x = self.transformer.ln_f(x)
        logits = self.lm_head(x)
        
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        
        return logits, loss

class Block(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.ln_1 = nn.LayerNorm(config.n_embd)
        self.attn = CausalSelfAttention(config)
        self.ln_2 = nn.LayerNorm(config.n_embd)
        self.mlp = MLP(config)
    
    def forward(self, x):
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x

class CausalSelfAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.c_attn = nn.Linear(config.n_embd, 3 * config.n_embd)
        self.c_proj = nn.Linear(config.n_embd, config.n_embd)
        self.n_head = config.n_head
        self.n_embd = config.n_embd
        self.dropout = config.dropout
    
    def forward(self, x):
        B, T, C = x.size()
        q, k, v = self.c_attn(x).split(self.n_embd, dim=2)
        k = k.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        q = q.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        v = v.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True, dropout_p=self.dropout if self.training else 0)
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.c_proj(y)

class MLP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.c_fc = nn.Linear(config.n_embd, 4 * config.n_embd)
        self.gelu = nn.GELU()
        self.c_proj = nn.Linear(4 * config.n_embd, config.n_embd)
        self.dropout = nn.Dropout(config.dropout)
    
    def forward(self, x):
        return self.dropout(self.c_proj(self.gelu(self.c_fc(x))))

def load_data(config):
    """Load Ecuador government data"""
    data_files = [
        'real_ecuador_data.jsonl',
        'sri_real_data.jsonl',
        'senae_real_data.jsonl',
        'registro_oficial_real_data.jsonl',
        'asamblea_real_data.jsonl',
    ]
    
    texts = []
    for file in data_files:
        path = Path(config.data_dir) / file
        if path.exists():
            with open(path) as f:
                for line in f:
                    item = json.loads(line)
                    texts.append(item.get('text', ''))
    
    return ' '.join(texts)

def train():
    config = Config()
    print(f"Training on {config.device}")
    
    # Load data
    print("Loading Ecuador government data...")
    text = load_data(config)
    print(f"Loaded {len(text):,} characters")
    
    # Simple char-level tokenization
    chars = sorted(list(set(text)))
    config.vocab_size = len(chars)
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for i, ch in enumerate(chars)}
    encode = lambda s: [stoi[c] for c in s]
    decode = lambda l: ''.join([itos[i] for i in l])
    
    # Prepare data
    data = torch.tensor(encode(text), dtype=torch.long)
    n = int(0.9 * len(data))
    train_data = data[:n]
    val_data = data[n:]
    
    # Model
    model = GPT(config).to(config.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Training loop
    for iter in range(config.max_iters):
        # Sample batch
        ix = torch.randint(len(train_data) - config.block_size, (config.batch_size,))
        x = torch.stack([train_data[i:i+config.block_size] for i in ix]).to(config.device)
        y = torch.stack([train_data[i+1:i+config.block_size+1] for i in ix]).to(config.device)
        
        # Forward
        logits, loss = model(x, y)
        
        # Backward
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        
        if iter % 100 == 0:
            print(f"iter {iter}: loss {loss.item():.4f}")
        
        if iter % config.eval_interval == 0:
            model.eval()
            with torch.no_grad():
                ix = torch.randint(len(val_data) - config.block_size, (config.batch_size,))
                x = torch.stack([val_data[i:i+config.block_size] for i in ix]).to(config.device)
                y = torch.stack([val_data[i+1:i+config.block_size+1] for i in ix]).to(config.device)
                _, val_loss = model(x, y)
                print(f"val loss: {val_loss.item():.4f}")
            model.train()
    
    # Save
    torch.save({
        'model': model.state_dict(),
        'config': config,
        'stoi': stoi,
        'itos': itos,
    }, 'yachaq_lex_model.pt')
    print("Model saved!")

if __name__ == '__main__':
    train()
