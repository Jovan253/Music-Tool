from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from audio.demucs import separate
from services.jobs import get_job, update_job


def run_separation(job_id: str) -> None:
    job = get_job(job_id)
    if job is None:
        raise ValueError(f"Job {job_id!r} not found")

    update_job(job_id, status="processing")

    try:
        input_path = job.file_path
        stems_dir = str(Path(input_path).parent / job_id / "stems")
        stems = separate(input_path, stems_dir)
        update_job(job_id, status="done", stems=stems)
    except Exception as exc:
        update_job(job_id, status="failed", error=str(exc))
