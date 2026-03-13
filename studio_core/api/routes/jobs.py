from fastapi import APIRouter
from studio_core.services.job_service import create_job, list_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("")
def jobs():
    return list_jobs()

@router.post("")
def new_job(payload: dict):
    return create_job(payload.get("type"), payload)
