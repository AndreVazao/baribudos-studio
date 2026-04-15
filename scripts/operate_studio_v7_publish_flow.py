from __future__ import annotations

import json
import os
from pathlib import Path


def _write_report(payload: dict) -> str:
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    report_path = artifacts_dir / "studio-v7-publish-flow-report.json"
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(report_path)


def main() -> int:
    project_id = str(os.getenv("PROJECT_ID", "")).strip()
    action = str(os.getenv("FLOW_ACTION", "readiness")).strip().lower() or "readiness"
    user_name = str(os.getenv("FLOW_USER_NAME", "Andre")).strip() or "Andre"
    user_role = str(os.getenv("FLOW_USER_ROLE", "owner")).strip() or "owner"

    if not project_id:
        payload = {"ok": False, "error": "project_id_missing"}
        payload["report"] = _write_report(payload)
        print(json.dumps(payload, ensure_ascii=False))
        return 1

    from studio_core.services.bootstrap_service import bootstrap_system
    from studio_core.services.production_readiness_service import (
        get_production_readiness,
        sync_ready_for_publish_with_readiness,
    )
    from studio_core.services.publication_package_freeze_service import (
        build_freeze_snapshot,
        freeze_publication_package_operationally,
    )
    from studio_core.services.website_publisher_service import (
        build_publish_envelope,
        get_project_publish_status,
        publish_project_to_website,
        revalidate_project_on_website,
    )
    from studio_core.core.storage import get_json_item

    bootstrap_system()

    try:
        if action == "readiness":
            result = get_production_readiness(project_id)
        elif action == "sync_readiness":
            result = sync_ready_for_publish_with_readiness(project_id)
        elif action == "freeze_preview":
            project = get_json_item("data/projects.json", project_id)
            if not project:
                raise ValueError("project_not_found")
            result = build_freeze_snapshot(project, user_name=user_name, user_role=user_role)
        elif action == "freeze":
            result = freeze_publication_package_operationally(project_id, user_name=user_name, user_role=user_role)
        elif action == "website_status":
            result = get_project_publish_status(project_id)
        elif action == "website_envelope":
            result = build_publish_envelope(project_id)
        elif action == "website_publish":
            result = publish_project_to_website(project_id)
        elif action == "website_revalidate":
            result = revalidate_project_on_website(project_id)
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
