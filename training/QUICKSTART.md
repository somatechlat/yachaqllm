# YACHAQ-LEX Training Quick Start

## 🎯 Current Status

✅ **6,616 files downloaded** (71% complete)
✅ **9,328 JSONL entries** ready for training
✅ **Real data from**: SRI, Registro Oficial, Asamblea, GAD, Academic sources

**WE CAN START TRAINING NOW!**

---

## 📋 Step-by-Step Guide

### Step 1: Generate Synthetic Questions (Local)

```bash
cd training/

# Install dependencies
pip install -r requirements.txt

# Generate 1M questions (takes ~2 hours)
python generate_synthetic_questions.py
```

**Output**: `synthetic_data/synthetic_batch_*.jsonl` (1M questions, ~500MB)

---

### Step 2: Option A - Train Locally (if you have GPU)

```bash
# Requires: RTX 3090/4090 (24GB) or A100
python train_sagemaker.py
```

**Time**: ~95 hours
**Cost**: ~$50 electricity

---

### Step 2: Option B - Train on SageMaker (Recommended)

#### 2.1 Setup AWS

```bash
# Install AWS CLI
pip install awscli boto3 sagemaker

# Configure AWS
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1)
```

#### 2.2 Create S3 Bucket

```bash
aws s3 mb s3://yachaq-lex-data
```

#### 2.3 Update deploy_sagemaker.py

Edit `deploy_sagemaker.py`:
```python
REGION = "us-east-1"  # Your region
ROLE = "arn:aws:iam::123456789:role/SageMakerRole"  # Your IAM role
BUCKET = "yachaq-lex-data"  # Your bucket
```

#### 2.4 Start Training

```bash
python deploy_sagemaker.py
```

**Time**: ~95 hours (spot instances)
**Cost**: ~$39

---

### Step 3: Monitor Training

```bash
# Check SageMaker console
# https://console.aws.amazon.com/sagemaker/

# Or use CLI
aws sagemaker list-training-jobs --max-results 5
```

---

### Step 4: Evaluate Model

After training completes, test on real exam questions:

```bash
python evaluate_model.py --model-path ./output
```

**Target**: >85% accuracy on 60 exam questions

---

## 🎛️ Configuration Options

### Generate More Questions

Edit `generate_synthetic_questions.py`:
```python
total_target = 3000000  # 3M questions
```

### Adjust Training

Edit `train_sagemaker.py`:
```python
num_train_epochs = 5  # More epochs
learning_rate = 1e-4  # Lower LR
```

### Use Bigger GPU

Edit `deploy_sagemaker.py`:
```python
INSTANCE_TYPE = "ml.g5.12xlarge"  # 4x A10G (faster)
```

---

## 💰 Cost Estimates

### Development (One-time)
- Synthetic generation: $0 (local)
- S3 storage (50GB): $5/month
- Training (spot): $39
- Testing: $10
**Total: ~$54**

### Production (Monthly)
- SageMaker endpoint: $730/month
- S3 storage: $5/month
**Total: ~$735/month**

### Alternative: Local Deployment
- RTX 4090: $1,600 (one-time)
- Electricity: $10/month
**Break-even: 2-3 months**

---

## 📊 Expected Results

### After Training:
- **Exam accuracy**: 85-90%
- **Spanish quality**: 90%+
- **Legal citations**: 80%+
- **Response time**: <2s
- **Hallucination rate**: <5%

---

## 🚨 Troubleshooting

### "No JSONL files found"
```bash
# Check data exists
ls -lh ../rag/ingest/*.jsonl
```

### "Out of memory"
```python
# Reduce batch size in train_sagemaker.py
per_device_train_batch_size = 2  # Instead of 4
```

### "AWS credentials not found"
```bash
aws configure
# Enter your credentials
```

### "Spot instance interrupted"
- SageMaker auto-resumes from checkpoint
- No action needed

---

## 🎯 Next Steps After Training

1. ✅ Evaluate on test set
2. ✅ Deploy to SageMaker endpoint
3. ✅ Create API wrapper
4. ✅ Build web interface
5. ✅ Add RAG for document retrieval
6. ✅ Monitor and improve

---

## 📞 Support

Issues? Check:
- AWS SageMaker logs
- CloudWatch logs
- Training metrics in S3

---

## 🚀 Ready to Start?

```bash
# 1. Generate questions
python generate_synthetic_questions.py

# 2. Train on SageMaker
python deploy_sagemaker.py

# 3. Wait ~95 hours ☕

# 4. Celebrate! 🎉
```

**Let's build YACHAQ-LEX!** 🇪🇨
