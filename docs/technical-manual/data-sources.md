# Data Sources

This document outlines the primary and secondary data sources for the YACHAQ-LEX project.

## Primary Sources

### 1. Official Gazette (`Registro Oficial`)

- **URL:** `https://www.registroficial.gob.ec/`
- **Data Type:** Unstructured (PDF)
- **Content:** The official text of all laws, decrees, and regulations.
- **Access Method:** The download links for each publication follow a predictable pattern. We can automate the discovery and download of new issues.

### 2. Open Data Portal (`datosabiertos.gob.ec`)

- **URL:** `https://www.datosabiertos.gob.ec/`
- **Data Type:** Structured (CSV, XLSX)
- **Content:** A wide range of datasets from various government entities.
- **Key Datasets:**
    - **Registro Único de Contribuyentes (RUC):** The official registry of taxpayers from the SRI.

## Secondary Sources

### 1. National Assembly (`asambleanacional.gob.ec`)

- **URL:** `https://www.asambleanacional.gob.ec/es/leyes-aprobadas`
- **Data Type:** Unstructured (PDF)
- **Content:** The full text of approved laws.
- **Notes:** A good source for cross-referencing, but the Official Gazette is the primary source of truth.

## Sources Requiring Further Research

### 1. Constitutional Court (`corteconstitucional.gob.ec`)

- **URL:** `https://www.corteconstitucional.gob.ec/`
- **Data Type:** Unstructured (PDF)
- **Content:** Rulings and decisions of the Constitutional Court.
- **Notes:** Further investigation is needed to find a reliable way to access their publications.

## Global Foundation Corpora

These corpora provide the large-scale text backbone for pretraining. All entries below include license notes to keep the stack compliant.

- **Dolma (AI2):** ~3T tokens. License: ODC-BY. Coverage: web, papers, code, books, encyclopedias. Source: `https://huggingface.co/datasets/allenai/dolma`.
- **RefinedWeb (TII):** 600B tokens from Common Crawl with multi-stage filtering. License: ODC-BY. Source: `https://huggingface.co/datasets/tiiuae/falcon-refinedweb`.
- **FineWeb (Hugging Face):** 15T tokens across 96 Common Crawl snapshots with MinHash dedup. License: ODC-BY. Source: `https://huggingface.co/datasets/HuggingFaceFW/fineweb`.
- **RedPajama (Together):** 1T token multi-source mix following the LLaMA recipe. License: per subset (mostly ODC-BY/CC). Source: `https://huggingface.co/datasets/togethercomputer/RedPajama-Data-V2`.
- **C4 (Google):** Cleaned Common Crawl baseline. License: ODC-BY. Source: `https://huggingface.co/datasets/c4`.
- **The Pile (EleutherAI):** 825 GiB / 22 subsets. License: per subset; exclude Books3. Source: `https://pile.eleuther.ai/`.
- **Wikipedia Dumps:** CC-BY-SA. Pull latest en/es dumps. Source: `https://dumps.wikimedia.org/`.
- **Project Gutenberg:** US public domain books. Source: `https://www.gutenberg.org/`.
- **arXiv CC slices:** Use only CC-licensed papers and retain attribution. Source: `https://huggingface.co/datasets/arxiv_dataset`.

## Code and Software Documentation

- **The Stack v2 (BigCode):** 6.4 TB permissive code from Software Heritage. License: permissive OSS only. Source: `https://huggingface.co/datasets/bigcode/the-stack-dedup`.
- **StarCoder2Data:** Adds issues, docs, notebooks. License: permissive OSS only. Source: `https://huggingface.co/datasets/bigcode/starcoderdata`.

## Supervised Instruction Tuning

- **FLAN Collection:** Aggregated task prompts. License: per component (mostly academic-friendly). Source: `https://github.com/google-research/FLAN/tree/main/flan`.
- **Super-Natural Instructions:** 1,616 tasks with expert prompts. License: Apache 2.0. Source: `https://huggingface.co/datasets/super_natural_instructions`.
- **P3 / PromptSource:** Prompt templates for 170+ datasets. License: Apache 2.0. Source: `https://github.com/bigscience-workshop/promptsource`.
- **Databricks Dolly-15k:** 15k CC-BY-SA instructions. Source: `https://huggingface.co/datasets/databricks/databricks-dolly-15k`.
- **OpenOrca:** GPT-augmented FLAN mix. License: Apache 2.0. Source: `https://huggingface.co/datasets/Open-Orca/OpenOrca`.

## Preference Data (DPO/RLHF)

- **Anthropic HH-RLHF:** Helpful/harmless pairwise data. License: CC-BY-SA. Source: `https://huggingface.co/datasets/Anthropic/hh-rlhf`.

## Evaluation Suites

- **MMLU:** General knowledge benchmark. License: Apache 2.0. Source: `https://huggingface.co/datasets/cais/mmlu`.
- **HellaSwag:** Commonsense reasoning. License: MIT. Source: `https://huggingface.co/datasets/Rowan/hellaswag`.
- **ARC (Challenge/Easy):** Science QA. License: CC-BY-SA. Source: `https://huggingface.co/datasets/ai2_arc`.
- **TruthfulQA:** Misconception resilience. License: MIT. Source: `https://huggingface.co/datasets/truthful_qa`.
- **GSM8K:** Math word problems. License: MIT. Source: `https://huggingface.co/datasets/gsm8k`.
- **APPS / HumanEval / MBPP:** Code evaluation benchmarks. Licenses: MIT/Apache. Sources: `https://huggingface.co/datasets/codeparrot/apps`, `https://github.com/openai/human-eval`, `https://github.com/google-research/google-research/tree/master/mbpp`.

## Retrieval and RAG Testing

- **BEIR:** 18 retrieval datasets. License: per subset (mostly public). Source: `https://huggingface.co/datasets/beir/beir`.
- **MS MARCO:** Web passage ranking. License: Microsoft Research terms. Source: `https://github.com/microsoft/MSMARCO-Document-Ranking`.
- **Natural Questions:** Google queries plus Wikipedia answers. License: CC BY-SA 3.0. Source: `https://ai.google.com/research/NaturalQuestions/download`.
- **KILT:** Knowledge-intensive tasks aligned to Wikipedia. License: CC BY-SA. Source: `https://huggingface.co/datasets/facebook/kilt_tasks`.

## Safety and Toxicity Datasets

- **RealToxicityPrompts:** Toxicity prompts with scores. License: MIT. Source: `https://huggingface.co/datasets/allenai/real-toxicity-prompts`.
- **Civil Comments / Jigsaw:** Toxicity labels with identity annotations. License: CC BY 4.0. Source: `https://www.kaggle.com/c/jigsaw-unintended-bias-in-toxicity-classification`.
- **Wikipedia Detox:** Talk page moderation labels. License: CC BY-SA. Source: `https://figshare.com/articles/dataset/Wikipedia_Talk_Labels_Toxicity/4054689`.

## Exclusions and Guardrails

- **Books3:** Exclude to avoid copyright violations; do not mirror derivatives.
- **Unlicensed Crawls:** Only ingest datasets with explicit ODC/CC/OSS terms. Maintain attribution logs for every download batch.
