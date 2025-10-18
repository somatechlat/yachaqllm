from rag.eval.run_eval import evaluate_records


def test_evaluate_records_handles_valid_citations():
    records = [
        {
            "citations": [
                {
                    "source": "SRI",
                    "ro_number": "RO 563",
                    "article": "Art. 72",
                    "url": "https://www.sri.gob.ec/ro-563",
                }
            ],
            "valid_as_of": "2025-10-10",
        },
        {
            "citations": [],
            "valid_as_of": None,
        },
    ]
    metrics = evaluate_records(records)
    assert metrics["count"] == 2.0
    assert metrics["citation_accuracy"] == 0.5
    assert metrics["hallucination_rate"] == 0.5
    assert metrics["freshness_coverage"] == 0.5


def test_evaluate_records_empty_dataset():
    metrics = evaluate_records([])
    assert metrics["count"] == 0.0
    assert metrics["citation_accuracy"] == 0.0
    assert metrics["hallucination_rate"] == 0.0
    assert metrics["freshness_coverage"] == 0.0
