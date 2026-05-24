## 1. Infrastructure & Dependencies

- [x] 1.1 Add `redis:7-alpine` service to `docker-compose.yml` (port 6379, named `redis`)
- [x] 1.2 Add `rq>=1.16` and `redis>=5.0` to `apps/api/pyproject.toml` and install into venv
- [x] 1.3 Add `RQ_REDIS_URL=redis://localhost:6379/0` to `apps/api/.env` and `.env.example`

## 2. Queue Module

- [x] 2.1 Create `apps/api/queue.py` — `get_queue()` returns a cached `rq.Queue("default", connection=Redis.from_url(RQ_REDIS_URL))`; raises `503` HTTPException if Redis is unreachable

## 3. Wire Upload Route

- [x] 3.1 Update `apps/api/routes/upload.py` — replace `threading.Thread(...).start()` with `get_queue().enqueue(run_separation, job.job_id)`; catch `redis.exceptions.ConnectionError` and raise `HTTPException(503)`
- [x] 3.2 Remove `import threading` from `upload.py`

## 4. Startup Recovery

- [x] 4.1 Add a `lifespan` async context manager to `apps/api/main.py` — on startup, query all jobs with `status="processing"`, call `update_job(job_id, status="pending")` for each, then re-enqueue them via `get_queue().enqueue(run_separation, job_id)`

## 5. Verification

- [x] 5.1 Run `docker compose up -d` and confirm both `db` and `redis` containers are running
- [x] 5.2 Start the API (`uvicorn main:app`) and the RQ worker (`rq worker --with-scheduler`) in separate terminals
- [x] 5.3 Upload a file via the UI — confirm job moves from `pending` → `processing` → `done` and stems load in the mixer
- [x] 5.4 While a job is `processing`, kill and restart the API — confirm the job is re-enqueued and eventually completes
