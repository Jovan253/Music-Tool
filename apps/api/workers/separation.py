import shutil
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from audio.demucs import separate, STEM_NAMES
from services.jobs import get_job, update_job
from storage.supabase_storage import download_file, upload_file


def run_separation(job_id: str) -> None:
    job = get_job(job_id)
    if job is None:
        raise ValueError(f"Job {job_id!r} not found")

    update_job(job_id, status="processing")

    tmp_dir = tempfile.mkdtemp()
    try:
        # Download upload from Supabase to a temp file
        upload_path = job.file_path  # e.g. "abc123.mp3"
        ext = upload_path.rsplit(".", 1)[-1] if "." in upload_path else "wav"
        audio_bytes = download_file("uploads", upload_path)
        input_file = Path(tmp_dir) / f"input.{ext}"
        input_file.write_bytes(audio_bytes)

        stems_dir = str(Path(tmp_dir) / "stems")
        local_stems = separate(str(input_file), stems_dir)

        # Upload each stem to Supabase and collect paths
        supabase_stems: dict[str, str] = {}
        for stem_name in STEM_NAMES:
            local_path = local_stems.get(stem_name)
            if not local_path:
                continue
            stem_bytes = Path(local_path).read_bytes()
            supabase_path = f"{job_id}/{stem_name}.wav"
            upload_file("stems", supabase_path, stem_bytes, "audio/wav")
            supabase_stems[stem_name] = supabase_path

        update_job(job_id, status="done", stems=supabase_stems)
    except Exception as exc:
        update_job(job_id, status="failed", error=str(exc))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
