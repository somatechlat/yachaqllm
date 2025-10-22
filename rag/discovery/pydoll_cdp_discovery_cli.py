"""CLI wrapper to run the async Pydoll CDP discovery.

This script is intentionally lightweight: it will raise a friendly error if Pydoll
is not installed. Use it for local interactive capture and debugging.
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from rag.discovery.pydoll_cdp_discovery import PydollCDPDiscovery, PydollNotInstalled

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _run(url: str, out: Optional[str] = None) -> int:
    try:
        d = PydollCDPDiscovery(output_dir=out or "rag/discovery/out_cdp")
        trace = await d.capture_trace(url)
        print(f"Wrote trace {trace.get('trace_id')} to {d.output_dir}")
        return 0
    except PydollNotInstalled as e:
        logger.error(str(e))
        return 2


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: python -m rag.discovery.pydoll_cdp_discovery_cli <url> [out_dir]")
        return 1
    url = argv[0]
    out = argv[1] if len(argv) > 1 else None
    return asyncio.run(_run(url, out))


if __name__ == "__main__":
    raise SystemExit(main())
