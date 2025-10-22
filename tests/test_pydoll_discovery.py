import importlib
from pathlib import Path


def test_discovery_module_exists():
    mod = importlib.import_module("rag.discovery.pydoll_discovery")
    assert hasattr(mod, "PydollDiscovery")


def test_discovery_class_api():
    mod = importlib.import_module("rag.discovery.pydoll_discovery")
    Discovery = mod.PydollDiscovery
    d = Discovery(output_dir=Path("rag/discovery/out_test"))
    assert callable(getattr(d, "capture_trace"))
