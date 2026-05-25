# Spec: job-persistence

## Requirement: Jobs are persisted to PostgreSQL
The system SHALL store all job records in a PostgreSQL `jobs` table. Each job SHALL include a `user_id` column containing the Supabase Auth user ID of the owner. Job data SHALL survive API server restarts and redeployments.

### Scenario: Job survives server restart
- **WHEN** a job is created and the server is restarted
- **THEN** a subsequent authenticated `GET /jobs/{job_id}` by the same user returns the same job

### Scenario: Separation result is persisted
- **WHEN** the Demucs worker finishes and marks a job as `done`
- **THEN** the stems and status are stored in the database

### Scenario: Failed job is persisted
- **WHEN** the Demucs worker encounters an error
- **THEN** the error message and `failed` status are stored

## Requirement: Jobs are scoped to the authenticated user
The system SHALL only return jobs owned by the authenticated user. A user SHALL NOT be able to read or access jobs created by another user.

### Scenario: User sees only their own jobs
- **WHEN** an authenticated user requests `GET /jobs/{job_id}` for a job they created
- **THEN** the server returns the job record

### Scenario: User cannot access another user's job
- **WHEN** an authenticated user requests `GET /jobs/{job_id}` for a job created by a different user
- **THEN** the server responds `404 Not Found`

### Scenario: Unauthenticated job status request rejected
- **WHEN** a request is made to `GET /jobs/{job_id}` without a valid Bearer token
- **THEN** the server responds `401 Unauthorized`

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
