## Why

Railway is the only part of this stack that costs money, and it is hosting four always-on services for an app with near-zero traffic. Railway's Free plan grants $1/month of credit — nowhere near enough for web + worker + Postgres + Redis running continuously — and Hobby is $5/month with a usage credit that four services will likely exceed.

Modal already runs the GPU separation step and its Starter plan is free with $30/month of compute credits (~50 T4-hours, i.e. thousands of songs at ~25s each). Modal can also host a full ASGI app, so the same platform can run the API with scale-to-zero billing.

Moving the API to Modal also removes the reason Redis and RQ exist. A Modal function call is itself a queued, durable, retried unit of work with an addressable id — which is what the RQ queue was providing. Deleting Redis, the RQ queue module, and the separate worker service removes an entire tier of moving parts rather than relocating it.

## What Changes

- Add `apps/api/modal_app.py` — a Modal app that serves the existing FastAPI application via `@modal.asgi_app()`, plus a one-shot `migrate()` function for Alembic
- Move the body of `run_separation` into a Modal GPU function that owns the whole job: download the upload, separate, transcode, upload stems, and write the terminal job status
- `POST /upload` dispatches with `.spawn()` instead of `get_queue().enqueue()`
- Delete `apps/api/job_queue.py`, the RQ/Redis dependency, and the separate worker process
- Delete the startup stale-job recovery in `main.py` in favour of Modal function retries
- Delete `apps/api/railway.toml`, `apps/api/Procfile`, and `apps/api/start.sh`
- Secrets move from a `.env` file to a Modal Secret; `DEMUCS_DEVICE`, `REDIS_URL` and `RQ_REDIS_URL` leave the production variable set
- Keep the local-CPU path for development so the app runs with no Modal credentials and no Redis container

Deliberately unchanged: the `GET /jobs/{job_id}` polling contract, the signed-URL stem flow, and every frontend file. Job state continues to live in Postgres, so the client cannot tell which executor ran the job.

## Capabilities

### New Capabilities

- `modal-api-host`: the Modal app definition that serves the FastAPI application, the image spec, secret wiring, and the migration entrypoint

### Modified Capabilities

- `job-queue`: dispatch moves from RQ/Redis to Modal `.spawn()`. The requirement that a dedicated worker process dequeues jobs is removed, as is the Redis-unavailable 503 path and the startup stale-job sweep.
- `stem-separation`: `run_separation` is no longer the orchestrator on the server side. The Modal function owns storage I/O and the terminal status write; the local function remains as the development fallback.

### Removed Capabilities

- `railway-config`: Railway is retired. `railway.toml`, `Procfile`, and `start.sh` are deleted along with their requirements.

## Impact

- `apps/api/modal_app.py` — new
- `apps/api/audio/modal_separation.py` — gains storage and database access; returns nothing instead of stem bytes
- `apps/api/workers/separation.py` — reduced to the local development path
- `apps/api/routes/upload.py` — `.spawn()` instead of `enqueue()`
- `apps/api/main.py` — lifespan stale-job sweep removed
- `apps/api/job_queue.py` — deleted
- `apps/api/pyproject.toml` — `rq` and `redis` removed
- `apps/api/railway.toml`, `apps/api/Procfile`, `apps/api/start.sh` — deleted
- `docker-compose.yml` — Redis service removed; Postgres stays for local development
- `README.md` — Railway deployment section replaced with Modal deployment steps
- No frontend changes. No database schema changes.
- Follow-on changes, not in scope here: Neon for Postgres, R2 for object storage with a stem retention policy.
