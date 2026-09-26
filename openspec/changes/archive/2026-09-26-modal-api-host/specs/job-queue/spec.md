## MODIFIED Requirements

### Requirement: Separation jobs are dispatched asynchronously
The system SHALL dispatch separation work asynchronously so that `POST /upload` returns without waiting for separation. When `MODAL_TOKEN_ID` is set, dispatch SHALL spawn the Modal separation function and return immediately. When it is not set, dispatch SHALL run the local separation path so that development requires neither Modal credentials nor Redis.

#### Scenario: Upload dispatches to Modal
- **WHEN** a client POSTs a valid audio file and `MODAL_TOKEN_ID` is set
- **THEN** a job record is created, the Modal separation function is spawned, and the response returns without waiting for separation to finish

#### Scenario: Upload falls back to local execution
- **WHEN** a client POSTs a valid audio file and `MODAL_TOKEN_ID` is not set
- **THEN** separation runs via the local path and the job reaches a terminal status with the same record shape

#### Scenario: Client polls for completion
- **WHEN** a client polls `GET /jobs/{job_id}` after dispatch
- **THEN** it observes `processing` and then `done` or `failed`, read from the database, with no knowledge of which executor ran the job

## REMOVED Requirements

### Requirement: Separation jobs are dispatched via RQ
**Reason:** Redis and RQ are removed. A Modal function call is already a durable, addressable, retried unit of work, so the queue tier no longer earns its cost — it was four always-on services' worth of infrastructure to express "run this later".

**Migration:** `POST /upload` calls `.spawn()` on the Modal function instead of `get_queue().enqueue()`. `apps/api/job_queue.py` is deleted, the `rq` and `redis` dependencies are dropped, the separate worker process is retired, and the Redis service is removed from `docker-compose.yml`. The `503 Service Unavailable` response for an unreachable Redis disappears with it; Modal dispatch failures surface as a failed job rather than a rejected upload.

### Requirement: Stale processing jobs are reset on startup
**Reason:** The startup sweep assumed a long-lived web process. Under scale-to-zero the API starts and stops constantly, so the sweep would fire on every cold start and re-run jobs that are legitimately still in flight.

**Migration:** Modal function retries cover the transient failures the sweep existed to recover from. A job whose retries are exhausted terminates as `failed` with an error message, which is visible to the client through the existing polling contract.
