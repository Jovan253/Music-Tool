import io
import logging
import shutil
import tempfile
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from pydub import AudioSegment
from audio.demucs import separate, STEM_NAMES, get_demucs_device
from services.jobs import get_job, update_job
from storage.supabase_storage import download_file, upload_file

log = logging.getLogger(__name__)


def run_separation(job_id: str) -> None:
    job = get_job(job_id)
    if job is None:
        raise ValueError(f"Job {job_id!r} not found")

    update_job(job_id, status="processing")

    tmp_dir = tempfile.mkdtemp()
    try:
        upload_path = job.file_path
        ext = upload_path.rsplit(".", 1)[-1] if "." in upload_path else "wav"
        audio_bytes = download_file("uploads", upload_path)

        device = get_demucs_device()
        log.info("Job %s: separating on device %s", job_id, device)

        t0 = time.monotonic()
        input_file = Path(tmp_dir) / f"input.{ext}"
        input_file.write_bytes(audio_bytes)
        local_stems = separate(str(input_file), str(Path(tmp_dir) / "stems"), device=device)
        processing_ms = int((time.monotonic() - t0) * 1000)

        stem_paths: dict[str, str] = {}
        for stem_name in STEM_NAMES:
            local_wav = local_stems.get(stem_name)
            if not local_wav:
                continue
            buf = io.BytesIO()
            AudioSegment.from_wav(local_wav).export(buf, format="mp3", bitrate="256k")
            remote_path = f"{job_id}/{stem_name}.mp3"
            upload_file("stems", remote_path, buf.getvalue(), "audio/mpeg")
            stem_paths[stem_name] = remote_path

        update_job(job_id, status="done", stems=stem_paths, processing_ms=processing_ms)
    except Exception as exc:
        log.exception("Job %s failed", job_id)
        update_job(job_id, status="failed", error=str(exc))
        # Re-raised so Modal counts the attempt and applies its retry policy.
        # Swallowing here would make a failed job look successful to Modal.
        raise
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
