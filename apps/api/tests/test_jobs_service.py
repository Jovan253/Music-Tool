from services.jobs import create_job, get_job, update_job

STALE = "No module named 'numpy'"


def _new_job():
    return create_job(filename="track.mp3", file_path="track.mp3", user_id="user-1")


def test_success_after_a_failure_clears_the_stale_error(db):
    # This actually happened: a job failed on a missing dependency, the dependency
    # was fixed, the retry succeeded — and the row still carried the old error text
    # next to status "done", which the UI would happily render.
    job = _new_job()
    update_job(job.job_id, status="failed", error=STALE)
    assert get_job(job.job_id).error == STALE

    update_job(job.job_id, status="done", stems={"vocals": "v.mp3"}, processing_ms=1234)

    fresh = get_job(job.job_id)
    assert fresh.status == "done"
    assert fresh.error is None
    assert fresh.processing_ms == 1234


def test_retrying_clears_the_error_too(db):
    job = _new_job()
    update_job(job.job_id, status="failed", error=STALE)
    update_job(job.job_id, status="processing")
    assert get_job(job.job_id).error is None


def test_a_failure_keeps_its_error(db):
    job = _new_job()
    update_job(job.job_id, status="failed", error=STALE)
    assert get_job(job.job_id).error == STALE


def test_jobs_are_scoped_to_their_user(db):
    job = _new_job()
    assert get_job(job.job_id, user_id="user-1") is not None
    assert get_job(job.job_id, user_id="someone-else") is None


def test_unknown_job_is_none(db):
    assert get_job("nope") is None
