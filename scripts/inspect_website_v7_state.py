from __future__ import annotations

import json
import os
from pathlib import Path
from urllib import error, parse, request


def _write_report(payload: dict) -> str:
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    report_path = artifacts_dir / "studio-v7-website-visibility-report.json"
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(report_path)


def _text(value) -> str:
    return str(value or "").strip()


def _base_url() -> str:
    explicit = _text(os.getenv("BARIBUDOS_WEBSITE_BASE_URL"))
    if explicit:
        return explicit.rstrip("/")

    publish_url = _text(os.getenv("BARIBUDOS_WEBSITE_PUBLISH_URL"))
    if publish_url and "/api/studio/publish" in publish_url:
        return publish_url.split("/api/studio/publish", 1)[0].rstrip("/")
    return ""


def _studio_api_key() -> str:
    return _text(os.getenv("BARIBUDOS_WEBSITE_PUBLISH_API_KEY")) or _text(os.getenv("STUDIO_PUBLISH_API_KEY"))


def _get_json(url: str, api_key: str) -> dict:
    req = request.Request(
        url,
        headers={
            "x-studio-api-key": api_key,
            "Accept": "application/json",
        },
        method="GET",
    )
    with request.urlopen(req, timeout=30) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {"ok": True}


def main() -> int:
    mode = _text(os.getenv("VISIBILITY_MODE")) or "project"
    project_id = _text(os.getenv("PROJECT_ID"))
    base_url = _base_url()
    api_key = _studio_api_key()

    if not base_url:
        payload = {"ok": False, "error": "website_base_url_missing"}
        payload["report"] = _write_report(payload)
        print(json.dumps(payload, ensure_ascii=False))
        return 1

    if not api_key:
        payload = {"ok": False, "error": "website_studio_api_key_missing"}
        payload["report"] = _write_report(payload)
        print(json.dumps(payload, ensure_ascii=False))
        return 1

    try:
        if mode == "project":
            if not project_id:
                raise ValueError("project_id_missing")
            url = f"{base_url}/api/studio/project-status/{parse.quote(project_id)}"
            result = _get_json(url, api_key)
        elif mode == "catalog":
            url = f"{base_url}/api/studio/catalog-status"
            result = _get_json(url, api_key)
        elif mode == "selling":
            url = f"{base_url}/api/studio/selling-status"
            result = _get_json(url, api_key)
        else:
            raise ValueError(f"unsupported_mode:{mode}")
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        payload = {
            "ok": False,
            "mode": mode,
            "project_id": project_id,
            "error": f"http_error:{exc.code}",
            "details": body,
        }
        payload["report"] = _write_report(payload)
        print(json.dumps(payload, ensure_ascii=False))
        return 1
    except Exception as exc:
        payload = {
            "ok": False,
            "mode": mode,
            "project_id": project_id,
            "error": str(exc),
        }
        payload["report"] = _write_report(payload)
        print(json.dumps(payload, ensure_ascii=False))
        return 1

    payload = {
        "ok": True,
        "mode": mode,
        "project_id": project_id,
        "base_url": base_url,
        "result": result,
    }
    payload["report"] = _write_report(payload)
    print(json.dumps({
        "ok": True,
        "mode": mode,
        "project_id": project_id,
        "report": payload["report"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
