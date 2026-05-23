from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal
import uuid

JobStatus = Literal["pending", "processing", "done", "failed"]


@dataclass
class JobRecord:
    job_id: str
    status: JobStatus
    filename: str
    file_path: str
    created_at: str


_store: dict[str, JobRecord] = {}


def create_job(filename: str, file_path: str) -> JobRecord:
    job = JobRecord(
        job_id=str(uuid.uuid4()),
        status="pending",
        filename=filename,
        file_path=file_path,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    _store[job.job_id] = job
    return job


def get_job(job_id: str) -> JobRecord | None:
    return _store.get(job_id)
