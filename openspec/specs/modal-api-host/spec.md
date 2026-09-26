# Spec: modal-api-host

How this backend is hosted. Both the API and the GPU separation function run on
Modal as separately deployed apps, sharing one secret and one source tree.

## Requirement: The FastAPI application is served by Modal
The system SHALL provide `apps/api/modal_app.py` defining a Modal app that serves the existing FastAPI application from `main.py` as an ASGI app. The image SHALL install the project's runtime dependencies, install `ffmpeg` at the system level for `pydub`, and include the API source. The function SHALL receive its configuration from a Modal secret rather than a `.env` file.

### Scenario: Health check responds on the deployed URL
- **WHEN** the Modal app is deployed and a client requests `GET /health` on its URL
- **THEN** the response is `200` with body `{"status":"ok"}`

### Scenario: Cold start serves the first request
- **WHEN** a request arrives after the app has scaled to zero
- **THEN** the container starts and the request is served without error, within a few seconds

### Scenario: Missing configuration fails at deploy, not under traffic
- **WHEN** the Modal secret omits a required variable
- **THEN** the deploy fails because the secret declares its required keys, rather than a container starting and failing per-request

### Scenario: Export works in the deployed image
- **WHEN** a client exports a mix from the deployed API
- **THEN** `pydub` finds `ffmpeg` in the image and the mixdown returns audio

## Requirement: The separation function is a separately deployed Modal app
The system SHALL provide `apps/api/modal_separation.py` defining a T4 GPU function that separates one job by id. Its image SHALL install the `local-separation` extra from `pyproject.toml` so that torch, torchaudio, demucs and their undeclared transitive requirements are pinned in exactly one place. The function SHALL declare a retry policy and a timeout generous enough for a cold container to fetch model weights before work begins.

### Scenario: Deployed function is resolvable by name
- **WHEN** the API dispatches a job
- **THEN** it resolves the function by app name and function name at runtime, and a missing deploy or a rename surfaces as a failed job rather than a startup error

### Scenario: Separation dependencies resolve at import
- **WHEN** the separation image is built
- **THEN** importing demucs inside it succeeds, including transitive requirements such as numpy that neither torch nor demucs declares

### Scenario: GPU is asserted, not assumed
- **WHEN** the separation function runs
- **THEN** it selects the CUDA device explicitly rather than allowing auto-detection to fall back to CPU and consume the whole timeout

## Requirement: Configuration comes from one Modal secret
Production configuration SHALL live in a Modal secret containing `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`, `SECRET_KEY` and `CORS_ORIGINS`. The secret SHALL NOT contain Modal's own API tokens, which a Modal container does not need. Source added to an image SHALL exclude `.env` so credentials never reach an image layer.

### Scenario: Config change takes effect
- **WHEN** a value in the secret is changed
- **THEN** it applies after the secret is recreated and both apps are redeployed, because containers read the secret at start

### Scenario: Credentials are absent from the image
- **WHEN** the image source is assembled
- **THEN** `.env` and the local virtualenv are excluded

## Requirement: Database migrations run as an explicit one-shot
The system SHALL provide a Modal function that runs `alembic upgrade head` on demand. Migrations SHALL NOT run from the ASGI application's startup path, because concurrent containers would race.

### Scenario: Migrating a new database
- **WHEN** the migration function is invoked against a database with no tables
- **THEN** the schema is created to head and the function exits successfully

### Scenario: Migrating an up-to-date database
- **WHEN** the migration function is invoked against a database already at head
- **THEN** it completes successfully and makes no changes

### Scenario: Concurrent API containers do not race on schema
- **WHEN** Modal starts several API containers at once
- **THEN** none of them attempt migrations
