from fastapi import APIRouter
from studio_core.core.storage import read_json, write_json

FILE = "data/sponsors.json"
router = APIRouter(prefix="/sponsors", tags=["sponsors"])

@router.get("")
def list_sponsors():
    return read_json(FILE, [])

@router.post("")
def create_sponsor(payload: dict):
    data = read_json(FILE, [])
    data.append(payload)
    write_json(FILE, data)
    return payload
