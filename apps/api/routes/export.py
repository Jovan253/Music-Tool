import io
from typing import Literal
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.jobs import get_job
from audio.mixer import mix_stems
from storage.supabase_storage import download_file

router = APIRouter()

MEDIA_TYPES = {"mp3": "audio/mpeg", "wav": "audio/wav"}


class ExportRequest(BaseModel):
    stems: dict[str, float]
    format: Literal["mp3", "wav"] = "mp3"


@router.post("/jobs/{job_id}/export")
def export_mix(job_id: str, body: ExportRequest):
    job = get_job(job_id)
    if job is None or job.status != "done" or job.stems is None:
        raise HTTPException(status_code=404, detail="Job not found or not complete")

    stem_bytes: dict[str, bytes] = {
        name: download_file("stems", path)
        for name, path in job.stems.items()
    }

    audio_bytes = mix_stems(stem_bytes, body.stems, body.format)

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type=MEDIA_TYPES[body.format],
        headers={"Content-Disposition": f'attachment; filename="mix.{body.format}"'},
    )
