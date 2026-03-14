from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.cover_service import build_cover

router = APIRouter(prefix="/covers", tags=["covers"])


@router.post("/build")
def create_cover(payload: dict) -> dict:
    try:
        result = build_cover(
            saga_id=str(payload.get("saga_id", "baribudos")).strip(),
            project_id=str(payload.get("project_id", "")).strip(),
            title=str(payload.get("title", "Nova História")).strip(),
            age_range=str(payload.get("age_range", "4-10 anos")).strip(),
            illustration_path=str(payload.get("illustration_path", "")).strip(),
            producer=str(payload.get("producer", "Produzido por Baribudos Studio")).strip(),
            output_name=payload.get("output_name"),
        )
        return {"ok": True, "result": result}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
