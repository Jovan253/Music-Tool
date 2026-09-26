# Spec: job-queue

> There is no longer a queue process. Redis and RQ were removed by the
> `modal-api-host` change: a Modal function call is already durable, addressable
> and retried, so the queue tier no longer earned four always-on services. The
> capability name is kept for continuity; it now describes dispatch.

## Requirement: Separation jobs are dispatched asynchronously
The system SHALL dispatch separation work asynchronously so that `POST /upload` returns without waiting for separation. Dispatch SHALL spawn the Modal separation function when Modal is available, and SHALL otherwise run the local separation path in-process so that development requires neither Modal credentials nor Redis.

Modal availability SHALL be determined by whether the process is running inside a Modal container, falling back to the presence of `MODAL_TOKEN_ID` when it is not. A Modal container carries no `MODAL_TOKEN_*` variables because it is authenticated ambiently, so the token alone SHALL NOT be treated as the signal.

### Scenario: Upload dispatches to Modal
- **WHEN** a client POSTs a valid audio file and Modal is available
- **THEN** a job record is created, the Modal separation function is spawned, and the response returns without waiting for separation to finish

### Scenario: Dispatch from inside a Modal container
- **WHEN** the deployed API dispatches a job and no `MODAL_TOKEN_ID` is present in its environment
- **THEN** it still spawns remotely, using the container's ambient credentials

### Scenario: Upload falls back to local execution
- **WHEN** a client POSTs a valid audio file, Modal is unavailable, and torch and demucs are installed
- **THEN** separation runs in-process as a background task and the job reaches a terminal status with the same record shape

### Scenario: Local execution without separation dependencies
- **WHEN** Modal is unavailable and torch or demucs is not installed
- **THEN** the job is marked `failed` with an error naming the `local-separation` extra, and no work is queued that cannot succeed

### Scenario: Client polls for completion
- **WHEN** a client polls `GET /jobs/{job_id}` after dispatch
- **THEN** it observes `processing` and then `done` or `failed`, read from the database, with no knowledge of which executor ran the job

## Requirement: Failed jobs are recovered by retries, not by a startup sweep
The system SHALL rely on the Modal function's retry policy to recover transient separation failures. It SHALL NOT sweep `processing` jobs at API startup, because under scale-to-zero hosting containers start and stop constantly and such a sweep would re-run jobs that are legitimately in flight.

### Scenario: Transient failure is retried
- **WHEN** the separation function fails with a transient error
- **THEN** Modal retries it, and the job reaches `done` without any operator action

### Scenario: Retries exhausted
- **WHEN** the separation function fails repeatedly and its retry budget is exhausted
- **THEN** the job ends as `failed` with an error rather than remaining `processing` indefinitely

### Scenario: API restart has no effect on in-flight jobs
- **WHEN** the API starts or scales to zero while a job is separating
- **THEN** the job is untouched and continues on Modal
