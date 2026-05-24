## Why

The current daemon thread worker is fire-and-forget — if the server restarts mid-separation the job stays stuck in `processing` forever with no way to recover it. An RQ queue backed by Redis gives us reliable task dispatch, worker restarts without job loss, and a clean separation between the API process and the CPU-heavy Demucs process.

## What Changes

- Add Redis to `docker-compose.yml` as a local dev service
- Add `rq` and `redis` to API dependencies
- Replace `threading.Thread` in `upload.py` with `rq.Queue.enqueue()`
- Move `run_separation` to a standalone worker module invoked by `rq worker`
- On API startup, reset any jobs stuck in `processing` back to `pending` and re-enqueue them
- Add `RQ_REDIS_URL` env var (defaults to `redis://localhost:6379/0`)

## Capabilities

### New Capabilities
- `job-queue`: Separation jobs are enqueued into Redis via RQ and processed by a dedicated worker; jobs survive API restarts and can be retried

### Modified Capabilities

## Impact

- `docker-compose.yml` — add `redis:7-alpine` service
- `apps/api/pyproject.toml` — add `rq`, `redis`
- `apps/api/queue.py` (new) — `get_queue()` returns an `rq.Queue` connected to Redis
- `apps/api/routes/upload.py` — replace `threading.Thread` with `queue.enqueue(run_separation, job_id)`
- `apps/api/workers/separation.py` — no logic changes; works as-is as an RQ task function
- `apps/api/main.py` — startup event resets stale `processing` jobs and re-enqueues them
- `apps/api/.env` / `.env.example` — add `RQ_REDIS_URL`
