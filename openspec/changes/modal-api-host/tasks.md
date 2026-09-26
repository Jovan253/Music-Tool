## 1. Verify the Modal API surface before writing against it

- [x] 1.1 Confirm against the installed Modal version (1.5.5) how local Python source is added to an image — `add_local_python_source` vs `add_local_dir` — and how `@modal.asgi_app()` is combined with `@app.function()`
- [x] 1.2 Confirm the `.spawn()` return type and whether the call id is worth persisting on the job row given status already lives in Postgres

Findings are recorded in `design.md` under "Verified API surface". Outcome: use
`add_local_dir` (not `add_local_python_source`), ignore `.env` and `.venv`,
install the `local-separation` extra via `pip_install_from_pyproject`, use
`Secret.from_name(required_keys=...)`, and do not persist the call id.

## 2. Secrets

- [ ] 2.1 Create a Modal Secret holding `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`, `SECRET_KEY`, `CORS_ORIGINS`
- [ ] 2.2 Document the secret's name and contents in `RUNBOOK.md`

## 3. Modal app

- [ ] 3.1 Create `apps/api/modal_app.py` defining the image (python 3.11, project dependencies, `apt_install("ffmpeg")`, API source) and the Modal app
- [ ] 3.2 Add the ASGI entrypoint returning the existing `main.app`, with the secret attached
- [ ] 3.3 Add a `migrate()` function that runs `alembic upgrade head`
- [ ] 3.4 Deploy and confirm `GET /health` responds on the Modal URL

## 4. Move the job body into Modal

- [ ] 4.1 Extend `apps/api/audio/modal_separation.py` so the GPU function takes `job_id`, downloads the upload, separates, transcodes to MP3, uploads stems, and writes `done`/`failed` with `processing_ms`
- [ ] 4.2 Attach the secret and set `retries` on the function
- [ ] 4.3 Reduce `apps/api/workers/separation.py` to the local development path only
- [ ] 4.4 Verify a failure inside the Modal function lands as `failed` with a useful `error` on the job row

## 5. Replace the queue

- [ ] 5.1 Change `apps/api/routes/upload.py` to `.spawn()` the Modal function when Modal is configured, and to run the local path in-process otherwise
- [ ] 5.2 Remove the lifespan stale-job sweep from `apps/api/main.py`
- [ ] 5.3 Delete `apps/api/job_queue.py`
- [ ] 5.4 Remove `rq` and `redis` from `pyproject.toml`
- [ ] 5.5 Remove the Redis service from `docker-compose.yml`
- [ ] 5.6 Update the tests: drop any Redis assumptions, add coverage for dispatch choosing Modal vs local

## 6. Retire Railway

- [ ] 6.1 Point Vercel's `VITE_API_BASE_URL` and the API's `CORS_ORIGINS` at the Modal URL
- [ ] 6.2 Suspend the Railway services and confirm the app still works end-to-end
- [ ] 6.3 Delete `apps/api/railway.toml`, `apps/api/Procfile`, `apps/api/start.sh`
- [ ] 6.4 Replace the README's Railway deployment section with Modal deployment steps
- [ ] 6.5 Update `RUNBOOK.md`: service map, env var provenance, cold start (no Redis), target architecture
- [ ] 6.6 Update `TASKS.md` Phase 4 deploy items
- [ ] 6.7 Delete the Railway project

## 7. Verify

- [ ] 7.1 Upload a short clip against the deployed Modal API and confirm four stems load in the mixer
- [ ] 7.2 Confirm a cold-start request to `/health` succeeds within a few seconds
- [ ] 7.3 Confirm local development runs with no Modal credentials and no Redis container
- [ ] 7.4 Confirm CI is still green
