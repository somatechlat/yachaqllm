# YACHAQ-LEX

The best Ecuadorian legal AI model for law, taxes, customs, and government processes.

## Mission

Train a specialized LLM that provides accurate, verified answers about:
- Ecuadorian law and legal processes
- Tax regulations and SRI procedures
- Customs and SENAE requirements
- Government processes and regulations
- Court rulings and jurisprudence

## Architecture

Based on [nanochat](https://github.com/karpathy/nanochat) - minimal, efficient LLM training framework.

**Training Pipeline:**
1. **Data Collection** - Scrape verified Ecuadorian sources (government sites, academic repositories)
2. **Data Processing** - Extract text, validate quality, create training format
3. **Model Training** - Fine-tune base model (Qwen2.5-7B-Instruct) using nanochat
4. **Evaluation** - Test accuracy on real legal/tax questions
5. **Deployment** - Serve model via API

## Data Sources

### Government (CRITICAL)
- Registro Oficial - Laws and decrees
- SRI - Tax regulations
- Función Judicial - Court rulings
- Superintendencia de Compañías - Corporate regulations

### Academic Repositories (HIGH)
- 30+ Ecuadorian university repositories (DSpace)
- Legal, accounting, tax research
- Thesis and academic papers

**Target:** 50K-100K verified documents for 90-95% accuracy

## Project Structure

```
├── rag/ingest/          # Data collection scrapers
├── training/            # nanochat training scripts
├── rag/app/             # RAG API service
├── config/              # Source configurations
└── infra/aws/           # AWS infrastructure
```

## Current Status

- ✓ Core scrapers operational for priority government sources
- ✓ AWS S3 bucket (`yachaq-lex-raw-0017472631`) provisioned for raw data storage
- ⏳ Large-scale backfill and continuous ingestion in progress
- ⏳ nanochat training integration and evaluation pending

## Quality Standards

- NO synthetic/fake data
- NO hallucinated answers
- ONLY verified sources
- Truth and accuracy over quantity

## Tech Stack

- **Training:** nanochat (PyTorch, minimal dependencies)
- **Base Model:** Qwen2.5-7B-Instruct (Apache 2.0)
- **Data:** Python scrapers (requests, BeautifulSoup, Scrapy)
- **Storage:** AWS S3
- **Infrastructure:** AWS (SageMaker for training)

## Getting Started

```bash
# Install dependencies
pip install -r training/requirements.txt

# Run data collection
cd rag/ingest
python scrape_all.py

# Train model (after data collection complete)
cd training
python train_nanochat_yachaq.py
```

## License

Apache 2.0
