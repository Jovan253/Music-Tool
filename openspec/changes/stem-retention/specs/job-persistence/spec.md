## MODIFIED Requirements

### Requirement: A job record has a terminal status
A job's `status` SHALL be one of `pending`, `processing`, `done`, `failed` or `expired`. `expired` means the record survives but its audio has been deleted by the retention sweep, so it can neither be played nor exported and the source file is no longer available to re-separate.

No database migration is needed for this addition: `status` is stored as a plain string column, not a database enum.

#### Scenario: Expired job reports its state
- **WHEN** `GET /jobs/{job_id}` is called for a job whose audio has been deleted
- **THEN** the response has `"status": "expired"` and a null `stems`

#### Scenario: Expired job cannot be exported
- **WHEN** an export is requested for an expired job
- **THEN** it is refused, because export requires status `done` and present stems

#### Scenario: Stem URLs are unavailable for an expired job
- **WHEN** a stem URL is requested for an expired job
- **THEN** it is refused rather than returning a signed URL to a deleted object
