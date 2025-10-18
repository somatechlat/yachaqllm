"""Simple evaluation pipeline for YACHAQ-LEX responses."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, List


def has_valid_citation(citation: Dict[str, str]) -> bool:
    required_fields = {"source", "ro_number", "article", "url"}
    if not required_fields.issubset(citation):
        return False
    return all(str(citation[field]).strip() for field in required_fields)


def evaluate_records(records: Iterable[Dict[str, object]]) -> Dict[str, float]:
    total = 0
    citation_hits = 0
    hallucinations = 0
    freshness_hits = 0

    for record in records:
        total += 1
        citations = record.get("citations", [])
        validity_flag = bool(record.get("valid_as_of"))
        if citations and all(has_valid_citation(c) for c in citations):
            citation_hits += 1
        else:
            hallucinations += 1
        if validity_flag:
            freshness_hits += 1

    if total == 0:
        return {"count": 0.0, "citation_accuracy": 0.0, "hallucination_rate": 0.0, "freshness_coverage": 0.0}

    return {
        "count": float(total),
        "citation_accuracy": citation_hits / total,
        "hallucination_rate": hallucinations / total,
        "freshness_coverage": freshness_hits / total,
    }


def load_records(path: Path) -> List[Dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate YACHAQ-LEX responses.")
    parser.add_argument("dataset", type=Path, help="Path to JSONL dataset with citations and validity metadata")
    args = parser.parse_args()

    records = load_records(args.dataset)
    metrics = evaluate_records(records)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
