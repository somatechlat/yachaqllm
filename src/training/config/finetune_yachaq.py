# Yachaq LLM EC - Training Configuration
# Based on nanoGPT config style

# Model to fine-tune
init_from = 'gpt2'  # or 'Equall/Saul-7B-Base' for SaulLM

# Data location (prepared by prepare_data.py)
data_dir = '/Users/macbookpro201916i964gb1tb/Downloads/1x/yachaq/training/data'
out_dir = 'out-yachaq-ec'

# Training settings
batch_size = 4
block_size = 1024  # context length
max_iters = 50000
eval_interval = 500
eval_iters = 100

# Learning rate
learning_rate = 3e-5  # Lower for fine-tuning
min_lr = 3e-6
warmup_iters = 1000
lr_decay_iters = 50000

# Optimizer
weight_decay = 0.1
beta1 = 0.9
beta2 = 0.95
grad_clip = 1.0

# System
device = 'cuda'  # or 'mps' for Mac
dtype = 'bfloat16'  # or 'float16'
compile = True  # PyTorch 2.0

# Logging
wandb_log = True
wandb_project = 'yachaq-llm-ec'
wandb_run_name = 'finetune-ecuador'

# Checkpointing
always_save_checkpoint = True
