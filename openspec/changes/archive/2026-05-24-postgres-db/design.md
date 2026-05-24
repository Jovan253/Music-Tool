## Context

The API currently stores jobs in a module-level `dict[str, Job]`. It works for local dev but is wiped on every restart, which will be frequent once we deploy. PostgreSQL is already in the planned stack so this is a straight migration with no new infrastructure decisions.

The separation worker runs in a daemon thread and calls `update_job()` synchronously. Routes are synchronous FastAPI handlers today. We want to keep things simple and avoid introducing async complexity into the worker.

## Goals / Non-Goals

**Goals:**
- Jobs persist across server restarts
- No change to the external API shape (request/response bodies, status codes)
- Alembic migration for the initial schema
- SQLAlchemy ORM for the model layer
- Synchronous DB access (keeps the worker simple, avoids async complexity in threads)

**Non-Goals:**
- Async SQLAlchemy (`asyncpg`) — overkill at this scale; sync `psycopg2` is fine
- Connection pooling tuning
- Soft deletes or job history
- Multi-user scoping (that belongs to the auth change)

## Decisions

### SQLAlchemy sync over async
FastAPI supports both, but the separation worker runs in a plain `threading.Thread` — async sessions can't be used safely from a thread without an event loop. Sync SQLAlchemy with `psycopg2` keeps the worker simple and routes fast enough at current scale.

### ORM over Core
SQLAlchemy ORM adds minimal overhead and the model maps 1:1 to the current `Job` dataclass. Core would be lower-level with no benefit here.

### `stems` stored as JSONB
The stems field is `dict[str, str]` (stem name → file path). JSONB in PostgreSQL handles this natively and avoids a separate join table.

### Alembic for migrations
Even at MVP stage, having a migration history makes deploys reproducible and rollback straightforward.

### Session-per-request via FastAPI dependency
`get_db()` dependency yields a session, commits on success, rolls back on exception, closes on exit. Worker gets its own session directly from `SessionLocal`.

## Risks / Trade-offs

- [Thread safety] SQLAlchemy sync sessions are not thread-safe — each thread (worker) must create its own session. → Worker calls `SessionLocal()` directly, not the route dependency.
- [Schema drift] If `DATABASE_URL` is not set, startup fails loudly. → Raise a clear error at startup.
- [Migration on first deploy] Initial deploy must run `alembic upgrade head` before the app starts. → Document in README; add to Railway/Render start command.

## Migration Plan

1. Add dependencies (`sqlalchemy`, `psycopg2-binary`, `alembic`) to `pyproject.toml`
2. Create `apps/api/db.py` — engine, `SessionLocal`, `Base`
3. Create `apps/api/models/job.py` — `JobModel` ORM class
4. Generate initial Alembic migration (`alembic revision --autogenerate`)
5. Create `apps/api/store/jobs.py` — CRUD functions using `SessionLocal`
6. Replace imports in all routes and the worker
7. Remove `jobs_store.py`

Rollback: restore `jobs_store.py` and revert store imports. No data migration needed for rollback (in-memory store has no data to preserve).
