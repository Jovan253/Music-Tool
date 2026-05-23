from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.jobs import get_job

router = APIRouter()

_VALID_STEMS = {"vocals", "drums", "bass", "other"}


@router.get("/jobs/{job_id}/stems/{stem_name}")
def get_stem(job_id: str, stem_name: str):
    if stem_name not in _VALID_STEMS:
        raise HTTPException(status_code=404, detail="Stem not found")
    job = get_job(job_id)
    if job is None or job.status != "done" or job.stems is None:
        raise HTTPException(status_code=404, detail="Stem not found")
    path = job.stems.get(stem_name)
    if not path:
        raise HTTPException(status_code=404, detail="Stem not found")
    return FileResponse(path, media_type="audio/wav")
