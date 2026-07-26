from __future__ import annotations

import json
import logging
import os
import shutil
import sys
import tempfile
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from specguard.engine.heuristic import run_heuristic_audit  # noqa: E402
from specguard.parsers.git_diff import parse_diff  # noqa: E402
from specguard.parsers.kiro_spec import parse_requirements, parse_tasks  # noqa: E402

REPORTS_TABLE = os.environ.get("SPECGUARD_REPORTS_TABLE")
REPORT_TTL_SECONDS = 7 * 24 * 60 * 60
MAX_BODY_BYTES = 200_000

log = logging.getLogger("specguard.lambda")
log.setLevel(logging.INFO)


def handler(event: dict, _context: object) -> dict:
    raw_body = event.get("body") or "{}"
    if len(raw_body.encode("utf-8")) > MAX_BODY_BYTES:
        return _response(413, {"error": f"request body exceeds {MAX_BODY_BYTES} bytes"})

    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError:
        return _response(400, {"error": "invalid JSON body"})

    requirements_md = body.get("requirements_md", "")
    tasks_md = body.get("tasks_md", "")
    diff_text = body.get("diff", "")
    spec_name = str(body.get("spec_name", "remote-spec"))[:200]

    if not requirements_md or not diff_text:
        return _response(400, {"error": "requirements_md and diff are required"})

    tmp_dir = Path(tempfile.mkdtemp())
    try:
        requirements = parse_requirements(_write_temp(tmp_dir, "requirements.md", requirements_md))
        tasks = parse_tasks(_write_temp(tmp_dir, "tasks.md", tasks_md)) if tasks_md else []
        changes = parse_diff(diff_text)
        report = run_heuristic_audit(spec_name, "remote", requirements, tasks, changes)
    except Exception:
        log.exception("audit failed")
        return _response(500, {"error": "audit failed - see server logs"})
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    report_id = str(uuid.uuid4())
    payload = report.to_dict()
    payload["report_id"] = report_id

    if REPORTS_TABLE:
        try:
            _store_report(report_id, payload)
        except Exception:
            log.exception("failed to persist report %s", report_id)
            payload["storage_warning"] = "report not persisted - see server logs"

    return _response(200, payload)


def _write_temp(tmp_dir: Path, name: str, content: str) -> Path:
    path = tmp_dir / name
    path.write_text(content, encoding="utf-8")
    return path


def _store_report(report_id: str, payload: dict) -> None:
    import boto3

    table = boto3.resource("dynamodb").Table(REPORTS_TABLE)
    table.put_item(
        Item={
            "report_id": report_id,
            "created_at": int(time.time()),
            "expires_at": int(time.time()) + REPORT_TTL_SECONDS,
            "payload": json.dumps(payload, ensure_ascii=False),
        }
    )


def _response(status: int, payload: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload, ensure_ascii=False),
    }
