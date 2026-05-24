## Why

The current job store is an in-memory Python dict — every server restart wipes all jobs, stems paths, and status. A PostgreSQL-backed store makes jobs durable so users don't lose their work on redeploy or crash.

## What Changes

- Add `asyncpg` + `SQLAlchemy` (async) to the API dependencies
- Add a `jobs` table mirroring the current `Job` dataclass (job_id, status, filename, stems JSON, error, created_at)
- Replace all reads/writes to the in-memory `_jobs` dict with async DB queries
- Add Alembic for schema migrations
- Provide a `DATABASE_URL` env var wired through existing config

## Capabilities

### New Capabilities
- `job-persistence`: Jobs are stored in PostgreSQL and survive server restarts; status, stems paths, and error fields are read from and written to the database

### Modified Capabilities

## Impact

- `apps/api/store/jobs.py` (new) — DB-backed CRUD replacing `jobs_store.py`
- `apps/api/models/job.py` (new) — SQLAlchemy ORM model
- `apps/api/db.py` (new) — engine + session factory
- `apps/api/routes/upload.py`, `routes/jobs.py`, `routes/stems.py`, `routes/export.py` — swap store imports
- `apps/api/pyproject.toml` — add `sqlalchemy[asyncio]`, `asyncpg`, `alembic`
- New `alembic/` directory at `apps/api/`
- `.env` — add `DATABASE_URL`
