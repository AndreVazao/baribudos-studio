from __future__ import annotations

from fastapi import APIRouter, HTTPException

from studio_core.services.age_badge_service import generate_age_badge

router = APIRouter(prefix="/age-badges", tags=["age-badges"])


@router.post("/generate")
def create_age_badge(payload: dict) -> dict:
    try:
        saga_id = str(payload.get("saga_id", "baribudos")).strip()
        age_range = str(payload.get("age_range", "4-10")).strip()
        language = str(payload.get("language", "pt-PT")).strip()
        output_name = payload.get("output_name")

        result = generate_age_badge(
            saga_id=saga_id,
            age_range=age_range,
            language=language,
            output_name=output_name,
        )
        return {"ok": True, "result": result}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
