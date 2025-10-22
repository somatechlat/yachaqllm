"""Integration test for Pydoll CDP discovery.

This test will be skipped when `pydoll` is not available in the test environment.
It performs a lightweight navigation to example.com and asserts a trace file is produced.
"""
from __future__ import annotations

import importlib
import shutil
from pathlib import Path

import pytest


def _has_pydoll() -> bool:
    try:
        importlib.import_module("pydoll")

        return True
    except Exception:
        return False


@pytest.mark.skipif(not _has_pydoll(), reason="pydoll not installed")
def test_cdp_capture_creates_trace(tmp_path: Path) -> None:
    # import here to avoid import error when pydoll isn't present
    from rag.discovery.pydoll_cdp_discovery import PydollCDPDiscovery

    out_dir = tmp_path / "out"
    d = PydollCDPDiscovery(output_dir=out_dir)

    import asyncio


    trace = asyncio.run(d.capture_trace("https://example.com"))
    assert trace.get("trace_id")
    trace_file = out_dir / f"{trace['trace_id']}.json"
    assert trace_file.exists()

    # cleanup
    shutil.rmtree(out_dir, ignore_errors=True)
