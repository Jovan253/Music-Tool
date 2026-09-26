import os
from fastapi import APIRouter, HTTPException
from services.jobs import get_job
from storage.supabase_storage import create_signed_url

router = APIRouter(prefix="/demo")

_VALID_STEMS = {"vocals", "drums", "bass", "other"}


def demo_job_id() -> str | None:
    return os.environ.get("DEMO_JOB_ID") or None


def _load_demo_job():
    # The job id comes from configuration and never from the request. These routes
    # are unauthenticated, so accepting an id would let anyone read anyone's stems.
    job_id = demo_job_id()
    if not job_id:
        raise HTTPException(status_code=404, detail="No demo track is configured")
    job = get_job(job_id)
    if job is None or job.status != "done" or not job.stems:
        raise HTTPException(status_code=404, detail="The demo track is unavailable")
    return job


@router.get("/job")
def get_demo_job():
    job = _load_demo_job()
    return {
        # The stored filename is whatever the uploader happened to call it, which is
        # rarely presentable. DEMO_TRACK_TITLE overrides it for display.
        "title": os.environ.get("DEMO_TRACK_TITLE") or job.filename,
        "processing_ms": job.processing_ms,
        "stems": sorted(job.stems.keys()),
    }


@router.get("/stems/{stem_name}")
def get_demo_stem(stem_name: str):
    if stem_name not in _VALID_STEMS:
        raise HTTPException(status_code=404, detail="Stem not found")
    job = _load_demo_job()
    path = job.stems.get(stem_name)
    if not path:
        raise HTTPException(status_code=404, detail="Stem not found")
    try:
        url = create_signed_url("stems", path, 3600)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not generate stem URL: {exc}")
    return {"url": url}
