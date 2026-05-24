## 1. Dependencies & Configuration

- [x] 1.1 Add `sqlalchemy`, `psycopg2-binary`, and `alembic` to `apps/api/pyproject.toml` and install into venv
- [x] 1.2 Add `DATABASE_URL` to `apps/api/.env` (local dev value pointing to local Postgres instance)
- [x] 1.3 Create `apps/api/db.py` — read `DATABASE_URL` from env (raise `RuntimeError` if missing), create sync `engine` with `psycopg2`, `SessionLocal = sessionmaker(...)`, `Base = declarative_base()`

## 2. ORM Model & Migration

- [x] 2.1 Create `apps/api/models/job.py` — `JobModel` ORM class with columns: `job_id` (PK string), `status`, `filename`, `stems` (JSON), `error` (nullable string), `created_at` (DateTime)
- [x] 2.2 Initialise Alembic inside `apps/api/`: `alembic init alembic`; point `sqlalchemy.url` in `alembic.ini` to `DATABASE_URL`; import `Base` and `JobModel` in `alembic/env.py` so autogenerate sees the model
- [x] 2.3 Generate initial migration: `alembic revision --autogenerate -m "create jobs table"` and verify the generated file creates the `jobs` table correctly
- [x] 2.4 Run `alembic upgrade head` against the local database to create the table

## 3. Store Layer

- [x] 3.1 Create `apps/api/store/jobs.py` — implement `create_job`, `get_job`, `update_job` functions using `SessionLocal`; `get_job` returns `None` when not found; `update_job` accepts keyword args for any subset of fields
- [x] 3.2 Delete `apps/api/jobs_store.py` (the old in-memory store)

## 4. Wire Routes & Worker

- [x] 4.1 Update `apps/api/routes/upload.py` — replace `jobs_store` import with `store.jobs`; call `create_job(...)` instead of dict assignment
- [x] 4.2 Update `apps/api/routes/jobs.py` — replace `jobs_store` import with `store.jobs`; call `get_job(job_id)`
- [x] 4.3 Update `apps/api/routes/stems.py` — replace `jobs_store` import with `store.jobs`
- [x] 4.4 Update `apps/api/routes/export.py` — replace `jobs_store` import with `store.jobs`
- [x] 4.5 Update `apps/api/workers/separation.py` — open its own `SessionLocal` session; call `update_job(job_id, status="done", stems=...)` on success and `update_job(job_id, status="failed", error=...)` on failure; close session in `finally`

## 5. Verification

- [x] 5.1 Upload a file, confirm job appears in the `jobs` table in the database
- [x] 5.2 Wait for separation to complete, confirm `status` and `stems` are updated in the database
- [x] 5.3 Restart the API server, poll the same `job_id`, confirm the job is still returned correctly
