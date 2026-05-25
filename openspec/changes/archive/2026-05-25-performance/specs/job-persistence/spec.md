## ADDED Requirements

### Requirement: Job record stores processing duration
The `jobs` table SHALL include a nullable `processing_ms INTEGER` column. The worker SHALL write the wall-clock milliseconds of the Demucs call to this column on successful completion. Failed jobs and jobs that predate this change SHALL have `processing_ms` as `NULL`.

#### Scenario: Successful job has processing_ms set
- **WHEN** a separation job completes successfully
- **THEN** the job record has a non-null `processing_ms` value greater than zero

#### Scenario: Failed job has processing_ms null
- **WHEN** a separation job fails before or during Demucs inference
- **THEN** the job record has `processing_ms` as `NULL`

#### Scenario: Pre-existing jobs unaffected
- **WHEN** the migration runs on a database with existing rows
- **THEN** those rows have `processing_ms` as `NULL` and remain otherwise unchanged

### Requirement: processing_ms exposed in job API response
The `GET /jobs/{job_id}` endpoint SHALL include `processing_ms` in its JSON response. The value SHALL be an integer when set, or `null` when not available.

#### Scenario: Completed job response includes processing_ms
- **WHEN** `GET /jobs/{job_id}` is called for a successfully completed job
- **THEN** the response body includes `"processing_ms": <integer>`

#### Scenario: Pending or failed job response includes null processing_ms
- **WHEN** `GET /jobs/{job_id}` is called for a job that is pending, processing, or failed
- **THEN** the response body includes `"processing_ms": null`
