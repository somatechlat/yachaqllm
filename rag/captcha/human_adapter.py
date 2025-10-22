from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

MANIFEST_DIR = Path("rag/ingest/comprehensive_data/sercop_captcha_queue")
CAPTCHA_SUBDIR = MANIFEST_DIR / "captchas"


def ensure_dirs():
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    CAPTCHA_SUBDIR.mkdir(parents=True, exist_ok=True)


@dataclass
class HumanTask:
    task_id: str
    created_at: str
    form_defaults: Dict[str, str]
    cookies: Dict[str, str]
    captcha_path: str
    referer: str
    search_url: str
    captcha_src: str
    user_agent: str
    ttl_hint_seconds: int = 180


def create_manifest_entry(task: HumanTask) -> None:
    ensure_dirs()
    manifest_file = MANIFEST_DIR / "manifest.jsonl"
    with manifest_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(task), ensure_ascii=False) + "\n")


def prepare_task(form_defaults: Dict[str, str], cookies: Dict[str, str], captcha_bytes: bytes, captcha_src: str, referer: str, search_url: str, user_agent: str = "YACHAQ-LEX/1.0") -> HumanTask:
    ensure_dirs()
    task_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()
    # persist captcha image
    # choose extension by inspection; default .png
    p = CAPTCHA_SUBDIR / f"{task_id}.png"
    p.write_bytes(captcha_bytes)

    task = HumanTask(
        task_id=task_id,
        created_at=created_at,
        form_defaults=form_defaults,
        cookies=cookies,
        captcha_path=str(Path("captchas") / p.name),
        referer=referer,
        search_url=search_url,
        captcha_src=captcha_src,
        user_agent=user_agent,
        ttl_hint_seconds=180,
    )
    create_manifest_entry(task)
    return task
