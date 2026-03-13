from fastapi import APIRouter
from studio_core.services.saga_service import list_sagas, create_saga

router = APIRouter(prefix="/sagas", tags=["sagas"])

@router.get("")
def get_sagas():
    return list_sagas()

@router.post("")
def new_saga(payload: dict):
    return create_saga(payload)
