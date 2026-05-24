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

## Notes

- The frontend reads `VITE_API_BASE_URL` from `.env` — must be prefixed `VITE_` for Vite to expose it client-side. Defaults to `http://localhost:8000`.
- CORS is pre-configured to allow `http://localhost:5173` in development.
- Never commit `.env` files — they are gitignored.
- Stem separation (Demucs) takes 30–60 seconds per track on CPU. The job will show as processing until the worker completes it.
