import io
import logging
import os
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

# The Modal function declares its own 300s timeout; leave headroom for container
# cold start and the Supabase round trip. Local CPU separation was measured at
# ~12 min for a 2-minute track.
MODAL_TIMEOUT_S = 420
LOCAL_CPU_TIMEOUT_S = 1800


def modal_enabled() -> bool:
    return bool(os.environ.get("MODAL_TOKEN_ID"))


def separation_timeout() -> int:
    return MODAL_TIMEOUT_S if modal_enabled() else LOCAL_CPU_TIMEOUT_S


def _separate_via_modal(audio_bytes: bytes) -> dict[str, bytes]:
    from modal import Function
    fn = Function.from_name("music-tool-separation", "separate_on_gpu")
    return fn.remote(audio_bytes)


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

        use_modal = modal_enabled()
        if use_modal:
            log.info("Job %s: separating on Modal GPU", job_id)
        else:
            log.warning(
                "Job %s: MODAL_TOKEN_ID not set — falling back to local CPU separation "
                "on device %s, expect ~12 min for a 2-minute track",
                job_id,
                get_demucs_device(),
            )

        t0 = time.monotonic()

        if use_modal:
            stem_mp3s = _separate_via_modal(audio_bytes)
            processing_ms = int((time.monotonic() - t0) * 1000)

            supabase_stems: dict[str, str] = {}
            for stem_name, mp3_bytes in stem_mp3s.items():
                supabase_path = f"{job_id}/{stem_name}.mp3"
                upload_file("stems", supabase_path, mp3_bytes, "audio/mpeg")
                supabase_stems[stem_name] = supabase_path
        else:
            input_file = Path(tmp_dir) / f"input.{ext}"
            input_file.write_bytes(audio_bytes)
            stems_dir = str(Path(tmp_dir) / "stems")

            local_stems = separate(str(input_file), stems_dir, device=get_demucs_device())
            processing_ms = int((time.monotonic() - t0) * 1000)

            supabase_stems = {}
            for stem_name in STEM_NAMES:
                local_wav = local_stems.get(stem_name)
                if not local_wav:
                    continue
                buf = io.BytesIO()
                AudioSegment.from_wav(local_wav).export(buf, format="mp3", bitrate="256k")
                supabase_path = f"{job_id}/{stem_name}.mp3"
                upload_file("stems", supabase_path, buf.getvalue(), "audio/mpeg")
                supabase_stems[stem_name] = supabase_path

        update_job(job_id, status="done", stems=supabase_stems, processing_ms=processing_ms)
    except Exception as exc:
        update_job(job_id, status="failed", error=str(exc))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
