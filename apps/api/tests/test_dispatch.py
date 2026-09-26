from unittest.mock import MagicMock, patch

from workers.dispatch import (
    MODAL_APP_NAME,
    MODAL_FUNCTION_NAME,
    dispatch_separation,
    modal_enabled,
)


def test_modal_enabled_locally_follows_the_token(monkeypatch):
    with patch("modal.is_local", return_value=True):
        monkeypatch.delenv("MODAL_TOKEN_ID", raising=False)
        assert modal_enabled() is False
        monkeypatch.setenv("MODAL_TOKEN_ID", "ak-something")
        assert modal_enabled() is True


def test_modal_enabled_inside_a_modal_container_ignores_the_token(monkeypatch):
    # The regression this guards: a Modal container has no MODAL_TOKEN_* vars
    # because it is authenticated ambiently. Testing for the token there made
    # dispatch run separation in-process inside an image with no torch, so every
    # upload failed with ModuleNotFoundError.
    monkeypatch.delenv("MODAL_TOKEN_ID", raising=False)
    with patch("modal.is_local", return_value=False):
        assert modal_enabled() is True


def test_dispatch_spawns_on_modal_when_enabled(monkeypatch):
    monkeypatch.setenv("MODAL_TOKEN_ID", "ak-something")
    background = MagicMock()

    with patch("modal.is_local", return_value=True), patch(
        "modal.Function.from_name"
    ) as from_name:
        dispatch_separation("job-1", background)

    from_name.assert_called_once_with(MODAL_APP_NAME, MODAL_FUNCTION_NAME)
    from_name.return_value.spawn.assert_called_once_with("job-1")
    background.add_task.assert_not_called()


def test_dispatch_falls_back_to_background_task_when_deps_present(monkeypatch):
    monkeypatch.delenv("MODAL_TOKEN_ID", raising=False)
    background = MagicMock()

    with patch("modal.is_local", return_value=True), patch(
        "workers.dispatch._local_separation_available", return_value=True
    ), patch("modal.Function.from_name") as from_name:
        dispatch_separation("job-2", background)

    from_name.assert_not_called()
    background.add_task.assert_called_once()
    assert background.add_task.call_args[0][1] == "job-2"


def test_dispatch_fails_the_job_when_local_deps_are_missing(monkeypatch):
    monkeypatch.delenv("MODAL_TOKEN_ID", raising=False)
    background = MagicMock()

    with patch("modal.is_local", return_value=True), patch(
        "workers.dispatch._local_separation_available", return_value=False
    ), patch("workers.dispatch.update_job") as update_job:
        dispatch_separation("job-3", background)

    # Queue nothing that is guaranteed to crash; record an actionable error.
    background.add_task.assert_not_called()
    update_job.assert_called_once()
    assert update_job.call_args.kwargs["status"] == "failed"
    assert "local-separation" in update_job.call_args.kwargs["error"]


def test_function_name_matches_the_deployed_modal_function():
    # dispatch resolves the function by name at runtime, so a rename in
    # modal_separation.py that misses this constant fails only once a job runs.
    import modal_separation

    assert modal_separation.app.name == MODAL_APP_NAME
    assert hasattr(modal_separation, MODAL_FUNCTION_NAME)


def test_separation_timeout_is_generous_enough_for_a_cold_gpu():
    import modal_separation

    # A cold container pulls Demucs weights before doing any work, so the timeout
    # has to clear far more than the ~25s of actual T4 separation.
    assert modal_separation.SEPARATION_TIMEOUT_S >= 600
