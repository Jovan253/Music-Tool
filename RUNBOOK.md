# Runbook

Operational reference: where every external service lives, which credential comes from where, and how to get the app running from a cold machine. Written for coming back to this project after months away.

For product scope and roadmap see [TASKS.md](TASKS.md). For first-time setup prose see [README.md](README.md).

---

## Status — read this first

Last verified: **2026-09-26** (repo had been dormant since 2026-05-26).

| Thing | State |
|---|---|
| Local dev environment | Working. `apps/api/.venv` and `node_modules` installed, `.env` files populated. **ffmpeg is still missing** — see [Cold start](#cold-start-local). |
| API | **Live on Modal**: `https://jovan253--music-tool-api-fastapi-app.modal.run`. `/health` 200 in 6.5s cold, 0.18s warm. |
| GPU separation | **Live on Modal** as `music-tool-separation` / `separate_job`. |
| Postgres | **Live on Neon**, migrated to head (`7bc48242348d`). |
| Supabase | Used for auth and (still) file storage. Was auto-paused after the dormancy; restored. |
| Modal secret | `music-tool` exists with all six required keys. |
| Railway | Still running, **not yet retired** — it stays until one real upload succeeds end-to-end on Modal. |
| Cloudflare R2 | Credentials in `.env`, but **no code reads them yet** — the storage migration is a later change. |
| Vercel | Not set up yet. |
| Tests / CI | 18 API tests; GitHub Actions runs them plus web lint and build. Green. |

**Not yet verified end-to-end:** a real authenticated upload producing four playable stems. Everything up to that point is confirmed working.

---

## Your values — fill these in once

Fill this in the first time you check each dashboard, so you never have to hunt again. Safe to commit: project refs and anon keys are public by design.

**Never put service-role keys, Modal secrets, or R2 secret keys in this file.** They belong in `.env` (gitignored) and in each host's env var settings.

| Value | Yours | Where to find it |
|---|---|---|
| Supabase project ref | `<fill in>` | Dashboard URL: `supabase.com/dashboard/project/<ref>` |
| Supabase URL | `https://<ref>.supabase.co` | Project Settings → Data API |
| Neon project / connection host | `<fill in>` | Neon console → your project → Connection string |
| R2 account ID | `<fill in>` | Cloudflare dashboard → R2 → Overview |
| R2 bucket names | `uploads`, `stems` | Chosen to match the current Supabase bucket names |
| Modal workspace | `jovan253` | `modal profile current` |
| Modal apps | `music-tool-api`, `music-tool-separation` | `apps/api/modal_app.py`, `apps/api/modal_separation.py` |
| Modal secret name | `music-tool` | `modal secret list` |
| Deployed API URL | https://jovan253--music-tool-api-fastapi-app.modal.run | `modal app list`, or the deploy output |
| Vercel frontend URL | `<fill in>` | Vercel project → Domains |
| GitHub repo | https://github.com/Jovan253/Music-Tool | — |

---

## Service map

What each service does, where to go, and what to check when something is broken.

### Supabase — Auth (and, for now, storage + Postgres)
- **Dashboard:** https://supabase.com/dashboard
- **Currently does:** user auth (`apps/api/auth.py`, `apps/web/src/features/auth/`), file storage in buckets `uploads` and `stems`, and optionally Postgres.
- **After migration:** auth only.
- **Free plan limits:** 500MB database, 1GB file storage, 5GB egress, 50k monthly active users, **2 active projects**, and **auto-pause after 7 days of database inactivity**.
- **Check when broken:**
  - Project banner says *Paused* → click Restore. This is the single most likely failure after time away.
  - Storage → confirm `uploads` and `stems` buckets still exist.
  - Settings → API → confirm the service-role key hasn't been rotated out from under your `.env`.
  - Auth → Users → confirm your login account still exists.
- **Keeping it alive:** any real DB query resets the 7-day pause clock. A weekly Modal cron that pings the database is the cheap insurance (free, and Modal cron is included).

### Modal — hosts both the API and GPU separation
- **Dashboard:** https://modal.com/apps
- **Tokens:** https://modal.com/settings/tokens
- **Two apps, deployed separately:**

  | App | Entrypoint | What it is |
  |---|---|---|
  | `music-tool-api` | `apps/api/modal_app.py` | The FastAPI app as an ASGI function, plus `migrate()` |
  | `music-tool-separation` | `apps/api/modal_separation.py` | `separate_job(job_id)` on a T4, owns the whole job |

- **Free plan:** Starter is $0 with **$30/month of compute credits** (~50 T4-hours), 10 concurrent GPUs. At ~25s/song that is thousands of songs a month.
- **Deploy:**
  ```powershell
  cd apps\api
  .venv\Scripts\modal.exe deploy modal_app.py
  .venv\Scripts\modal.exe deploy modal_separation.py
  ```
- **Run migrations** (never runs automatically — deliberately outside the request path):
  ```powershell
  .venv\Scripts\modal.exe run modal_app.py::migrate
  ```
- **Check when broken:**
  - modal.com/apps → are both apps listed as deployed?
  - `workers/dispatch.py` resolves `separate_job` **by name at runtime**, so a rename or a missing separation deploy fails only once a job actually runs, not at API boot.
  - The app's logs tab shows per-invocation errors and GPU cold-start time.
  - Credit balance on the billing page — jobs fail once credits run out.
- **Secrets:** the `music-tool` secret supplies all six config vars. Changing a value means `modal secret create music-tool --from-dotenv <file> --force`, then redeploying both apps.

### Neon — Postgres
- **Dashboard:** https://console.neon.tech
- **Does:** job records (`apps/api/models/job.py`), schema managed by Alembic. Currently at revision `7bc48242348d`.
- **Free plan:** 0.5GB storage, 100 CU-hours/month, auto-suspends after 5 minutes idle but **auto-resumes on the next connection in ~0.5–1s** — no manual unpausing, which is why it beats Supabase Postgres here.
- **Note:** `apps/api/db.py` sets `pool_pre_ping=True`, which is what makes auto-suspend survivable, and normalizes the URL so a `postgres://` connection string from any provider works.

### Cloudflare R2 — object storage (migration target)
- **Dashboard:** https://dash.cloudflare.com → R2
- **Will do:** original uploads and separated stems.
- **Free plan:** 10GB storage, 1M writes/month, 10M reads/month, **zero egress fees, permanently**. Audio streaming is egress-heavy, which is why this matters more than the storage number.
- **Note:** R2 is S3-compatible, so `apps/api/storage/supabase_storage.py` becomes a boto3 client and signed URLs keep working the same way.

### Vercel — frontend
- **Dashboard:** https://vercel.com/dashboard
- **Will do:** host `apps/web`. Root directory `apps/web`, build `npm run build`, output `dist`.
- **Must set:** `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`.
- **Gotcha:** after deploying, add the Vercel URL to the API's `CORS_ORIGINS` or every request fails in the browser with an opaque CORS error.

### Railway — being retired
- **Dashboard:** https://railway.app/dashboard
- **Why retired:** the Free plan is $1/month of credit, which won't run four always-on services; Hobby is $5/month and web + worker + Postgres + Redis running 24/7 will likely exceed its included credit. Modal's scale-to-zero does the same job for $0.
- Leave the project in place until the Modal API deploy is verified, then delete it to stop any accrual.

---

## Environment variables — provenance

Backend (`apps/api/.env`, copied from `apps/api/.env.example`):

| Variable | Comes from | Notes |
|---|---|---|
| `DATABASE_URL` | Neon console → Connection string | Currently points at Neon even locally, so docker compose Postgres is optional. A `postgres://` URL is normalized automatically. |
| `SUPABASE_URL` | Supabase → Settings → Data API | Public value |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API | **Secret.** Server-side only, never in frontend |
| `SUPABASE_ANON_KEY` | Supabase → Settings → API | Public by design |
| `SECRET_KEY` | you | Generate: `openssl rand -hex 32` |
| `CORS_ORIGINS` | you | Comma-separated. Must include your Vercel URL in prod |
| `DEMUCS_DEVICE` | you | `cpu` or `cuda`. Only affects the local in-process path |
| `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET` | modal.com → Settings → Tokens | **Secret.** Presence of `MODAL_TOKEN_ID` is what makes dispatch spawn on Modal instead of running in-process |
| `R2_*` | Cloudflare → R2 | **No code reads these yet.** Present ahead of the storage migration. |

Production values do **not** come from this file — they come from the Modal
secret `music-tool`, which holds the first six rows. Note that `MODAL_TOKEN_*`
and the R2 keys are deliberately *excluded* from that secret: the API has no
need for Modal's own credentials, and nothing reads R2 yet.

Frontend (`apps/web/.env`, copied from `apps/web/.env.example`):

| Variable | Notes |
|---|---|
| `VITE_API_BASE_URL` | Defaults to `http://localhost:8000`. Set to the deployed API URL in Vercel |
| `VITE_SUPABASE_URL` | Public |
| `VITE_SUPABASE_ANON_KEY` | Public by design — this is the anon key, not the service role key |

Anything prefixed `VITE_` is compiled into the client bundle and is world-readable. Never put a service-role key there.

---

## Cold start (local)

For a machine with nothing installed. Verified present here: Node v20.11.0, Python 3.11.8, Docker 29.7.2.

**1. Unpause Supabase.** https://supabase.com/dashboard → if the project shows *Paused*, restore it. Auth won't work until you do.

**2. Backend env + dependencies.**
```powershell
cd apps\api
Copy-Item .env.example .env
# edit .env — at minimum SUPABASE_* and DATABASE_URL
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
```

Dependency extras — the core install is deliberately light:

| Install | Gets you |
|---|---|
| `pip install -e .` | API, storage, Modal client. No torch. |
| `pip install -e ".[dev]"` | The above plus pytest. Use this for normal development. |
| `pip install -e ".[local-separation]"` | Adds torch + demucs (~2.5GB) — only needed to run separation on your own CPU instead of Modal. |

Docker is now **optional**: Redis is gone entirely, and `DATABASE_URL` points at Neon. Run `docker compose up -d` only if you want a local Postgres instead.

**ffmpeg is a separate system install** and `pydub` needs it for the export mixdown and MP3 transcode. Without it, export fails at runtime with a confusing pydub warning. Install once:
```powershell
winget install Gyan.FFmpeg
```

**4. Frontend env + dependencies.**
```powershell
cd apps\web
Copy-Item .env.example .env
npm install
```

**4. Run two processes, one terminal each.** (There is no third terminal any more — the RQ worker is gone.)
```powershell
# Terminal 1 — frontend
cd apps\web; npm run dev

# Terminal 2 — API
cd apps\api; .venv\Scripts\activate; uvicorn main:app --reload
```

**5. Verify.**
- http://localhost:5173 — frontend
- http://localhost:8000/health — `{"status":"ok"}`
- http://localhost:8000/docs — API docs
- Sign in, upload a short clip, confirm four stems appear in the mixer.

With `MODAL_TOKEN_ID` set, uploads dispatch to Modal's GPU and come back in ~25s. Without it, separation runs in-process as a FastAPI background task on your CPU — roughly 12 minutes per track, and `uvicorn --reload` may kill it mid-run.

### Testing the local frontend against the deployed API

Point the frontend at Modal instead of localhost by setting `VITE_API_BASE_URL` in `apps/web/.env`:
```
VITE_API_BASE_URL=https://jovan253--music-tool-api-fastapi-app.modal.run
```
This works because the Modal secret's `CORS_ORIGINS` still allows `http://localhost:5173`. Restart the Vite dev server after changing it — Vite reads env at startup.

---

## Troubleshooting

**Uploads silently do nothing / Supabase never populates.** On Windows, closing a terminal does not kill uvicorn. A stale process on port 8000 intercepts requests while your new server idles.
```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```
If it respawns or the PID won't resolve: `Get-Process python | Stop-Process -Force`.

**Jobs stuck in `processing`.** Check the `music-tool-separation` logs on modal.com. A job that dies without writing a terminal status means the container was killed rather than raising — `run_separation` records `failed` on any exception it sees. There is no longer a startup sweep to rescue these; Modal's `retries=2` is the recovery mechanism.

**Jobs fail on a timeout.** `SEPARATION_TIMEOUT_S` in `apps/api/modal_separation.py` is 900s, which is generous because a cold container pulls Demucs weights before starting work. Actual separation on a T4 is ~25s.

**CORS errors in the browser.** `CORS_ORIGINS` doesn't include the origin you're calling from. In production it comes from the Modal secret, not `.env` — updating it means recreating the secret and redeploying.

**Modal call fails with "function not found".** `workers/dispatch.py` resolves the function by name at runtime. Either `music-tool-separation` was never deployed, it went to a different workspace, or `separate_job` was renamed without updating `MODAL_FUNCTION_NAME`. Re-run `modal deploy modal_separation.py`.

**Config change didn't take effect in production.** The Modal secret is read at container start, so recreate the secret *and* redeploy both apps.

**Jobs created before May 2026 fail.** Pre-Supabase jobs store local filesystem paths that no longer resolve. Expected; ignore those rows.

**Vite / Node version errors.** Do not upgrade Vite past 5.x — Vite 8+ requires Node 20.19+ and this machine runs 20.11.0.

---

## Target architecture

Decision made 2026-09-26: migrate off Railway to an all-free, scale-to-zero stack. Motivation is uptime as much as cost — Supabase's 7-day pause and Railway's $1/month free credit both make an occasionally-visited portfolio app fragile.

| Concern | From | To | State |
|---|---|---|---|
| API host | Railway `web` service | Modal `@modal.asgi_app()` | **Done** |
| Job queue | Redis + RQ + Railway `worker` | Modal `.spawn()` | **Done** — `job_queue.py`, the worker and the stale-job sweep are deleted |
| GPU separation | Modal, inference only | Modal, owns the whole job | **Done** |
| Postgres | Supabase / Railway add-on | Neon | **Done** — migrated to head |
| Object storage | Supabase Storage | Cloudflare R2 | Not started; credentials in place |
| Auth | Supabase Auth | unchanged | — |
| Frontend | — | Vercel | Not started |
| Railway | 4 always-on services | deleted | **Pending** the end-to-end upload test |

Order of work:
1. ~~Fix the `job_timeout` / CPU-fallback mismatch so failures are loud instead of confusing.~~ **Done.**
2. ~~Move the API to Modal, replace RQ with `.spawn()`.~~ **Done.** Retiring Railway is the one remaining piece, gated on a real upload succeeding.
3. ~~Move Postgres to Neon.~~ **Done.**
4. Move storage to R2 and add a stem retention policy — at ~20–60MB per job, unbounded storage fills any free tier.
5. ~~Baseline tests + CI.~~ **Done** — 18 API tests plus a GitHub Actions workflow running them alongside web lint and build.
6. UX polish: upload progress, waveform loading states, error surfaces, mobile layout.
7. Deploy the frontend to Vercel, then add its URL to `CORS_ORIGINS` in the Modal secret.

---

## Future items

Deliberately deferred:

1. **Architecture and sequence diagrams, plus a plain-language explanation of how the app works.** Worth doing *after* the Modal migration lands, not before — the topology is mid-change, so anything drawn now documents a system that is about to stop existing. Wanted: an architecture diagram (who talks to whom across Modal, Neon, R2, Supabase Auth, Vercel), a sequence diagram for the upload → separate → poll → play flow, and a general written explanation suitable for a portfolio reader who has never seen the repo.

2. **Settle the app's name.** Currently "Music Tool" in the repo, provisionally "MusicSeparator" elsewhere. Worth deciding before creating more accounts, since the name ends up baked into project slugs, bucket names, and deploy URLs that are annoying to change later.
3. **One mailbox for all service accounts.** Right now Supabase, Railway, Modal, Neon, R2 and Vercel notifications scatter across a personal inbox with no shared heading. A dedicated address under the app's name keeps billing warnings, pause notices and quota alerts in one filterable place — the Supabase pause that broke this project is exactly the kind of email worth not missing.

   Cheapest version needing zero setup: a Gmail `+` alias (`youraddress+musicseparator@gmail.com`) works immediately on every one of these services and filters cleanly. A separate account is tidier long-term but only worth it if the project outlives the portfolio use.

## Gotchas worth remembering

- **`.claude/` is gitignored**, so project-level Claude config doesn't travel with the repo. `CLAUDE.md` at the root is tracked, which is the part that matters.
- **`modal deploy` is a separate step from your API deploy.** The worker resolves the Modal function by name at runtime, so a stale or missing deploy fails only when a job runs.
- **Two OpenSpec changes are unarchived** (`modal-gpu-worker`, `railway-deploy`) with all tasks ticked including production smoke tests that were never confirmed. Treat their checkmarks as unverified.
- **Supabase free plan allows 2 active projects.** If another project holds a slot, this one can't be restored until you pause that one.
- Stem storage is 256kbps MP3, 4 stems per job, plus the original upload — budget ~20–60MB per song when sizing any storage tier.
