# Runbook

Operational reference: where every external service lives, which credential comes from where, and how to get the app running from a cold machine. Written for coming back to this project after months away.

For product scope and roadmap see [TASKS.md](TASKS.md). For first-time setup prose see [README.md](README.md).

---

## Status — read this first

Last verified: **2026-09-26** (repo had been dormant since 2026-05-26).

| Thing | State |
|---|---|
| Local dev environment | **Absent.** No `.env` files, no `apps/api/.venv`, no `node_modules`. Cold start required — see [Cold start](#cold-start-local). |
| Supabase project | Exists, but **likely auto-paused** (free plan pauses after 7 days of no DB activity). Restore is free, one click. |
| Railway | Project exists. **Being retired** — see [Target architecture](#target-architecture). |
| Modal | Account status unconfirmed. `music-tool-separation` must be deployed for GPU separation to work. |
| Vercel | Not set up yet. |
| Automated tests / CI | None exist. |

The app has never been verified running end-to-end in production.

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
| Modal workspace | `<fill in>` | modal.com → workspace switcher |
| Modal app name | `music-tool-separation` | Defined in `apps/api/audio/modal_separation.py:8` |
| Deployed API URL | `<fill in>` | Modal app URL once the ASGI app is deployed |
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

### Modal — GPU separation (and, after migration, the API)
- **Dashboard:** https://modal.com/apps
- **Tokens:** https://modal.com/settings/tokens
- **Currently does:** runs Demucs on a T4 GPU. `apps/api/workers/separation.py:17` looks the function up **by name**, so the app must already be deployed — it is not deployed automatically with your API.
- **Free plan:** Starter is $0 with **$30/month of compute credits** (~50 T4-hours), 10 concurrent GPUs. At ~25s/song that is thousands of songs a month.
- **Deploy the separation app:**
  ```powershell
  cd apps\api
  modal deploy audio/modal_separation.py
  ```
- **Check when broken:**
  - modal.com/apps → is `music-tool-separation` listed and deployed?
  - The app's logs tab shows per-invocation errors and GPU cold-start time.
  - Credit balance on the billing page — jobs fail once credits run out.

### Neon — Postgres (migration target)
- **Dashboard:** https://console.neon.tech
- **Will do:** job records (`apps/api/models/job.py`), schema managed by Alembic.
- **Free plan:** 0.5GB storage, 100 CU-hours/month, auto-suspends after 5 minutes idle but **auto-resumes on the next connection in ~0.5–1s** — no manual unpausing, which is why it beats Supabase Postgres here.
- **Note:** `apps/api/db.py` already sets `pool_pre_ping=True`, which is exactly what's needed to survive auto-suspend. No code change required beyond `DATABASE_URL`.

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
| `DATABASE_URL` | docker compose locally; Neon in prod | Local: `postgresql://musictool:musictool@localhost:5432/musictool` |
| `REDIS_URL` / `RQ_REDIS_URL` | docker compose locally | **Goes away** once the queue moves to Modal `.spawn()` |
| `SUPABASE_URL` | Supabase → Settings → Data API | Public value |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API | **Secret.** Server-side only, never in frontend |
| `SUPABASE_ANON_KEY` | Supabase → Settings → API | Public by design |
| `SECRET_KEY` | you | Generate: `openssl rand -hex 32` |
| `CORS_ORIGINS` | you | Comma-separated. Must include your Vercel URL in prod |
| `DEMUCS_DEVICE` | you | `cpu` or `cuda`. Only affects the local fallback path |
| `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET` | modal.com → Settings → Tokens | **Secret.** Presence of `MODAL_TOKEN_ID` is what switches separation to GPU |

Frontend (`apps/web/.env`, copied from `apps/web/.env.example`):

| Variable | Notes |
|---|---|
| `VITE_API_BASE_URL` | Defaults to `http://localhost:8000`. Set to the deployed API URL in Vercel |
| `VITE_SUPABASE_URL` | Public |
| `VITE_SUPABASE_ANON_KEY` | Public by design — this is the anon key, not the service role key |

Anything prefixed `VITE_` is compiled into the client bundle and is world-readable. Never put a service-role key there.

---

## Cold start (local)

Current state assumed: nothing installed. Verified present on this machine: Node v20.11.0, Python 3.11.8, Docker 29.7.2.

**1. Unpause Supabase.** https://supabase.com/dashboard → if the project shows *Paused*, restore it. Nothing else will work until this is done.

**2. Start local Postgres + Redis.**
```powershell
docker compose up -d
```

**3. Backend env + dependencies.**
```powershell
cd apps\api
Copy-Item .env.example .env
# edit .env — at minimum SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
```

Dependency extras — the core install is deliberately light:

| Install | Gets you |
|---|---|
| `pip install -e .` | API, queue, storage, Modal client. No torch. |
| `pip install -e ".[dev]"` | The above plus pytest. Use this for normal development. |
| `pip install -e ".[local-separation]"` | Adds torch + demucs (~2.5GB) — only needed to run separation on your own CPU instead of Modal. |

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

**5. Run three processes, one terminal each.**
```powershell
# Terminal 1 — frontend
cd apps\web; npm run dev

# Terminal 2 — API
cd apps\api; .venv\Scripts\activate; uvicorn main:app --reload

# Terminal 3 — worker (SimpleWorker avoids Windows fork issues)
cd apps\api; .venv\Scripts\activate; rq worker default --worker-class rq.SimpleWorker
```

**6. Verify.**
- http://localhost:5173 — frontend
- http://localhost:8000/health — `{"status":"ok"}`
- http://localhost:8000/docs — API docs
- Sign in, upload a short clip, confirm four stems appear in the mixer.

Do not skip step 5's third terminal. The API does not process jobs itself — without the worker, jobs sit in `processing` forever.

---

## Troubleshooting

**Uploads silently do nothing / Supabase never populates.** On Windows, closing a terminal does not kill uvicorn. A stale process on port 8000 intercepts requests while your new server idles.
```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```
If it respawns or the PID won't resolve: `Get-Process python | Stop-Process -Force`.

**Jobs stuck in `processing`.** The RQ worker isn't running, or it crashed. Check terminal 3.

**Jobs fail on a timeout.** The RQ timeout now adapts to which separation path is active — `separation_timeout()` in `apps/api/workers/separation.py` returns 420s when `MODAL_TOKEN_ID` is set and 1800s when it isn't. If a job still times out, check the worker log: it logs which path it took on every run, and warns loudly when it falls back to local CPU.

**CORS errors in the browser.** `CORS_ORIGINS` doesn't include the origin you're calling from. It's comma-separated and falls back to `http://localhost:5173`.

**Modal call fails with "function not found".** The app was never deployed, or was deployed to a different workspace. Re-run `modal deploy audio/modal_separation.py`.

**Jobs created before May 2026 fail.** Pre-Supabase jobs store local filesystem paths that no longer resolve. Expected; ignore those rows.

**Vite / Node version errors.** Do not upgrade Vite past 5.x — Vite 8+ requires Node 20.19+ and this machine runs 20.11.0.

---

## Target architecture

Decision made 2026-09-26: migrate off Railway to an all-free, scale-to-zero stack. Motivation is uptime as much as cost — Supabase's 7-day pause and Railway's $1/month free credit both make an occasionally-visited portfolio app fragile.

| Concern | From | To |
|---|---|---|
| API host | Railway `web` service | Modal `@modal.asgi_app()` |
| Job queue | Redis + RQ + Railway `worker` | Modal `.spawn()` + poll by call id |
| GPU separation | Modal | unchanged |
| Postgres | Supabase / Railway add-on | Neon |
| Object storage | Supabase Storage | Cloudflare R2 |
| Auth | Supabase Auth | unchanged |
| Frontend | — | Vercel |

Removing Redis and RQ deletes `apps/api/job_queue.py`, the separate worker process, the Redis add-on, and the stale-job requeue logic in `apps/api/main.py:29`.

Order of work:
1. ~~Fix the `job_timeout` / CPU-fallback mismatch so failures are loud instead of confusing.~~ **Done.**
2. Move the API to Modal, replace RQ with `.spawn()`, retire Railway.
3. Move Postgres to Neon.
4. Move storage to R2 and add a stem retention policy — at ~20–60MB per job, unbounded storage fills any free tier.
5. Baseline tests + CI.
6. UX polish: upload progress, waveform loading states, error surfaces, mobile layout.

---

## Future: account hygiene

Two open items, deliberately deferred:

1. **Settle the app's name.** Currently "Music Tool" in the repo, provisionally "MusicSeparator" elsewhere. Worth deciding before creating more accounts, since the name ends up baked into project slugs, bucket names, and deploy URLs that are annoying to change later.
2. **One mailbox for all service accounts.** Right now Supabase, Railway, Modal, Neon, R2 and Vercel notifications scatter across a personal inbox with no shared heading. A dedicated address under the app's name keeps billing warnings, pause notices and quota alerts in one filterable place — the Supabase pause that broke this project is exactly the kind of email worth not missing.

   Cheapest version needing zero setup: a Gmail `+` alias (`youraddress+musicseparator@gmail.com`) works immediately on every one of these services and filters cleanly. A separate account is tidier long-term but only worth it if the project outlives the portfolio use.

## Gotchas worth remembering

- **`.claude/` is gitignored**, so project-level Claude config doesn't travel with the repo. `CLAUDE.md` at the root is tracked, which is the part that matters.
- **`modal deploy` is a separate step from your API deploy.** The worker resolves the Modal function by name at runtime, so a stale or missing deploy fails only when a job runs.
- **Two OpenSpec changes are unarchived** (`modal-gpu-worker`, `railway-deploy`) with all tasks ticked including production smoke tests that were never confirmed. Treat their checkmarks as unverified.
- **Supabase free plan allows 2 active projects.** If another project holds a slot, this one can't be restored until you pause that one.
- Stem storage is 256kbps MP3, 4 stems per job, plus the original upload — budget ~20–60MB per song when sizing any storage tier.
