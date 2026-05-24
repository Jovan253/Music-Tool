from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal
import uuid

from db import SessionLocal
from models.job import JobModel

JobStatus = Literal["pending", "processing", "done", "failed"]


@dataclass
class JobRecord:
    job_id: str
    status: JobStatus
    filename: str
    file_path: str
    created_at: str
    stems: dict[str, str] | None = field(default=None)
    error: str | None = field(default=None)


def _to_record(row: JobModel) -> JobRecord:
    return JobRecord(
        job_id=row.job_id,
        status=row.status,
        filename=row.filename,
        file_path=row.file_path,
        created_at=row.created_at.isoformat() if isinstance(row.created_at, datetime) else str(row.created_at),
        stems=row.stems,
        error=row.error,
    )


def create_job(filename: str, file_path: str) -> JobRecord:
    row = JobModel(
        job_id=str(uuid.uuid4()),
        status="pending",
        filename=filename,
        file_path=file_path,
        created_at=datetime.now(timezone.utc),
    )
    with SessionLocal() as db:
        db.add(row)
        db.commit()
        db.refresh(row)
        return _to_record(row)


def get_job(job_id: str) -> JobRecord | None:
    with SessionLocal() as db:
        row = db.get(JobModel, job_id)
        return _to_record(row) if row else None


def update_job(
    job_id: str,
    *,
    status: JobStatus | None = None,
    file_path: str | None = None,
    stems: dict[str, str] | None = None,
    error: str | None = None,
) -> JobRecord:
    with SessionLocal() as db:
        row = db.get(JobModel, job_id)
        if row is None:
            raise ValueError(f"Job {job_id!r} not found")
        if status is not None:
            row.status = status
        if file_path is not None:
            row.file_path = file_path
        if stems is not None:
            row.stems = stems
        if error is not None:
            row.error = error
        db.commit()
        db.refresh(row)
        return _to_record(row)
