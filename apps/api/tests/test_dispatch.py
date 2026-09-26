from unittest.mock import MagicMock, patch

import pytest

from workers.dispatch import MODAL_APP_NAME, MODAL_FUNCTION_NAME, dispatch_separation
from workers.separation import modal_enabled


def test_modal_enabled_follows_token(monkeypatch):
    monkeypatch.delenv("MODAL_TOKEN_ID", raising=False)
    assert modal_enabled() is False
    monkeypatch.setenv("MODAL_TOKEN_ID", "ak-something")
    assert modal_enabled() is True


def test_dispatch_spawns_on_modal_when_configured(monkeypatch):
    monkeypatch.setenv("MODAL_TOKEN_ID", "ak-something")
    background = MagicMock()

    with patch("modal.Function.from_name") as from_name:
        dispatch_separation("job-1", background)

    from_name.assert_called_once_with(MODAL_APP_NAME, MODAL_FUNCTION_NAME)
    from_name.return_value.spawn.assert_called_once_with("job-1")
    # Modal owns the work; nothing should be queued on the web process.
    background.add_task.assert_not_called()


def test_dispatch_falls_back_to_background_task(monkeypatch):
    monkeypatch.delenv("MODAL_TOKEN_ID", raising=False)
    background = MagicMock()

    with patch("modal.Function.from_name") as from_name:
        dispatch_separation("job-2", background)

    from_name.assert_not_called()
    background.add_task.assert_called_once()
    args = background.add_task.call_args[0]
    assert args[1] == "job-2"


def test_function_name_matches_the_deployed_modal_function():
    # workers/dispatch.py resolves the function by name at runtime, so a rename in
    # modal_separation.py that misses this constant fails only once a job runs.
    import modal_separation

    assert modal_separation.app.name == MODAL_APP_NAME
    assert hasattr(modal_separation, MODAL_FUNCTION_NAME)


@pytest.mark.parametrize("attr", ["SEPARATION_TIMEOUT_S"])
def test_separation_timeout_is_generous_enough_for_a_cold_gpu(attr):
    import modal_separation

    # A cold container pulls Demucs weights before doing any work, so the timeout
    # has to clear far more than the ~25s of actual T4 separation.
    assert getattr(modal_separation, attr) >= 600
