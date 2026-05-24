from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from services.jobs import create_job, update_job
from workers.separation import run_separation
from job_queue import get_queue

router = APIRouter()

ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a"}
ALLOWED_MIME_TYPES = {"audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4", "audio/x-m4a", "video/mp4"}
MAX_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

UPLOADS_DIR = Path(__file__).parent.parent / "uploads"


@router.post("/upload", status_code=201)
async def upload_audio(file: UploadFile):
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50 MB")

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    job = create_job(filename=file.filename or f"upload.{ext}", file_path="")
    dest = UPLOADS_DIR / f"{job.job_id}.{ext}"
    dest.write_bytes(contents)
    update_job(job.job_id, file_path=str(dest))

    get_queue().enqueue(run_separation, job.job_id)

    return JSONResponse(
        status_code=201,
        content={"job_id": job.job_id, "status": "processing", "filename": job.filename},
    )
