## Why

The backend runs locally only; there's no way for users to access the app without running the server themselves. Deploying to Railway gives the API and RQ worker a permanent public URL so the frontend (Vercel) can talk to them.

## What Changes

- Add `railway.toml` defining two Railway services: `web` (FastAPI) and `worker` (RQ SimpleWorker)
- Add a startup script that runs `alembic upgrade head` then launches uvicorn
- Add `Procfile` as a fallback service definition
- Document all required Railway environment variables (DATABASE_URL, REDIS_URL, SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY, DEMUCS_DEVICE=cpu, SECRET_KEY)
- Pin `DEMUCS_DEVICE=cpu` for Railway starter tier (no GPU)
- Wire `CORS_ORIGINS` env var so the deployed frontend domain is accepted

## Capabilities

### New Capabilities

- `railway-config`: Railway deployment configuration — `railway.toml`, startup script, env var inventory, and Procfile for the API monorepo service

### Modified Capabilities

- `monorepo-foundation`: CORS origin is now driven by a `CORS_ORIGINS` env var instead of being hardcoded to `localhost:5173`

## Impact

- `apps/api/` — new `railway.toml`, `Procfile`, `start.sh`; `main.py` CORS origins from env
- No frontend changes (Vercel deploy is a separate change)
- Requires Railway project to be created manually and env vars set in the Railway dashboard
