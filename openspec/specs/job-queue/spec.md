# Spec: job-queue

## Requirement: Separation jobs are dispatched via RQ
The system SHALL enqueue separation jobs into an RQ queue backed by Redis instead of spawning a thread. A dedicated worker process SHALL dequeue and execute each job.

### Scenario: Upload enqueues a job
- **WHEN** a client POSTs a valid audio file to `POST /upload`
- **THEN** a job record is created with status `pending` and a separation task is enqueued in Redis

### Scenario: Worker processes the job
- **WHEN** an RQ worker is running and a job is enqueued
- **THEN** the worker picks up the job, runs Demucs separation, and updates the job status to `done` or `failed`

### Scenario: Redis unavailable returns 503
- **WHEN** a client uploads a file and Redis is unreachable
- **THEN** the server responds `503 Service Unavailable`

## Requirement: Stale processing jobs are reset on startup
The system SHALL detect jobs with status `processing` at API startup and reset them to `pending`, then re-enqueue them.

### Scenario: Stale job is recovered after restart
- **WHEN** a job is in `processing` state and the API server restarts
- **THEN** the job status is reset to `pending` and it is re-enqueued for processing

### Scenario: No stale jobs on clean startup
- **WHEN** the API starts and no jobs are in `processing` state
- **THEN** startup completes normally with no side effects

## Requirement: RQ_REDIS_URL configures the broker connection
The system SHALL read `RQ_REDIS_URL` from the environment to connect to Redis. It SHALL default to `redis://localhost:6379/0` if not set.

### Scenario: Custom Redis URL is used
- **WHEN** `RQ_REDIS_URL` is set to a non-default value
- **THEN** the RQ queue connects to that Redis instance
