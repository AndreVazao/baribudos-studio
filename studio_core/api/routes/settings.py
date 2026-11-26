from fastapi import APIRouter, Depends
from studio_core.services.auth_principal import require_roles
from studio_core.services.settings_service import get_settings, update_settings
router = APIRouter(prefix="/settings", dependencies=[Depends(require_roles("owner", "admin"))], tags=["settings"])
@router.get("")
def read_settings():
    return get_settings()
@router.post("")
def save_settings(payload: dict):
    return update_settings(payload)
