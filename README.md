# Music Tool

AI-powered music backing track generator. Upload a song, separate it into stems (vocals, drums, bass, other), and create custom mixes for practice.

## Prerequisites

- Node.js 20.x (do not use 20.19+ — Vite 5 requires exactly 20.18 or lower)
- Python 3.11+
- Docker Desktop (for PostgreSQL and Redis)
- A free [Supabase](https://supabase.com) project with two storage buckets: `uploads` and `stems`

## First-time setup

### 1. Clone and install

```bash
git clone <repo-url>
cd music-tool
npm install
```

### 2. Start local services (PostgreSQL + Redis)

```bash
docker compose up -d
```

This starts PostgreSQL on port 5432 and Redis on port 6379.

### 3. Backend environment

```bash
cd apps/api
cp .env.example .env
```

Edit `apps/api/.env` and fill in your Supabase credentials:

```
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
```

Get these from your Supabase project: **Settings → API → Service role key**.

The `uploads` and `stems` buckets must already exist in Supabase Storage before starting the API.

### 4. Backend dependencies

```bash
cd apps/api
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e .
```

### 5. Run database migrations

```bash
cd apps/api
alembic upgrade head
```

## Running the app

You need three processes running simultaneously — open three terminals.

**Terminal 1 — Frontend**
```bash
npm run dev:web
```

**Terminal 2 — API server**
```bash
cd apps/api
uvicorn main:app --reload
```

**Terminal 3 — RQ worker** (Windows)
```bash
cd apps/api
.venv\Scripts\rq worker default --worker-class rq.SimpleWorker
```

**Terminal 3 — RQ worker** (macOS / Linux)
```bash
cd apps/api
rq worker default
```

### Verify

- Frontend: http://localhost:5173
- Backend health: http://localhost:8000/health → `{"status":"ok"}`
- API docs: http://localhost:8000/docs

## Troubleshooting

### Uploads not reaching the API / Supabase not populating

On Windows, closing a terminal does not always kill the uvicorn process. A lingering process on port 8000 will silently intercept all requests while the new server sits idle.

Check and kill any leftover processes:

```powershell
# See what's on port 8000
Get-NetTCPConnection -LocalPort 8000 -State Listen | Select-Object LocalAddress, OwningProcess

# Kill it
Stop-Process -Id <OwningProcess> -Force

# Or kill all Python processes at once
Get-Process python | Stop-Process -Force
```

Then restart uvicorn. Confirm it's receiving requests by checking that `POST /upload` appears in the terminal after an upload.

### Jobs stuck in "processing" / stems never appear

The RQ worker must be running separately — the API server does not process jobs itself. Start it in a third terminal (see above).

### Old jobs (pre-Supabase) fail after migration

Jobs created before the cloud-storage change store local file paths in the database. The new worker tries to fetch those paths from Supabase and will fail. This is expected — only jobs created after the migration work end-to-end.

## Project Structure

```
music-tool/
├── apps/
│   ├── web/               # React + TypeScript frontend (Vite)
│   │   └── src/
│   │       ├── features/
│   │       │   ├── upload/
│   │       │   ├── mixer/
│   │       │   ├── waveform/
│   │       │   └── export/
│   │       └── lib/       # Shared utilities (api.ts, etc.)
│   └── api/               # Python FastAPI backend
│       ├── main.py
│       ├── routes/
│       ├── services/
│       ├── workers/
│       ├── audio/
│       ├── storage/       # Supabase storage client
│       ├── models/
│       └── alembic/       # Database migrations
├── docker-compose.yml     # PostgreSQL + Redis for local dev
├── .env.example
└── README.md
```

## Railway Deployment (backend)

### 1. Create the Railway project

1. Go to [railway.app](https://railway.app) and create a new project
2. Add a **PostgreSQL** add-on — Railway injects `DATABASE_URL` automatically
3. Add a **Redis** add-on — Railway injects `REDIS_URL` automatically
4. Connect your GitHub repo and set the **root directory to `apps/api`**

### 2. Add services

Railway needs two services from this repo:

| Service | Start command |
|---------|--------------|
| `web` | `bash start.sh` (runs migrations then uvicorn) |
| `worker` | `rq worker default --worker-class rq.SimpleWorker` |

Both services share the same environment variables.

### 3. Set environment variables

Set the following on **both** the `web` and `worker` services (use Railway's "Copy variables" feature after setting them on the first service):

| Variable | Value |
|----------|-------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (Settings → API) |
| `SUPABASE_ANON_KEY` | Anon key (Settings → API) |
| `SECRET_KEY` | Random string — generate with `openssl rand -hex 32` |
| `DEMUCS_DEVICE` | `cpu` (Railway hobby tier has no GPU) |
| `CORS_ORIGINS` | `http://localhost:5173` for now; update to your Vercel URL after frontend deploy |

`DATABASE_URL` and `REDIS_URL` are injected automatically by the add-ons — no need to set them manually.

### 4. Deploy

Push to `main` — Railway auto-deploys. The `web` service runs `alembic upgrade head` on every start before uvicorn begins accepting traffic.

Smoke test: `GET https://<your-railway-domain>/health` → `{"status":"ok"}`

## Notes

- The frontend reads `VITE_API_BASE_URL` from `.env` — must be prefixed `VITE_` for Vite to expose it client-side. Defaults to `http://localhost:8000`.
- CORS origins are driven by the `CORS_ORIGINS` env var (comma-separated). Falls back to `http://localhost:5173` for local dev.
- Never commit `.env` files — they are gitignored.
- Stem separation (Demucs) takes 30–60 seconds per track on CPU. The job will show as processing until the worker completes it.
