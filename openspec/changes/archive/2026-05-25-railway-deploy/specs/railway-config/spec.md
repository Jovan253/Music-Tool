## ADDED Requirements

### Requirement: railway.toml defines web and worker services
`apps/api/railway.toml` SHALL define two services: `web` running FastAPI via `start.sh` and `worker` running the RQ SimpleWorker. Both services SHALL be rooted at `apps/api/`.

#### Scenario: Railway reads service config
- **WHEN** the Railway platform reads `apps/api/railway.toml`
- **THEN** it provisions a `web` service bound to `$PORT` and a `worker` service with no public port

### Requirement: Startup script runs migrations before server
`apps/api/start.sh` SHALL run `alembic upgrade head` and then start `uvicorn main:app --host 0.0.0.0 --port $PORT`. The script SHALL be executable.

#### Scenario: Fresh deploy applies migrations
- **WHEN** Railway starts the `web` service for the first time against a new database
- **THEN** `alembic upgrade head` creates all tables before uvicorn accepts traffic

#### Scenario: Idempotent re-deploy
- **WHEN** Railway restarts the `web` service and migrations are already at head
- **THEN** `alembic upgrade head` exits cleanly with no changes and uvicorn starts normally

### Requirement: Procfile provides fallback service definition
`apps/api/Procfile` SHALL define a `web` process running the same `start.sh` command.

#### Scenario: Procfile used when railway.toml absent
- **WHEN** Railway falls back to Procfile-based detection
- **THEN** the `web` process starts uvicorn via `start.sh`

### Requirement: Required environment variables are documented
`apps/api/.env.example` SHALL document every variable required in production: `DATABASE_URL`, `REDIS_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`, `SECRET_KEY`, `DEMUCS_DEVICE`, `CORS_ORIGINS`. Each SHALL have a one-line comment explaining its purpose.

#### Scenario: Developer provisions Railway env vars
- **WHEN** a developer reads `.env.example` before configuring the Railway dashboard
- **THEN** they can identify every variable to set and understand its purpose
