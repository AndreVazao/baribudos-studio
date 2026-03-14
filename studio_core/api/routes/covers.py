from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.core.models import now_iso
from studio_core.core.storage import update_json_item
from studio_core.services.cover_service import build_cover

router = APIRouter(prefix="/covers", tags=["covers"])

PROJECTS_FILE = "data/projects.json"


@router.post("/build")
def create_cover(payload: dict) -> dict:
    try:
        result = build_cover(
            saga_id=str(payload.get("saga_id", "baribudos")).strip(),
            project_id=str(payload.get("project_id", "")).strip(),
            title=str(payload.get("title", "Nova História")).strip(),
            age_range=str(payload.get("age_range", "4-10")).strip(),
            language=str(payload.get("language", "pt-PT")).strip(),
            illustration_path=str(payload.get("illustration_path", "")).strip(),
            producer=str(payload.get("producer", "Produzido por Baribudos Studio")).strip(),
            output_name=payload.get("output_name"),
        )

        project_id = str(payload.get("project_id", "")).strip()
        if project_id:
            try:
                update_json_item(
                    PROJECTS_FILE,
                    project_id,
                    lambda current: {
                        **current,
                        "cover_image": result.get("file_path", ""),
                        "outputs": {
                            **(current.get("outputs", {}) or {}),
                            "covers": result
                        },
                        "updated_at": now_iso()
                    }
                )
            except Exception:
                pass

        return {"ok": True, "result": result}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
