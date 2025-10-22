"""Lightweight discovery runner (skeleton)

This module provides a minimal discovery runner that captures a page via HTTP GET and
produces a canonical trace JSON and raw response artifact. It is intentionally lightweight
so it can be used before full Pydoll integration.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PydollDiscovery:
    """Minimal discovery runner producing a canonical trace (non-CDP).

    Notes:
    - This is a stop-gap implementation that produces traces conforming to
      `docs/trace-schema.md`. Full Pydoll-based discovery will be implemented in Sprint 2.
    """

    def __init__(self, output_dir: str | Path = "rag/discovery/out") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def capture_trace(self, url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 15) -> Dict:
        """Capture a minimal trace for the given URL and return the trace dict.

        This performs a simple GET request and writes raw response + trace JSON.
        """
        trace_id = f"trace-{int(datetime.now(timezone.utc).timestamp())}-{uuid.uuid4().hex[:8]}"
        capture_time = datetime.now(timezone.utc).isoformat()

        headers = headers or {"User-Agent": "Yachaq-Discovery/1.0"}

        logger.info("Fetching URL: %s", url)
        resp = requests.get(url, headers=headers, timeout=timeout)

        # Save raw response
        raw_key = f"{trace_id}.response.html"
        raw_path = self.output_dir / raw_key
        raw_path.write_bytes(resp.content)

        # Build minimal trace per docs/trace-schema.md
        trace = {
            "trace_version": "1.0",
            "trace_id": trace_id,
            "capture_time": capture_time,
            "source": {"source_id": "ad-hoc", "source_name": "ad-hoc-run", "environment": "local"},
            "page_url": url,
            "browser": {"user_agent": headers.get("User-Agent"), "browser_version": "n/a", "headless": False, "platform": "requests"},
            "session": {"session_id": trace_id, "cookie_summary": {k: {"present": True, "expires": None, "secure": False} for k in resp.cookies.keys()}},
            "form_extractions": [],
            "events": [
                {
                    "event_id": "e-0",
                    "type": "document",
                    "initiator": "requests-client",
                    "request": {"method": "GET", "url": url, "headers": dict(resp.request.headers)},
                    "response": {"status": resp.status_code, "headers": dict(resp.headers), "body_snippet": resp.text[:1024], "body_size": len(resp.content)},
                    "timestamp_start": capture_time,
                    "timestamp_end": datetime.now(timezone.utc).isoformat(),
                    "replayable_hint": True,
                }
            ],
            "screenshots": [],
            "artifacts": {"raw_response_keys": {"e-0": str(raw_path)}},
            "metadata": {"capture_agent": "pydoll_discovery_skeleton"},
            "audit": {"captchas": [], "solver_summary": {"total_attempts": 0, "successes": 0, "avg_latency_ms": 0}},
        }

        trace_path = self.output_dir / f"{trace_id}.json"
        trace_path.write_text(json.dumps(trace, ensure_ascii=False, indent=2))

        logger.info("Wrote trace to %s", trace_path)
        return trace


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Minimal discovery runner (skeleton)")
    parser.add_argument("url", help="URL to capture")
    parser.add_argument("--output-dir", default="rag/discovery/out")
    args = parser.parse_args()

    d = PydollDiscovery(output_dir=args.output_dir)
    trace = d.capture_trace(args.url)
    print(f"Trace written: {trace['trace_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
