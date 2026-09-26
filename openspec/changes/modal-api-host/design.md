## Context

The current topology is four always-on Railway services: a FastAPI web service, an RQ worker, Postgres, and Redis. The worker's only real job is to wait on a Modal GPU call and then move bytes into Supabase — it is a paid, permanently-running process whose work is almost entirely I/O against other people's infrastructure.

Modal bills per second of execution and scales to zero. Hosting the ASGI app there means the API costs nothing while idle, and a Modal function call replaces the queue outright: it is durable, has an addressable id, and supports automatic retries.

## Decisions

**The Modal function owns the entire job, not just inference**

Today `run_separation` (on the worker) calls Modal for bytes, then does the Supabase upload and the job-status write. With no worker process there is nowhere for that glue to live, so the Modal function takes it over: it downloads the upload, separates, transcodes, uploads stems, and writes the terminal status.

This reverses a decision recorded in `modal-gpu-worker/design.md`, which deliberately kept Supabase credentials out of Modal so that the function was "purely compute: bytes in, bytes out". That rationale was secret hygiene, and it was reasonable while a trusted worker existed to do the I/O. It no longer holds: the worker is the thing being deleted, and Modal Secrets are a real secret store rather than an environment leak. The tradeoff is accepted knowingly.

The payoff is that `GET /jobs/{job_id}` keeps reading status from Postgres exactly as it does now, so **the frontend polling contract is untouched** and no client code changes.

**One function, not a GPU/CPU split**

Storage I/O runs inside the GPU container, so a few seconds of T4 time is spent on downloads and uploads. Splitting into a cheap CPU orchestrator that calls a GPU inference function would avoid that, at the cost of a second function, another hop, and more failure modes. At ~25s per job against $30/month of credits, the waste is immaterial. Revisit only if credits become the binding constraint.

**Retries replace the startup stale-job sweep**

`main.py` currently resets `processing` jobs to `pending` at startup and re-enqueues them, which made sense for a long-lived web service. Under scale-to-zero, containers start and stop constantly, so that sweep would fire on every cold start and re-run jobs that are legitimately in flight. Modal function retries cover the transient failures the sweep was there for, and a job whose retries are exhausted ends as `failed` with an error — which is the honest outcome.

**Migrations run as an explicit one-shot, not at app startup**

Alembic in an ASGI lifespan would race whenever Modal starts more than one container. A dedicated `migrate()` Modal function invoked manually (or from a deploy step) keeps it single-writer and makes the deploy sequence legible. This is what `start.sh` was doing serially; it becomes an explicit step rather than an implicit one.

**Local development keeps the in-process path**

`MODAL_TOKEN_ID` already gates the Modal path. With Modal unset, dispatch runs the existing local separation in-process, so a developer needs neither Modal credentials nor a Redis container — only Postgres via docker compose. Note that a Modal-hosted job cannot reach a localhost Postgres, so local work necessarily uses the local executor; this is a property of the split, not a bug.

## Risks

- **Cold start latency on the API.** A scale-to-zero container adds a second or two to the first request after idle. Acceptable for a portfolio app; mitigated later with a warm-up cron if it grates.
- **Source layout must satisfy Modal's image build.** Modal 1.x no longer auto-mounts local Python source, so the image has to declare the API package explicitly. The exact mechanism must be verified against the installed Modal version (1.5.5) during implementation rather than assumed — this is the most likely place to lose time.
- **Secrets move house.** Every variable that lived in Railway's dashboard has to exist in the Modal Secret before the first deploy, or the app fails at import: `db.py` and `storage/supabase_storage.py` both raise on missing vars at module scope.
- **Deleting Railway is irreversible-ish.** Keep the Railway project in place (suspended, not deleted) until a Modal deploy has passed a real upload end-to-end.
- **`pydub` needs ffmpeg in the image.** The export mixdown and MP3 transcode both depend on it; the existing separation image already does `apt_install("ffmpeg")` and the API image needs the same.

## Rollout

1. Create the Modal Secret with the full production variable set
2. Deploy the separation function and the ASGI app to Modal
3. Run `migrate()` against the production database
4. Smoke test `/health`, then a real upload end-to-end against the Modal URL
5. Point `CORS_ORIGINS` and the Vercel `VITE_API_BASE_URL` at the Modal URL
6. Suspend the Railway services, confirm nothing breaks for a few days, then delete the project and the deploy files

Rollback before step 6 is to repoint the frontend at the Railway URL; the database and storage are shared, so no data migration is involved either way.
