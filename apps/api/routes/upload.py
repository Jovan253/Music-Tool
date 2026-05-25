import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from auth import get_current_user
from services.jobs import create_job, update_job
from workers.separation import run_separation
from job_queue import get_queue
from storage.supabase_storage import upload_file

log = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a"}
MAX_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

_MIME_FOR_EXT = {"mp3": "audio/mpeg", "wav": "audio/wav", "m4a": "audio/mp4"}


@router.post("/upload", status_code=201)
async def upload_audio(
    file: UploadFile,
    user_id: str = Depends(get_current_user),
):
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50 MB")

    job = create_job(filename=file.filename or f"upload.{ext}", file_path="", user_id=user_id)
    supabase_path = f"{job.job_id}.{ext}"
    log.info("Uploading %s to Supabase uploads bucket at path %s", file.filename, supabase_path)
    try:
        upload_file("uploads", supabase_path, contents, _MIME_FOR_EXT.get(ext, "application/octet-stream"))
        log.info("Supabase upload succeeded: %s", supabase_path)
    except Exception as exc:
        log.error("Supabase upload FAILED: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Storage upload failed: {exc}") from exc
    update_job(job.job_id, file_path=supabase_path)

    get_queue().enqueue(run_separation, job.job_id, job_timeout=900)

    return JSONResponse(
        status_code=201,
        content={"job_id": job.job_id, "status": "processing", "filename": job.filename},
    )
