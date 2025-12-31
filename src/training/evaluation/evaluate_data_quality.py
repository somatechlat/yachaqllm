import json
import random
import boto3
import time
from botocore.exceptions import ClientError

# Configuration
DATASET_PATH = "data/instruction_dataset/train.jsonl"
SAMPLE_SIZE = 50
REGION = "us-east-1"
# CORRECT ID FOUND: Llama 3 70B (not 3.1)
MODEL_ID = "meta.llama3-70b-instruct-v1:0"

def get_bedrock_client():
    return boto3.client("bedrock-runtime", region_name=REGION)

def evaluate_example(client, example):
    """
    Uses Llama 3 70B as a judge to evaluate the quality of a Q&A pair.
    """
    instruction = example["instruction"]
    output = example["output"]
    
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a strict expert legal evaluator. Your job is to grade the quality of an LLM training example designed for an Ecuadorian Legal AI.

Review the following Question (Instruction) and Answer (Output).
Grade it on three criteria:

1. **Reasoning (1-5)**: Does the answer break down the problem step-by-step? Is it logical?
2. **Citations (Yes/No)**: Does it cite specific Ecuadorian laws (e.g., Art. X COIP, LRTI)?
3. **Professionalism (1-5)**: Is the tone and structure appropriate for a lawyer or CPA?

FORMAT YOUR RESPONSE AS JSON ONLY:
{{
  "reasoning_score": <int>,
  "has_citations": <bool>,
  "professionalism_score": <int>,
  "critique": "<short comment>"
}}
<|eot_id|><|start_header_id|>user<|end_header_id|>
---
QUESTION:
{instruction}

ANSWER:
{output}
---
Evaluate this example.<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    body = json.dumps({
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.1,
        "top_p": 0.9
    })

    try:
        response = client.invoke_model(
            modelId=MODEL_ID,
            body=body
        )
        response_body = json.loads(response.get("body").read())
        result_text = response_body["generation"]
        
        # Extract JSON from potential wrapper text
        try:
            start = result_text.find("{")
            end = result_text.rfind("}") + 1
            json_str = result_text[start:end]
            return json.loads(json_str)
        except:
            return {
                "reasoning_score": 0,
                "has_citations": False,
                "professionalism_score": 0,
                "critique": "Failed to parse JSON evaluation"
            }
            
    except ClientError as e:
        print(f"Error invoking model: {e}")
        return None

def main():
    print(f"Loading dataset from {DATASET_PATH}...")
    try:
        with open(DATASET_PATH, 'r') as f:
            data = [json.loads(line) for line in f]
    except FileNotFoundError:
        print("Dataset not found!")
        return

    if len(data) < SAMPLE_SIZE:
        print(f"Dataset too small ({len(data)}), taking all.")
        sample = data
    else:
        sample = random.sample(data, SAMPLE_SIZE)
        
    print(f"Evaluating {len(sample)} examples using {MODEL_ID}...")
    
    client = get_bedrock_client()
    results = []
    
    for i, item in enumerate(sample):
        print(f"Evaluating {i+1}/{len(sample)}...", end="\r")
        eval_result = evaluate_example(client, item)
        if eval_result:
            results.append(eval_result)
            
    if not results:
        print("No results collected.")
        return

    # Calculate stats
    avg_reasoning = sum(r["reasoning_score"] for r in results) / len(results)
    avg_prof = sum(r["professionalism_score"] for r in results) / len(results)
    citation_rate = sum(1 for r in results if r["has_citations"]) / len(results) * 100
    
    print("\n" + "="*50)
    print("EVALUATION RESULTS (LLM-as-a-Judge: Llama 3 70B)")
    print("="*50)
    print(f"Samples Evaluated: {len(results)}")
    print(f"Average Reasoning Score (1-5): {avg_reasoning:.2f}")
    print(f"Average Professionalism Score (1-5): {avg_prof:.2f}")
    print(f"Citation Rate: {citation_rate:.1f}%")
    print("="*50)
    
    print("\nSample Critiques:")
    for i in range(min(5, len(results))):
        print(f"- {results[i]['critique']}")
        
    # Save Report
    with open("DATA_QUALITY_REPORT.md", "w") as f:
        f.write(f"# Data Quality Evaluation Report\n")
        f.write(f"**Date**: {time.strftime('%Y-%m-%d')}\n")
        f.write(f"**Model Judge**: {MODEL_ID}\n\n")
        f.write(f"## Scores\n")
        f.write(f"- **Reasoning**: {avg_reasoning:.2f}/5.0\n")
        f.write(f"- **Professionalism**: {avg_prof:.2f}/5.0\n")
        f.write(f"- **Citation Rate**: {citation_rate:.1f}%\n\n")
        f.write(f"## Sample Critiques\n")
        for i in range(min(5, len(results))):
             f.write(f"- {results[i]['critique']}\n")

if __name__ == "__main__":
    main()
