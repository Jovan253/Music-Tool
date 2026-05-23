# Music Tool

AI-powered music backing track generator. Upload a song, separate it into stems (vocals, drums, bass, other), and create custom mixes for practice.

## Prerequisites

- Node.js 20+
- Python 3.11+
- npm 9+

## Setup

### 1. Clone and copy environment config

```bash
git clone <repo-url>
cd music-tool
cp .env.example .env
```

Edit `.env` if you need to change any defaults (the defaults work for local dev out of the box).

### 2. Frontend

```bash
# From repo root — installs all workspace packages
npm install

# Start the frontend dev server at http://localhost:5173
npm run dev:web
```

### 3. Backend

```bash
cd apps/api

# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -e .

# Copy backend env vars
cp .env.example .env

# Start the API server at http://localhost:8000
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify

With both servers running:

- Frontend: http://localhost:5173
- Backend health check: http://localhost:8000/health → `{"status":"ok"}`
- API docs (auto-generated): http://localhost:8000/docs

## Project Structure

```
music-tool/
├── apps/
│   ├── web/               # React + TypeScript frontend (Vite)
│   │   └── src/
│   │       ├── components/
│   │       ├── features/
│   │       │   ├── upload/
│   │       │   ├── mixer/
│   │       │   ├── waveform/
│   │       │   └── export/
│   │       ├── lib/       # Shared utilities (api.ts, etc.)
│   │       ├── hooks/
│   │       └── styles/
│   └── api/               # Python FastAPI backend
│       ├── main.py
│       ├── routes/
│       ├── services/
│       ├── workers/
│       ├── audio/
│       ├── storage/
│       ├── models/
│       └── schemas/
├── .env.example           # All environment variables documented here
└── README.md
```

## Notes

- The frontend reads `VITE_API_BASE_URL` from `.env` — must be prefixed `VITE_` for Vite to expose it client-side.
- CORS is pre-configured to allow `http://localhost:5173` in development.
- Never commit `.env` files — they are gitignored.
