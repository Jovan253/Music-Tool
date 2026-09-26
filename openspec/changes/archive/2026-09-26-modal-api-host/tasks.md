## 1. Verify the Modal API surface before writing against it

- [x] 1.1 Confirm against the installed Modal version (1.5.5) how local Python source is added to an image — `add_local_python_source` vs `add_local_dir` — and how `@modal.asgi_app()` is combined with `@app.function()`
- [x] 1.2 Confirm the `.spawn()` return type and whether the call id is worth persisting on the job row given status already lives in Postgres

Findings are recorded in `design.md` under "Verified API surface". Outcome: use
`add_local_dir` (not `add_local_python_source`), ignore `.env` and `.venv`,
install the `local-separation` extra via `pip_install_from_pyproject`, use
`Secret.from_name(required_keys=...)`, and do not persist the call id.

## 2. Secrets

- [x] 2.1 Create a Modal Secret holding `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`, `SECRET_KEY`, `CORS_ORIGINS`
- [x] 2.2 Document the secret's name and contents in `RUNBOOK.md`

Created as `music-tool` via `modal secret create --from-dotenv` on a filtered
temp file outside the repo, so no value passed through a command line.
`MODAL_TOKEN_SECRET` and the R2 keys were deliberately excluded — the API has
no need for Modal's own credentials.

## 3. Modal app

- [x] 3.1 Create `apps/api/modal_app.py` defining the image (python 3.11, project dependencies, `apt_install("ffmpeg")`, API source) and the Modal app
- [x] 3.2 Add the ASGI entrypoint returning the existing `main.app`, with the secret attached
- [x] 3.3 Add a `migrate()` function that runs `alembic upgrade head`
- [x] 3.4 Deploy and confirm `GET /health` responds on the Modal URL

Deployed at `https://jovan253--music-tool-api-fastapi-app.modal.run`. `/health`
returns 200 in 6.5s cold and 0.18s warm; `/docs` serves; an unauthenticated
`/jobs/{id}` returns 401. `migrate()` ran against Neon and found it at head,
which also proved the image contains `alembic.ini` and `alembic/` — the files
`add_local_python_source` would have dropped.

## 4. Move the job body into Modal

- [x] 4.1 Extend the GPU function so it takes `job_id`, downloads the upload, separates, transcodes to MP3, uploads stems, and writes `done`/`failed` with `processing_ms`
- [x] 4.2 Attach the secret and set `retries` on the function
- [x] 4.3 Reduce `apps/api/workers/separation.py` to a single implementation with no Modal branch
- [ ] 4.4 Verify a failure *during separation* lands as `failed` with a useful `error` on the job row

Moved to `apps/api/modal_separation.py` (repo root rather than `audio/`) so the
Modal entrypoint sits beside `modal_app.py`.

4.3 turned out to be load-bearing, not cosmetic: `run_separation` branched on
`MODAL_TOKEN_ID` internally, so once the same function ran *inside* the Modal
container — where that token exists — it would have called Modal from within
Modal. The branch moved out to `workers/dispatch.py`.

4.4 is partly covered: invoking `separate_job` with an unknown job id raised
`ValueError` from inside the GPU container, proving the source mounts, secret,
Neon connection and torch/demucs imports all work, and that `retries=2` is
active. A failure *after* the status write — mid-separation — is still
unverified.

## 5. Replace the queue

- [x] 5.1 Change `apps/api/routes/upload.py` to `.spawn()` the Modal function when Modal is configured, and to run the local path in-process otherwise
- [x] 5.2 Remove the lifespan stale-job sweep from `apps/api/main.py`
- [x] 5.3 Delete `apps/api/job_queue.py`
- [x] 5.4 Remove `rq` and `redis` from `pyproject.toml`
- [x] 5.5 Remove the Redis service from `docker-compose.yml`
- [x] 5.6 Update the tests: drop any Redis assumptions, add coverage for dispatch choosing Modal vs local

The local path uses a FastAPI `BackgroundTask` so the endpoint stays responsive
without Redis. Also deleted `get_stale_processing_jobs`, dead once the sweep
went. 18 tests pass, including one asserting the dispatch function-name
constant still matches the deployed Modal function, since that name is resolved
at runtime and a rename would otherwise surface only when a job runs.

## 6. Retire Railway

- [ ] 6.1 Point Vercel's `VITE_API_BASE_URL` and the API's `CORS_ORIGINS` at the Modal URL — deferred, Vercel does not exist yet
- [x] 6.2 Confirm the app works end-to-end without Railway
- [x] 6.3 Delete `apps/api/railway.toml`, `apps/api/Procfile`, `apps/api/start.sh`
- [x] 6.4 Replace the README's Railway deployment section with Modal deployment steps
- [x] 6.5 Update `RUNBOOK.md`: service map, env var provenance, cold start (no Redis), target architecture
- [x] 6.6 Update `TASKS.md` Phase 4 deploy items
- [ ] 6.7 Delete the Railway project — manual dashboard step, only the account owner can do it

## 7. Verify

- [x] 7.1 Upload a short clip against the deployed Modal API and confirm four stems load in the mixer
- [x] 7.2 Confirm a cold-start request to `/health` succeeds within a few seconds
- [ ] 7.3 Confirm local development runs with no Modal credentials and no Redis container — untested; `MODAL_TOKEN_ID` is set locally, and the in-process path needs the `local-separation` extra installed
- [x] 7.4 Confirm CI is still green

Evidence for 7.1: job `9395a276` logged `spawned on Modal` from the deployed API,
which also proves `.spawn()` works from inside a Modal container on ambient
credentials with no `MODAL_TOKEN_*` present. An earlier direct invocation
separated a 41s track in 6.7s on the T4 (17.2s wall clock including storage),
producing four stems with distinct md5s and a signed URL returning 200.

7.2: 6.5s cold, 0.18s warm.

Two bugs surfaced only by running real audio, both fixed: `numpy`/`soundfile`
missing from the `local-separation` extra, and `update_job` being unable to clear
a stale error so a retried job showed `done` alongside the old failure text.
