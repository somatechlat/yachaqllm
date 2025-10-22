from rag.captcha.service import CaptchaService
from datetime import datetime, timezone


def test_mock_solve():
    svc = CaptchaService()
    task = {
        "task_id": "t1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ttl_seconds": 300,
        "image_key": "captchas/t1.png",
    }
    res = svc.solve_task(task)
    assert res["task_id"] == "t1"
    assert res["adapter"] == "mock-adapter"
    assert res["confidence"] > 0.9
