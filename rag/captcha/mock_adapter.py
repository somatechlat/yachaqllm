"""Mock Captcha Adapter for tests and local runs.

This adapter deterministically returns a solved string for known test images and can
be used in unit/integration tests.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict


@dataclass
class SolveResult:
    task_id: str
    adapter: str
    result: str
    confidence: float
    latency_ms: int
    timestamp: str


def solve(task: Dict, timeout_seconds: int = 20) -> SolveResult:
    # For tests we simply return a deterministic value derived from the task id
    solution = f"SOLVE-{task.get('task_id', 'test')[:8]}"
    return SolveResult(
        task_id=task.get("task_id", ""),
        adapter="mock-adapter",
        result=solution,
        confidence=0.99,
        latency_ms=100,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
