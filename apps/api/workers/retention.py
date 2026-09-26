import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from services.jobs import JobRecord, expire_job, get_jobs_with_stems
from storage.supabase_storage import delete_files

log = logging.getLogger(__name__)

DEFAULT_RETENTION_DAYS = 14


@dataclass
class SweepResult:
    expired: list[str] = field(default_factory=list)
    skipped_exempt: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    dry_run: bool = False

    def summary(self) -> str:
        verb = "would expire" if self.dry_run else "expired"
        return (
            f"{verb} {len(self.expired)}, "
            f"exempt {len(self.skipped_exempt)}, "
            f"failed {len(self.failed)}"
        )


def retention_days() -> int:
    raw = os.environ.get("STEM_RETENTION_DAYS")
    if not raw:
        return DEFAULT_RETENTION_DAYS
    try:
        return int(raw)
    except ValueError:
        log.warning("STEM_RETENTION_DAYS=%r is not an integer; using default", raw)
        return DEFAULT_RETENTION_DAYS


def exempt_job_ids() -> set[str]:
    raw = os.environ.get("RETENTION_EXEMPT_JOB_IDS", "")
    return {part.strip() for part in raw.split(",") if part.strip()}


def _created_at_utc(job: JobRecord) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(job.created_at)
    except (TypeError, ValueError):
        log.warning("Job %s: unparseable created_at %r; skipping", job.job_id, job.created_at)
        return None
    # SQLite hands back naive datetimes even for a timezone-aware column, so
    # normalise before comparing or the subtraction raises.
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _paths_for(job: JobRecord) -> tuple[list[str], list[str]]:
    stem_paths = list((job.stems or {}).values())
    upload_paths = [job.file_path] if job.file_path else []
    return upload_paths, stem_paths


def expire_old_jobs(
    days: int | None = None,
    exempt: set[str] | None = None,
    dry_run: bool = False,
) -> SweepResult:
    window = retention_days() if days is None else days
    exempt = exempt_job_ids() if exempt is None else exempt
    cutoff = datetime.now(timezone.utc) - timedelta(days=window)

    result = SweepResult(dry_run=dry_run)
    log.info(
        "Retention sweep: window=%sd cutoff=%s dry_run=%s exempt=%s",
        window,
        cutoff.isoformat(),
        dry_run,
        sorted(exempt) or "none",
    )

    for job in get_jobs_with_stems():
        created = _created_at_utc(job)
        if created is None or created >= cutoff:
            continue

        if job.job_id in exempt:
            result.skipped_exempt.append(job.job_id)
            continue

        if dry_run:
            result.expired.append(job.job_id)
            continue

        uploads, stems = _paths_for(job)
        try:
            # Storage first, deliberately. Marking the row expired before deleting
            # would orphan the objects if deletion then failed: nothing would point
            # at them and no later sweep could find them.
            delete_files("stems", stems)
            delete_files("uploads", uploads)
            expire_job(job.job_id)
        except Exception:
            # Leave the record untouched so the next sweep retries it.
            log.exception("Job %s: retention failed", job.job_id)
            result.failed.append(job.job_id)
            continue

        result.expired.append(job.job_id)
        log.info("Job %s: expired, %d objects removed", job.job_id, len(stems) + len(uploads))

    log.info("Retention sweep complete: %s", result.summary())
    return result
