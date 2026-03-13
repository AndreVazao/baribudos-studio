from studio_core.core.storage import read_json, write_json
from uuid import uuid4

JOBS_FILE = "data/jobs.json"

def create_job(type, payload):
    jobs = read_json(JOBS_FILE, [])
    job = {
        "id": str(uuid4()),
        "type": type,
        "status": "queued",
        "payload": payload
    }
    jobs.append(job)
    write_json(JOBS_FILE, jobs)
    return job

def list_jobs():
    return read_json(JOBS_FILE, [])
