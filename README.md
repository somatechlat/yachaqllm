# Yachaq LLM EC - Project Structure
## First Ecuadorian Expert LLM

This repository contains the complete framework for training **Yachaq LLM EC**, the first Large Language Model deeply specialized in Ecuadorian law, culture, and knowledge.

## 📂 Architecture

```
yachaqllm/
├── docs/                   # Documentation (ISO/SRS)
│   ├── srs/                # Software Requirements Specs
│   ├── iso/                # ISO Compliance
│   └── architecture/       # System Design
├── src/                    # Source Code
│   ├── collectors/         # Data Collection Framework
│   │   ├── yachaq_collector.py
│   │   └── discover_ecuador.py
│   ├── training/           # ML Training Pipeline
│   │   ├── data_prep/      # Data Processing (nanoGPT style)
│   │   ├── config/         # Training Configurations
│   │   └── sagemaker/      # AWS Integration
│   ├── registry/           # Data Sources Registry
│   └── utils/              # Shared Utilities
├── tests/                  # Unit & Integration Tests
├── deploy/                 # Deployment Scripts (Terraform/CDK)
└── notebooks/              # Jupyter Notebooks for Analysis
```

## 🚀 Getting Started

### 1. Data Collection
```bash
# Discover sources
python3 src/collectors/discover_ecuador_sources.py

# Download specific category
python3 src/collectors/yachaq_collector.py --category legal
```

### 2. Training
```bash
# Prepare data (tokenize)
python3 src/training/data_prep/prepare_data.py

# Launch SageMaker training (AWS)
python3 src/training/sagemaker/launch_training.py
```

## ⚖️ Legal Compliance (LOPDP)
All data processing complies with the **Ley Orgánica de Protección de Datos Personales (LOPDP)** of Ecuador.
- Public sources only
- No PII collection
- Source registry logging

## 📄 License
MIT License
