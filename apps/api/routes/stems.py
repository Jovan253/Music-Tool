from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_user
from services.jobs import get_job
from storage.supabase_storage import create_signed_url

router = APIRouter()

_VALID_STEMS = {"vocals", "drums", "bass", "other"}


@router.get("/jobs/{job_id}/stems/{stem_name}")
def get_stem(job_id: str, stem_name: str, user_id: str = Depends(get_current_user)):
    if stem_name not in _VALID_STEMS:
        raise HTTPException(status_code=404, detail="Stem not found")
    job = get_job(job_id, user_id=user_id)
    if job is None or job.status != "done" or job.stems is None:
        raise HTTPException(status_code=404, detail="Stem not found")
    path = job.stems.get(stem_name)
    if not path:
        raise HTTPException(status_code=404, detail="Stem not found")
    return {"url": create_signed_url("stems", path, 3600)}
