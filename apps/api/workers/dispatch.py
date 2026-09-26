import logging

from fastapi import BackgroundTasks

from workers.separation import modal_enabled, run_separation

log = logging.getLogger(__name__)

MODAL_APP_NAME = "music-tool-separation"
MODAL_FUNCTION_NAME = "separate_job"


def dispatch_separation(job_id: str, background_tasks: BackgroundTasks) -> None:
    if modal_enabled():
        from modal import Function

        Function.from_name(MODAL_APP_NAME, MODAL_FUNCTION_NAME).spawn(job_id)
        log.info("Job %s: spawned on Modal", job_id)
        return

    # In-process is the development path only. It keeps the endpoint responsive
    # without needing Redis, but a CPU separation takes ~12 minutes.
    log.warning(
        "Job %s: MODAL_TOKEN_ID not set — running separation in-process", job_id
    )
    background_tasks.add_task(run_separation, job_id)
