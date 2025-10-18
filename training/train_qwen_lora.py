"""LoRA fine-tuning entry point for Qwen2.5-7B-Instruct using quantized loading."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training


DEFAULT_MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"


@dataclass
class RunConfig:
    model_name: str
    output_dir: Path
    train_path: Path
    eval_path: Optional[Path]
    max_steps: int
    per_device_train_batch_size: int
    per_device_eval_batch_size: int
    gradient_accumulation_steps: int
    learning_rate: float
    warmup_steps: int
    logging_steps: int
    save_steps: int
    eval_steps: int
    lora_r: int
    lora_alpha: int
    lora_dropout: float
    target_modules: Optional[list[str]]
    max_seq_length: int

    @classmethod
    def from_yaml(cls, path: Path) -> "RunConfig":
        with path.open("r", encoding="utf-8") as handle:
            raw: Dict[str, Any] = yaml.safe_load(handle)
        return cls(
            model_name=raw.get("model_name", DEFAULT_MODEL_NAME),
            output_dir=Path(raw["output_dir"]),
            train_path=Path(raw["train_path"]),
            eval_path=Path(raw["eval_path"]) if raw.get("eval_path") else None,
            max_steps=int(raw.get("max_steps", 1000)),
            per_device_train_batch_size=int(raw.get("per_device_train_batch_size", 1)),
            per_device_eval_batch_size=int(raw.get("per_device_eval_batch_size", 1)),
            gradient_accumulation_steps=int(raw.get("gradient_accumulation_steps", 8)),
            learning_rate=float(raw.get("learning_rate", 2e-4)),
            warmup_steps=int(raw.get("warmup_steps", 50)),
            logging_steps=int(raw.get("logging_steps", 10)),
            save_steps=int(raw.get("save_steps", 100)),
            eval_steps=int(raw.get("eval_steps", 100)),
            lora_r=int(raw.get("lora_r", 16)),
            lora_alpha=int(raw.get("lora_alpha", 32)),
            lora_dropout=float(raw.get("lora_dropout", 0.05)),
            target_modules=raw.get("target_modules"),
            max_seq_length=int(raw.get("max_seq_length", 1024)),
        )


def load_corpus(train_path: Path, eval_path: Optional[Path], max_seq_length: int, tokenizer):
    def build_dataset(path: Path):
        if path.suffix in {".json", ".jsonl"}:
            return load_dataset("json", data_files=str(path))
        if path.is_dir():
            return load_dataset("text", data_dir=str(path))
        return load_dataset("text", data_files=str(path))

    train_ds = build_dataset(train_path)["train"]
    eval_ds = build_dataset(eval_path)["train"] if eval_path else None

    def tokenize(batch: Dict[str, Any]) -> Dict[str, Any]:
        text_key = "text" if "text" in batch else list(batch.keys())[0]
        return tokenizer(batch[text_key], truncation=True, max_length=max_seq_length)

    train_ds = train_ds.map(tokenize, batched=True, remove_columns=train_ds.column_names)
    if eval_ds:
        eval_ds = eval_ds.map(tokenize, batched=True, remove_columns=eval_ds.column_names)
    return train_ds, eval_ds


def build_model_and_tokenizer(model_name: str, lora_cfg: RunConfig):
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype="float16",
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        trust_remote_code=True,
        quantization_config=quant_config,
    )
    model = prepare_model_for_kbit_training(model)
    target_modules = lora_cfg.target_modules or [
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ]
    lora_config = LoraConfig(
        r=lora_cfg.lora_r,
        lora_alpha=lora_cfg.lora_alpha,
        target_modules=target_modules,
        lora_dropout=lora_cfg.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    return model, tokenizer


def run_training(cfg: RunConfig) -> None:
    model, tokenizer = build_model_and_tokenizer(cfg.model_name, cfg)
    train_ds, eval_ds = load_corpus(cfg.train_path, cfg.eval_path, cfg.max_seq_length, tokenizer)

    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    training_args = TrainingArguments(
        output_dir=str(cfg.output_dir),
        per_device_train_batch_size=cfg.per_device_train_batch_size,
        per_device_eval_batch_size=cfg.per_device_eval_batch_size,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        learning_rate=cfg.learning_rate,
        warmup_steps=cfg.warmup_steps,
        logging_steps=cfg.logging_steps,
        save_steps=cfg.save_steps,
        eval_steps=cfg.eval_steps,
        max_steps=cfg.max_steps,
        evaluation_strategy="steps" if eval_ds else "no",
        save_total_limit=2,
        bf16=True,
        report_to=["wandb"],
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        data_collator=collator,
    )
    trainer.train()
    trainer.model.save_pretrained(cfg.output_dir / "adapter" )
    tokenizer.save_pretrained(cfg.output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LoRA fine-tuning for Qwen2.5-7B-Instruct.")
    parser.add_argument("config", type=Path, help="Path to YAML run configuration")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = RunConfig.from_yaml(args.config)
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    run_training(cfg)


if __name__ == "__main__":
    main()
