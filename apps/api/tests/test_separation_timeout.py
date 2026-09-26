from workers.separation import (
    LOCAL_CPU_TIMEOUT_S,
    MODAL_TIMEOUT_S,
    modal_enabled,
    separation_timeout,
)


def test_modal_enabled_follows_token(monkeypatch):
    monkeypatch.delenv("MODAL_TOKEN_ID", raising=False)
    assert modal_enabled() is False
    monkeypatch.setenv("MODAL_TOKEN_ID", "ak-something")
    assert modal_enabled() is True


def test_timeout_matches_active_path(monkeypatch):
    monkeypatch.setenv("MODAL_TOKEN_ID", "ak-something")
    assert separation_timeout() == MODAL_TIMEOUT_S

    monkeypatch.delenv("MODAL_TOKEN_ID", raising=False)
    assert separation_timeout() == LOCAL_CPU_TIMEOUT_S


def test_local_timeout_exceeds_measured_cpu_duration():
    # Local CPU separation was measured at ~12 min for a 2-minute track; the
    # timeout has to clear that or every local job dies mid-run.
    assert LOCAL_CPU_TIMEOUT_S > 12 * 60


def test_modal_timeout_exceeds_modal_function_timeout():
    # audio/modal_separation.py declares timeout=300 on the Modal function, so
    # the RQ timeout wrapping it must be strictly larger or RQ kills the job
    # while Modal is still legitimately working.
    assert MODAL_TIMEOUT_S > 300
