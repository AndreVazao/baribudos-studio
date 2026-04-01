from fastapi import APIRouter, HTTPException
from studio_core.services.saga_service import list_sagas, create_saga, update_saga

router = APIRouter(prefix="/sagas", tags=["sagas"])

@router.get("")
def get_sagas():
    return list_sagas()

@router.post("")
def new_saga(payload: dict):
    return create_saga(payload)

@router.patch("/{slug}")
def patch_saga(slug: str, payload: dict):
    try:
        return {"ok": True, "saga": update_saga(slug, payload or {})}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
