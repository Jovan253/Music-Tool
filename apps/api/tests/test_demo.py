from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from db import SessionLocal
from models.job import JobModel
from workers.retention import exempt_job_ids

DEMO_ID = "demo-job-id"
OTHER_ID = "someone-elses-job"
STEMS = {"vocals": "d/vocals.mp3", "drums": "d/drums.mp3", "bass": "d/bass.mp3", "other": "d/other.mp3"}


def _insert(job_id: str, status="done", stems=STEMS, filename="raw-recording-2026.mp3"):
    with SessionLocal() as session:
        session.add(
            JobModel(
                job_id=job_id,
                status=status,
                filename=filename,
                file_path=f"{job_id}.mp3",
                user_id="someone",
                stems=stems,
                processing_ms=6700,
                created_at=datetime.now(timezone.utc),
            )
        )
        session.commit()


@pytest.fixture
def demo_configured(monkeypatch):
    monkeypatch.setenv("DEMO_JOB_ID", DEMO_ID)
    monkeypatch.delenv("DEMO_TRACK_TITLE", raising=False)


def test_demo_job_is_served_without_a_token(client, db, demo_configured):
    _insert(DEMO_ID)
    response = client.get("/demo/job")
    assert response.status_code == 200
    body = response.json()
    assert body["stems"] == ["bass", "drums", "other", "vocals"]
    assert body["processing_ms"] == 6700


def test_demo_title_can_override_the_raw_filename(client, db, demo_configured, monkeypatch):
    _insert(DEMO_ID, filename="raw-recording-2026.mp3")
    assert client.get("/demo/job").json()["title"] == "raw-recording-2026.mp3"

    monkeypatch.setenv("DEMO_TRACK_TITLE", "Mardy Bum")
    assert client.get("/demo/job").json()["title"] == "Mardy Bum"


def test_demo_stem_returns_a_signed_url(client, db, demo_configured):
    _insert(DEMO_ID)
    with patch("routes.demo.create_signed_url", return_value="https://signed.example/vocals") as signer:
        response = client.get("/demo/stems/vocals")
    assert response.status_code == 200
    assert response.json() == {"url": "https://signed.example/vocals"}
    assert signer.call_args[0][1] == STEMS["vocals"]


def test_demo_routes_404_when_no_demo_is_configured(client, db, monkeypatch):
    monkeypatch.delenv("DEMO_JOB_ID", raising=False)
    assert client.get("/demo/job").status_code == 404
    assert client.get("/demo/stems/vocals").status_code == 404


def test_demo_cannot_be_pointed_at_another_job(client, db, demo_configured):
    # The whole safety property: these routes are unauthenticated, so the job id
    # must come from configuration only. There is no request parameter that can
    # reach another user's stems, and a traversal attempt is just an unknown stem.
    _insert(DEMO_ID)
    _insert(OTHER_ID)
    assert client.get(f"/demo/stems/../../{OTHER_ID}/vocals").status_code == 404
    assert client.get("/demo/stems/vocals.mp3").status_code == 404
    assert client.get("/demo/stems/secret").status_code == 404


def test_unconfigured_demo_does_not_expose_an_arbitrary_job(client, db, monkeypatch):
    monkeypatch.setenv("DEMO_JOB_ID", "does-not-exist")
    _insert(OTHER_ID)
    assert client.get("/demo/job").status_code == 404


def test_demo_unavailable_until_separation_finished(client, db, demo_configured):
    _insert(DEMO_ID, status="processing", stems=None)
    assert client.get("/demo/job").status_code == 404


def test_expired_demo_is_not_served(client, db, demo_configured):
    _insert(DEMO_ID, status="expired", stems=None)
    assert client.get("/demo/job").status_code == 404


def test_demo_job_is_exempt_from_retention_without_being_listed(monkeypatch):
    # Exempt by construction: listing it in RETENTION_EXEMPT_JOB_IDS as well would
    # be easy to forget, and forgetting deletes the public demo's audio.
    monkeypatch.delenv("RETENTION_EXEMPT_JOB_IDS", raising=False)
    monkeypatch.setenv("DEMO_JOB_ID", DEMO_ID)
    assert DEMO_ID in exempt_job_ids()

    monkeypatch.setenv("RETENTION_EXEMPT_JOB_IDS", "another-id")
    assert exempt_job_ids() == {DEMO_ID, "another-id"}
