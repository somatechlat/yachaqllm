# YACHAQ-LEX Exact Training Plan

## Data We're Downloading NOW (Real, Not Mock)

### Tax Data (SRI) - 125 files
- **RUC databases**: All 24 provinces (1.5GB CSV) - company tax IDs
- **Tax collections**: Monthly 2022-2025
- **Tax inscriptions**: New companies
- **Dictionaries**: Tax codes, categories

### Legal Data (Asamblea + RO) - 318 files  
- **Laws**: 305 approved laws with RO citations
- **Registro Oficial PDFs**: 13+ legal publications

### Total: 9,328 files being downloaded

## Training Approach (nanochat style - NO MOCK)

### Step 1: Create Training Data from Real Files
```python
# Extract from downloaded CSVs/PDFs
# Example from SRI_RUC_Pichincha.csv:
{
  "instruction": "¿Cuál es el RUC de Empresa XYZ en Pichincha?",
  "response": "El RUC es 1234567890001, registrado en Pichincha..."
}

# Example from Asamblea law:
{
  "instruction": "¿Qué dice la Ley Orgánica del Código Monetario sobre...?",
  "response": "Según el RO 142 del 13-10-2025, la ley establece..."
}
```

### Step 2: QLoRA Training (Qwen2.5-7B)
- **Base**: Qwen2.5-7B-Instruct
- **Method**: 4-bit QLoRA (rank 64)
- **Data**: Real Ecuador government data
- **Hardware**: AWS p3.2xlarge or GCP A100
- **Time**: 24-48 hours

### Step 3: Synthetic Data Generation
After base training, use the model to generate MORE training examples:
```python
# Use trained model to create Q&A pairs from raw data
# Example: Feed RUC CSV → Generate 1000 tax questions
# Example: Feed law PDF → Generate 500 legal questions
```

### Step 4: Fine-tune Again
- Train on synthetic + real data
- Iterate 2-3 times
- Final model = Ecuador expert

## Current Status
- ✅ 9,328 datasets scraped
- 🔄 Downloading priority files (32 SRI files done, 1.5GB)
- ⏳ Next: Text extraction
- ⏳ Next: Training data creation
- ⏳ Next: QLoRA training

## NO MOCK - ALL REAL
Every training example comes from actual Ecuador government data.
