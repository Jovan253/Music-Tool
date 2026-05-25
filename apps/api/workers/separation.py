import io
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


def _separate_via_modal(audio_bytes: bytes) -> dict[str, bytes]:
    from modal import Function
    fn = Function.lookup("music-tool-separation", "separate_on_gpu")
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

        use_modal = bool(os.environ.get("MODAL_TOKEN_ID"))

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
