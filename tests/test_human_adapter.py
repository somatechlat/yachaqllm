import tempfile
import shutil
from pathlib import Path

from rag.captcha import human_adapter


def test_prepare_task_writes_manifest(tmp_path):
    # point adapter dirs to tmp_path using env override by monkeypatching constants
    old_manifest_dir = human_adapter.MANIFEST_DIR
    old_captcha_subdir = human_adapter.CAPTCHA_SUBDIR
    try:
        human_adapter.MANIFEST_DIR = Path(tmp_path) / "sercop_captcha_queue"
        human_adapter.CAPTCHA_SUBDIR = human_adapter.MANIFEST_DIR / "captchas"
        # prepare a dummy task
        form_defaults = {"a": "b"}
        cookies = {"sid": "123"}
        captcha_bytes = b"PNGDATA"
        task = human_adapter.prepare_task(form_defaults=form_defaults, cookies=cookies, captcha_bytes=captcha_bytes, captcha_src="http://example/captcha.png", referer="http://example/", search_url="http://example/")
        manifest_file = human_adapter.MANIFEST_DIR / "manifest.jsonl"
        assert manifest_file.exists()
        content = manifest_file.read_text(encoding="utf-8")
        assert task.task_id in content
    finally:
        human_adapter.MANIFEST_DIR = old_manifest_dir
        human_adapter.CAPTCHA_SUBDIR = old_captcha_subdir