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

## Requirement: Job record stores processing duration
The `jobs` table SHALL include a nullable `processing_ms INTEGER` column. The worker SHALL write the wall-clock milliseconds of the Demucs call to this column on successful completion. Failed jobs and jobs that predate this change SHALL have `processing_ms` as `NULL`.

### Scenario: Successful job has processing_ms set
- **WHEN** a separation job completes successfully
- **THEN** the job record has a non-null `processing_ms` value greater than zero

### Scenario: Failed job has processing_ms null
- **WHEN** a separation job fails before or during Demucs inference
- **THEN** the job record has `processing_ms` as `NULL`

### Scenario: Pre-existing jobs unaffected
- **WHEN** the migration runs on a database with existing rows
- **THEN** those rows have `processing_ms` as `NULL` and remain otherwise unchanged

## Requirement: processing_ms exposed in job API response
The `GET /jobs/{job_id}` endpoint SHALL include `processing_ms` in its JSON response. The value SHALL be an integer when set, or `null` when not available.

### Scenario: Completed job response includes processing_ms
- **WHEN** `GET /jobs/{job_id}` is called for a successfully completed job
- **THEN** the response body includes `"processing_ms": <integer>`

### Scenario: Pending or failed job response includes null processing_ms
- **WHEN** `GET /jobs/{job_id}` is called for a job that is pending, processing, or failed
- **THEN** the response body includes `"processing_ms": null`
