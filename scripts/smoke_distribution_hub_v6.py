from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import mkdtemp


def main() -> int:
    temp_storage = Path(mkdtemp(prefix="baribudos_distribution_hub_v6_"))
    os.environ["BARIBUDOS_STORAGE_ROOT"] = str(temp_storage)

    from fastapi.testclient import TestClient
    from studio_core.api.main import app
    from studio_core.core.storage import read_json, write_json
    from studio_core.services.bootstrap_service import bootstrap_system

    bootstrap_system()

    project_id = "proj-v6-smoke-001"
    project_payload = {
        "id": project_id,
        "title": "Baribudos Smoke V6",
        "saga_slug": "baribudos",
        "saga_name": "Baribudos",
        "language": "pt-PT",
        "output_languages": ["pt-PT"],
        "status": "draft",
        "editorial_status": "draft",
        "created_by": "smoke",
        "created_by_name": "Smoke Runner",
        "cover_image": "https://cdn.example.com/cover.png",
        "illustration_path": "https://cdn.example.com/cover.png",
        "ready_for_publish": True,
        "commercial": {
            "internal_code": "SMOKE-V6",
            "currency": "EUR",
            "commercial_status": "draft",
            "website_marketing": {
                "public_state": "teaser_ready",
                "teaser_badge": "Em breve",
                "teaser_headline": "Baribudos Smoke V6",
                "teaser_subtitle": "Validação operacional do Distribution Hub V6.",
                "teaser_cta_label": "Ver teaser",
                "teaser_release_label": "Primeiras imagens",
                "teaser_gallery": [
                    "https://cdn.example.com/cover.png",
                    "https://cdn.example.com/gallery-1.png"
                ],
                "teaser_cover_url": "https://cdn.example.com/cover.png",
                "teaser_trailer_url": "https://cdn.example.com/trailer.mp4",
                "teaser_excerpt": "Excerto público do smoke test.",
                "teaser_visibility_notes": "Gerado por smoke test.",
                "prelaunch_enabled": False,
                "share_preview_images_during_production": True
            },
            "distribution_hub": {
                "version": "v6",
                "project_id": project_id,
                "primary_channel": "website",
                "notes": "Seed smoke test.",
                "channels": {
                    "website": {
                        "enabled": True,
                        "manual_status": "",
                        "attempts": 1,
                        "last_attempt": "",
                        "last_success_at": "",
                        "last_error": "",
                        "notes": "website channel ready"
                    },
                    "amazon": {
                        "enabled": True,
                        "manual_status": "planned",
                        "attempts": 0,
                        "last_attempt": "",
                        "last_success_at": "",
                        "last_error": "",
                        "notes": "amazon channel planned"
                    },
                    "youtube": {
                        "enabled": True,
                        "manual_status": "",
                        "attempts": 0,
                        "last_attempt": "",
                        "last_success_at": "",
                        "last_error": "",
                        "notes": ""
                    },
                    "audio": {
                        "enabled": True,
                        "manual_status": "",
                        "attempts": 0,
                        "last_attempt": "",
                        "last_success_at": "",
                        "last_error": "",
                        "notes": ""
                    }
                },
                "history": [],
                "created_at": "",
                "updated_at": "",
                "last_snapshot_at": ""
            }
        },
        "website_sync": {
            "publication_id": "proj-v6-smoke-001:website",
            "checksum": "smoke-checksum",
            "published_at": "2026-04-14T08:00:00+00:00"
        },
        "story": {
            "title": "Baribudos Smoke V6",
            "language": "pt-PT",
            "pages": [],
            "raw_text": "Texto base do smoke test."
        },
        "outputs": {
            "website": {
                "hero": "https://cdn.example.com/hero.png"
            }
        }
    }

    write_json("data/projects.json", [project_payload])

    with TestClient(app) as client:
        commercial_get = client.get(f"/api/project-commercial/{project_id}")
        assert commercial_get.status_code == 200, commercial_get.text

        commercial_patch = client.patch(
            f"/api/project-commercial/{project_id}?user_name=Andre&user_role=owner",
            json={
                "website_marketing": {
                    "public_state": "prelaunch_public",
                    "teaser_badge": "Pré-lançamento",
                    "teaser_cta_label": "Acompanhar lançamento"
                }
            },
        )
        assert commercial_patch.status_code == 200, commercial_patch.text

        hub_get = client.get(f"/api/distribution-hub/{project_id}")
        assert hub_get.status_code == 200, hub_get.text
        hub_payload = hub_get.json().get("distribution_hub", {})
        assert hub_payload.get("project_id") == project_id
        assert hub_payload.get("sales_readiness", {}).get("total", 0) >= 1
        assert isinstance(hub_payload.get("destinations", []), list)
        assert isinstance(hub_payload.get("external_outputs", []), list)

        hub_refresh = client.post(
            f"/api/distribution-hub/{project_id}/refresh?user_name=Andre&user_role=owner",
            json={},
        )
        assert hub_refresh.status_code == 200, hub_refresh.text

        website_status = client.get(f"/api/website-publisher/status/{project_id}")
        assert website_status.status_code == 200, website_status.text

    stored_projects = read_json("data/projects.json", [])
    report = {
        "ok": True,
        "storage_root": str(temp_storage),
        "project_id": project_id,
        "stored_projects": len(stored_projects) if isinstance(stored_projects, list) else 0,
        "distribution_hub_snapshot": hub_payload,
        "website_status": website_status.json(),
    }

    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    report_path = artifacts_dir / "distribution-hub-v6-smoke-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "report": str(report_path),
        "project_id": project_id,
        "destinations": len(hub_payload.get("destinations", [])),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
