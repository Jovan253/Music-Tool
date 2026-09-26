import logging
import os

import modal
from fastapi import BackgroundTasks

from services.jobs import update_job
from workers.separation import run_separation

log = logging.getLogger(__name__)

MODAL_APP_NAME = "music-tool-separation"
MODAL_FUNCTION_NAME = "separate_job"

_LOCAL_DEPS_MISSING = (
    "Separation cannot run in-process: torch and demucs are not installed. "
    "Either set MODAL_TOKEN_ID to dispatch to Modal's GPU, or install the extra "
    'with: pip install -e ".[local-separation]"'
)


def modal_enabled() -> bool:
    # Inside a Modal container there are no MODAL_TOKEN_* vars — the container is
    # already authenticated ambiently — so testing for the token would wrongly
    # conclude Modal is unavailable and run separation in an image with no torch.
    if not modal.is_local():
        return True
    return bool(os.environ.get("MODAL_TOKEN_ID"))


def _local_separation_available() -> bool:
    from importlib.util import find_spec

    return find_spec("torch") is not None and find_spec("demucs") is not None


def dispatch_separation(job_id: str, background_tasks: BackgroundTasks) -> None:
    if modal_enabled():
        modal.Function.from_name(MODAL_APP_NAME, MODAL_FUNCTION_NAME).spawn(job_id)
        log.info("Job %s: spawned on Modal", job_id)
        return

    if not _local_separation_available():
        log.error("Job %s: %s", job_id, _LOCAL_DEPS_MISSING)
        update_job(job_id, status="failed", error=_LOCAL_DEPS_MISSING)
        return

    # In-process is the development path only. It keeps the endpoint responsive
    # without Redis, but a CPU separation takes ~12 minutes.
    log.warning(
        "Job %s: MODAL_TOKEN_ID not set — running separation in-process", job_id
    )
    background_tasks.add_task(run_separation, job_id)
