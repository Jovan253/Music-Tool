from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from db import SessionLocal
from models.job import JobModel
from services.jobs import get_job
from workers.retention import exempt_job_ids, expire_old_jobs, retention_days

STEMS = {
    "vocals": "j/vocals.mp3",
    "drums": "j/drums.mp3",
    "bass": "j/bass.mp3",
    "other": "j/other.mp3",
}


def _insert(job_id: str, age_days: float, stems=STEMS, status="done"):
    with SessionLocal() as session:
        session.add(
            JobModel(
                job_id=job_id,
                status=status,
                filename=f"{job_id}.mp3",
                file_path=f"{job_id}.mp3",
                user_id="user-1",
                stems=stems,
                created_at=datetime.now(timezone.utc) - timedelta(days=age_days),
            )
        )
        session.commit()


@pytest.fixture
def storage():
    with patch("workers.retention.delete_files") as delete_files:
        yield delete_files


def test_job_past_the_window_is_expired(db, storage):
    _insert("old", age_days=30)

    result = expire_old_jobs(days=14, exempt=set())

    assert result.expired == ["old"]
    job = get_job("old")
    assert job.status == "expired"
    assert job.stems is None
    # Stems bucket and uploads bucket, in that order.
    assert [c.args[0] for c in storage.call_args_list] == ["stems", "uploads"]


def test_job_inside_the_window_is_untouched(db, storage):
    _insert("fresh", age_days=1)

    result = expire_old_jobs(days=14, exempt=set())

    assert result.expired == []
    assert get_job("fresh").status == "done"
    storage.assert_not_called()


def test_exempt_job_survives_regardless_of_age(db, storage):
    # The demo job case: without this the portfolio page loses its audio after the
    # window and the link breaks with no warning.
    _insert("demo", age_days=999)

    result = expire_old_jobs(days=14, exempt={"demo"})

    assert result.skipped_exempt == ["demo"]
    assert result.expired == []
    assert get_job("demo").status == "done"
    storage.assert_not_called()


def test_job_without_stems_is_never_selected(db, storage):
    _insert("nostems", age_days=99, stems=None, status="failed")

    result = expire_old_jobs(days=14, exempt=set())

    assert result.expired == []
    storage.assert_not_called()


def test_already_expired_job_is_not_swept_twice(db, storage):
    _insert("old", age_days=30)
    expire_old_jobs(days=14, exempt=set())
    storage.reset_mock()

    result = expire_old_jobs(days=14, exempt=set())

    assert result.expired == []
    storage.assert_not_called()


def test_storage_failure_leaves_the_record_retryable(db, storage):
    _insert("old", age_days=30)
    storage.side_effect = RuntimeError("storage down")

    result = expire_old_jobs(days=14, exempt=set())

    assert result.failed == ["old"]
    assert result.expired == []
    # Untouched, so the next sweep tries again rather than orphaning the objects.
    job = get_job("old")
    assert job.status == "done"
    assert job.stems == STEMS


def test_dry_run_reports_without_deleting(db, storage):
    _insert("old", age_days=30)

    result = expire_old_jobs(days=14, exempt=set(), dry_run=True)

    assert result.expired == ["old"]
    assert result.dry_run is True
    storage.assert_not_called()
    assert get_job("old").status == "done"


def test_boundary_is_strictly_older_than_the_cutoff(db, storage):
    _insert("just_inside", age_days=13.9)
    _insert("just_outside", age_days=14.1)

    result = expire_old_jobs(days=14, exempt=set())

    assert result.expired == ["just_outside"]


def test_retention_days_falls_back_on_a_bad_value(monkeypatch):
    monkeypatch.setenv("STEM_RETENTION_DAYS", "not-a-number")
    assert retention_days() == 14
    monkeypatch.setenv("STEM_RETENTION_DAYS", "3")
    assert retention_days() == 3
    monkeypatch.delenv("STEM_RETENTION_DAYS")
    assert retention_days() == 14


def test_exempt_ids_parse_from_a_comma_list(monkeypatch):
    # DEMO_JOB_ID is cleared explicitly: exempt_job_ids() folds it in, and a
    # developer with a demo configured in .env would otherwise fail this test
    # while CI, which has no .env, passed.
    monkeypatch.delenv("DEMO_JOB_ID", raising=False)
    monkeypatch.setenv("RETENTION_EXEMPT_JOB_IDS", " a , b ,, c ")
    assert exempt_job_ids() == {"a", "b", "c"}
    monkeypatch.setenv("RETENTION_EXEMPT_JOB_IDS", "")
    assert exempt_job_ids() == set()
