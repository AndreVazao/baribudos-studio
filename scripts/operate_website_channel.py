from __future__ import annotations

import json
import os
from pathlib import Path


def _write_report(payload: dict) -> str:
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    report_path = artifacts_dir / "website-channel-operation-report.json"
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(report_path)


def main() -> int:
    project_id = str(os.getenv("PROJECT_ID", "")).strip()
    action = str(os.getenv("CHANNEL_ACTION", "status")).strip().lower() or "status"

    if not project_id:
        report = {"ok": False, "error": "project_id_missing"}
        report["report"] = _write_report(report)
        print(json.dumps(report, ensure_ascii=False))
        return 1

    from studio_core.services.bootstrap_service import bootstrap_system
    from studio_core.services.website_publisher_service import (
        build_publish_envelope,
        get_project_publish_status,
        publish_project_to_website,
        revalidate_project_on_website,
        unpublish_project_on_website,
    )

    bootstrap_system()

    try:
        if action == "status":
            result = get_project_publish_status(project_id)
        elif action == "envelope":
            result = {
                "ok": True,
                "project_id": project_id,
                "envelope": build_publish_envelope(project_id),
            }
        elif action == "publish":
            result = publish_project_to_website(project_id)
        elif action == "revalidate":
            result = revalidate_project_on_website(project_id)
        elif action == "unpublish":
            result = unpublish_project_on_website(project_id)
        else:
            raise ValueError(f"unsupported_action:{action}")
    except Exception as exc:
        payload = {
            "ok": False,
            "project_id": project_id,
            "action": action,
            "error": str(exc),
        }
        payload["report"] = _write_report(payload)
        print(json.dumps(payload, ensure_ascii=False))
        return 1

    payload = {
        "ok": True,
        "project_id": project_id,
        "action": action,
        "result": result,
    }
    payload["report"] = _write_report(payload)
    print(json.dumps({
        "ok": True,
        "project_id": project_id,
        "action": action,
        "report": payload["report"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
