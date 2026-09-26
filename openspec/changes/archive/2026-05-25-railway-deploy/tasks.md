## 1. CORS and env var plumbing

- [x] 1.1 Update `apps/api/main.py` to read `CORS_ORIGINS` env var (comma-split), falling back to `http://localhost:5173`
- [x] 1.2 Add `CORS_ORIGINS` to `apps/api/.env.example` with a comment
- [x] 1.3 Add remaining production vars to `.env.example`: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `DEMUCS_DEVICE`

## 2. Railway service config

- [x] 2.1 Create `apps/api/start.sh`: run `alembic upgrade head` then `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`
- [x] 2.2 Create `apps/api/railway.toml` defining `web` (startCommand = `./start.sh`) and `worker` (startCommand = `rq worker default --worker-class rq.SimpleWorker`) services, both with `rootDirectory = "apps/api"`
- [x] 2.3 Create `apps/api/Procfile` with `web: bash start.sh` as fallback

## 3. Smoke test locally

- [x] 3.1 Verify `start.sh` is executable (`chmod +x`) and runs without errors against the local dev database
- [x] 3.2 Confirm `CORS_ORIGINS=http://localhost:5173` in `.env` still lets the frontend connect

## 4. Railway project setup (manual steps — document in README)

- [x] 4.1 Add a "Railway deployment" section to the root `README.md` listing: create project, attach PostgreSQL + Redis add-ons, set all env vars from `.env.example`, and point the service root to `apps/api`
- [x] 4.2 Note in README that the worker service requires the same env vars as web and should be added as a second service in the same Railway project
