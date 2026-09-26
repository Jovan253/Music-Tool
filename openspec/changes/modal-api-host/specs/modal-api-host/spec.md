## ADDED Requirements

### Requirement: The FastAPI application is served by Modal
The system SHALL provide `apps/api/modal_app.py` defining a Modal app that serves the existing FastAPI application from `main.py` as an ASGI app. The image SHALL install the project's runtime dependencies, install `ffmpeg` at the system level for `pydub`, and include the API source. The function SHALL receive its configuration from a Modal Secret rather than a `.env` file.

#### Scenario: Health check responds on the deployed URL
- **WHEN** the Modal app is deployed and a client requests `GET /health` on its URL
- **THEN** the response is `200` with body `{"status":"ok"}`

#### Scenario: Cold start serves the first request
- **WHEN** a request arrives after the app has scaled to zero
- **THEN** the container starts and the request is served without error

#### Scenario: Missing configuration fails loudly at deploy time
- **WHEN** the Modal Secret omits a required variable such as `DATABASE_URL` or `SUPABASE_URL`
- **THEN** the container fails at import with the existing explicit `RuntimeError` naming the missing variable, rather than serving requests in a broken state

#### Scenario: Export works in the deployed image
- **WHEN** a client exports a mix from the deployed API
- **THEN** `pydub` finds `ffmpeg` in the image and the mixdown returns audio rather than failing

### Requirement: Database migrations run as an explicit one-shot
The system SHALL provide a Modal function that runs `alembic upgrade head` on demand. Migrations SHALL NOT run from the ASGI application's startup path.

#### Scenario: Migrating a new database
- **WHEN** the migration function is invoked against a database with no tables
- **THEN** the schema is created to head and the function exits successfully

#### Scenario: Migrating an up-to-date database
- **WHEN** the migration function is invoked against a database already at head
- **THEN** it completes successfully and makes no changes

#### Scenario: Concurrent API containers do not race on schema
- **WHEN** Modal starts several API containers at once
- **THEN** none of them attempt migrations, because migration is not part of the request-serving path
