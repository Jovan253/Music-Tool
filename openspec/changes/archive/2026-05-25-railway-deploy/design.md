## Context

The API currently runs locally with CORS hardcoded to `localhost:5173` and all secrets in a `.env` file. Railway is the target platform: it natively supports monorepo root configs (`railway.toml`), PostgreSQL and Redis add-ons, and can run multiple services from one repo. The two services needed are:

- **web**: FastAPI via uvicorn on `$PORT` (Railway injects this)
- **worker**: RQ SimpleWorker consuming the `default` queue (Windows-safe class, already mandated by CLAUDE.md)

Alembic migrations must run before the web process starts so the DB schema is always current on deploy.

## Goals / Non-Goals

**Goals:**
- `railway.toml` defining both services from `apps/api/`
- `start.sh` that runs `alembic upgrade head` then starts uvicorn
- CORS origins driven by `CORS_ORIGINS` env var (comma-separated), falling back to `localhost:5173` for local dev
- Inventory of all env vars required on Railway with descriptions
- `Procfile` as fallback if `railway.toml` isn't picked up

**Non-Goals:**
- Automatic Railway project creation or CLI provisioning (manual step — Railway dashboard)
- Frontend Vercel deploy (separate change)
- GPU/CUDA on Railway (starter tier is CPU-only; `DEMUCS_DEVICE=cpu`)
- Zero-downtime migrations or blue/green deploys
- Docker containerisation (Railway can build from `pyproject.toml` directly via Nixpacks)

## Decisions

**`railway.toml` over `Procfile` only**
Railway's native config supports per-service `startCommand`, `buildCommand`, and health check paths. `Procfile` works but can't express two services or health checks. `railway.toml` is the primary; `Procfile` is kept as a single-service fallback.

**`start.sh` for web startup, not a custom entrypoint**
Running `alembic upgrade head` as a `buildCommand` in `railway.toml` would run it at every build, not deploy — migrations need the live `DATABASE_URL` which isn't available at build time. A startup script is the simplest correct approach.

**`CORS_ORIGINS` env var, comma-separated**
Single env var, split on commas in `main.py`. In development the `.env` file continues to set `CORS_ORIGINS=http://localhost:5173`. On Railway the var is set to the Vercel domain. No schema change needed.

**Nixpacks build (no Dockerfile)**
Railway auto-detects `pyproject.toml` and builds with Nixpacks, which handles Python, ffmpeg, and torch without a custom Dockerfile. Keeps the repo lighter; a Dockerfile can be added later if build customisation is needed.

**`SimpleWorker` class**
Already required by CLAUDE.md for Windows. On Railway (Linux) the standard Worker would work too, but `SimpleWorker` is safe on both and avoids divergence between dev and prod.

## Risks / Trade-offs

- **Demucs cold start / memory** → Railway starter has 512 MB RAM. Demucs `htdemucs` loads ~300 MB of weights; a single separation job may push close to the limit. Mitigation: document the need to upgrade to the 8 GB tier for real workloads; the MVP demo can use short clips.
- **Nixpacks + torch size** → PyTorch CPU wheel is ~200 MB; build times will be long (~5–10 min first build). Mitigation: Railway caches the build layer after first deploy.
- **Worker and web on separate services share the same DB/Redis** → Both read `DATABASE_URL` and `REDIS_URL` from Railway's shared env. No conflict as long as Alembic only runs from the web service.
- **Alembic on every restart** → `upgrade head` is idempotent so re-running on crash-loop restarts is safe.

## Migration Plan

1. Add `start.sh`, `railway.toml`, `Procfile` to `apps/api/`
2. Update `main.py` to read `CORS_ORIGINS` from env
3. Create Railway project in dashboard, attach PostgreSQL and Redis add-ons
4. Set env vars in Railway dashboard (see env var inventory in spec)
5. Push to `main` — Railway auto-deploys
6. Run a smoke test: `GET /health`, upload a short clip, verify separation completes
7. Rollback: redeploy previous commit via Railway dashboard
