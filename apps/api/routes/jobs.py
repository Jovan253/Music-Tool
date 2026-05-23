from fastapi import APIRouter, HTTPException
from services.jobs import get_job

router = APIRouter()


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.job_id,
        "status": job.status,
        "filename": job.filename,
        "created_at": job.created_at,
        "stems": job.stems,
        "error": job.error,
    }
