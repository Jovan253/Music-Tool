# Spec: job-persistence

## Requirement: Jobs are persisted to PostgreSQL
The system SHALL store all job records in a PostgreSQL `jobs` table. Job data SHALL survive API server restarts and redeployments.

### Scenario: Job survives server restart
- **WHEN** a job is created and the server is restarted
- **THEN** a subsequent `GET /jobs/{job_id}` returns the same job with its last-known status

### Scenario: Separation result is persisted
- **WHEN** the Demucs worker finishes and marks a job as `done` with stem paths
- **THEN** the stems and status are stored in the database and returned by subsequent status polls

### Scenario: Failed job is persisted
- **WHEN** the Demucs worker encounters an error and marks a job as `failed`
- **THEN** the error message and `failed` status are stored and returned by `GET /jobs/{job_id}`

## Requirement: DATABASE_URL must be configured at startup
The system SHALL read the `DATABASE_URL` environment variable at startup. If it is not set, the application SHALL refuse to start with a clear error message.

### Scenario: Missing DATABASE_URL prevents startup
- **WHEN** the API is started without `DATABASE_URL` set
- **THEN** the process exits with an error indicating the missing configuration

### Scenario: Valid DATABASE_URL connects on startup
- **WHEN** the API is started with a valid `DATABASE_URL`
- **THEN** the database connection is established and the app starts normally

## Requirement: Database schema is managed by Alembic migrations
The system SHALL use Alembic to manage the `jobs` table schema. Migrations SHALL be run before the application starts.

### Scenario: Fresh database is initialised by migration
- **WHEN** `alembic upgrade head` is run against an empty database
- **THEN** the `jobs` table exists with all required columns
