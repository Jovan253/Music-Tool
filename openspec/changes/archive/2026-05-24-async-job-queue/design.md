## Context

The API spawns a `threading.Thread(daemon=True)` for each Demucs job. This works locally but has two problems: (1) if the server restarts mid-separation the job stays `processing` forever in the DB, and (2) Demucs is CPU/memory heavy — running it in the same process as the API risks OOM kills taking down the HTTP server too. RQ separates the worker into its own process and uses Redis as a reliable broker.

## Goals / Non-Goals

**Goals:**
- Separation jobs survive API restarts
- Worker runs as a separate process (API and Demucs don't share memory)
- Stale `processing` jobs are reset on API startup and re-enqueued
- Local dev: single `docker compose up` brings up Postgres + Redis
- `RQ_REDIS_URL` env var configures the connection

**Non-Goals:**
- Job progress streaming / WebSocket updates (polling is sufficient for now)
- Multiple worker queues or priority queues
- Dead letter queue or retry logic beyond RQ defaults
- RQ Dashboard UI

## Decisions

### RQ over Celery
Celery is significantly more complex to configure (brokers, result backends, serialisers, beat scheduler). RQ is ~200 lines, uses Redis natively, and its task function is just a plain Python function — identical to the current `run_separation`. Zero learning curve, easy to swap later if needed.

### Reset stale jobs at startup, not at enqueue time
Checking for stale jobs at startup (FastAPI `lifespan`) is simpler than trying to detect them at enqueue time. The window where a job can be permanently lost is the period between the worker picking up a job and the API restarting — rare in practice, and resetting to `pending` + re-enqueuing is safe since Demucs is idempotent on the same input file.

### `queue.py` thin wrapper
A single `get_queue()` function returns a cached `rq.Queue`. This isolates the Redis connection from routes and makes it easy to swap the broker later.

### Worker entry point
RQ workers are started with `rq worker` CLI pointing at the queue name. The `run_separation` function in `workers/separation.py` needs no changes — RQ calls it directly with `job_id` as the argument.

## Risks / Trade-offs

- [Redis down] If Redis is unavailable, uploads will fail at enqueue time. → Acceptable for MVP; add retry/fallback later. Clear error surfaced to user.
- [Worker not running] If no worker process is running, jobs queue up in Redis but never process. → Surface this as `processing` status; user sees spinner. Document startup steps.
- [Re-enqueue on restart] If the API restarts and a worker is still processing the same job, it will be re-enqueued and run twice. → Demucs writes to the same output directory; second run overwrites with identical output. Acceptable for now.

## Migration Plan

1. Add `redis:7-alpine` to `docker-compose.yml`
2. Add `rq`, `redis` to `pyproject.toml` and install
3. Add `RQ_REDIS_URL` to `.env` and `.env.example`
4. Create `apps/api/queue.py`
5. Update `routes/upload.py` to use `get_queue().enqueue()`
6. Add `lifespan` startup handler in `main.py` to reset + re-enqueue stale jobs
7. Remove `threading.Thread` import and call from `upload.py`

Rollback: revert `upload.py` to `threading.Thread`, remove `queue.py` and startup handler.
