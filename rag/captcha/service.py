"""Captcha Service - orchestrates adapters and provides a simple API.

This lightweight service supports plugging in adapters (like `mock_adapter`) and exposes
`solve_task` which returns a SolveResult-like dict. It enforces TTL and basic retry policies.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict

from rag.captcha import human_adapter, mock_adapter

logger = logging.getLogger(__name__)


class CaptchaService:
    def __init__(self, adapters: list = None):
        # Default to the mock adapter for tests/local runs. Callers can inject
        # a human-first adapter in production by passing `adapters=[human_adapter]`.
        self.adapters = adapters or [mock_adapter]

    def solve_task(self, task: Dict, timeout_seconds: int = 20) -> Dict:
        """Attempt to solve using configured adapters in order.

        Returns a dict with keys: task_id, adapter, result, confidence, latency_ms, timestamp
        """
        # Enforce TTL
        created = task.get("created_at")
        if created:
            created_ts = datetime.fromisoformat(created)
            delta = datetime.now(timezone.utc) - created_ts
            ttl = task.get("ttl_seconds", 180)
            if delta.total_seconds() > ttl:
                raise RuntimeError("Captcha task expired")

        for adapter in self.adapters:
            try:
                res = adapter.solve(task, timeout_seconds=timeout_seconds)
                # Convert dataclass or object to dict if needed
                return res.__dict__ if hasattr(res, "__dict__") else dict(res)
            except Exception as exc:  # pragma: no cover - adapters may raise
                logger.warning("Adapter %s failed: %s", getattr(adapter, "__name__", str(adapter)), exc)
                continue

        raise RuntimeError("All adapters failed")
