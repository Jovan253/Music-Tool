## 1. Repo Root Scaffolding

- [x] 1.1 Create root `package.json` with `workspaces: ["apps/web"]` and `dev:web` / `dev:api` scripts
- [x] 1.2 Create `.env.example` at repo root with `VITE_API_BASE_URL=http://localhost:8000` and `API_HOST=0.0.0.0`, `API_PORT=8000`
- [x] 1.3 Create root `.gitignore` that ignores `.env`, `node_modules`, `__pycache__`, `.venv`, `*.pyc`

## 2. Frontend App (apps/web)

- [x] 2.1 Scaffold Vite + React + TypeScript app at `apps/web` using `npm create vite@latest`
- [x] 2.2 Install and configure TailwindCSS in `apps/web`
- [x] 2.3 Set up directory structure: `src/components/`, `src/features/`, `src/lib/`, `src/hooks/`, `src/styles/`
- [x] 2.4 Add `VITE_API_BASE_URL` to `apps/web/.env.example` and wire it into a `src/lib/api.ts` base client
- [x] 2.5 Verify `npx tsc --noEmit` passes with zero errors

## 3. Backend App (apps/api)

- [x] 3.1 Create `apps/api` directory with `pyproject.toml` listing `fastapi` and `uvicorn` as dependencies
- [x] 3.2 Create `apps/api/main.py` with FastAPI app, CORS middleware allowing `http://localhost:5173`, and `GET /health` returning `{"status": "ok"}`
- [x] 3.3 Create directory structure: `routes/`, `services/`, `workers/`, `audio/`, `storage/`, `models/`, `schemas/`
- [x] 3.4 Add `apps/api/.env.example` with `API_HOST` and `API_PORT` vars

## 4. Verification & Documentation

- [x] 4.1 Start both dev servers and confirm frontend at `localhost:5173` and backend health check at `localhost:8000/health` both respond
- [x] 4.2 Confirm frontend fetch to `${VITE_API_BASE_URL}/health` succeeds without CORS errors in browser devtools
- [x] 4.3 Write root `README.md` with setup steps: clone → copy `.env.example` → install frontend deps → create Python venv → install backend deps → start both servers
