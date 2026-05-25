## MODIFIED Requirements

### Requirement: Backend serves stem audio files
The system SHALL expose a `GET /jobs/{job_id}/stems/{stem_name}` endpoint that verifies the Bearer token, confirms the job belongs to the authenticated user, generates a short-lived signed URL for the requested stem in Supabase Storage, and responds with a `307 Temporary Redirect`. Valid stem names are `vocals`, `drums`, `bass`, and `other`. Unauthenticated requests SHALL be rejected with `401 Unauthorized`.

#### Scenario: Valid stem request returns redirect
- **WHEN** an authenticated user requests `GET /jobs/{job_id}/stems/vocals` for a completed job they own
- **THEN** the server responds `307 Temporary Redirect` to a signed URL for the stem audio file

#### Scenario: Unauthenticated stem request rejected
- **WHEN** a request is made to the stems endpoint without a valid Bearer token
- **THEN** the server responds `401 Unauthorized`

#### Scenario: Unknown job returns 404
- **WHEN** an authenticated user requests a stem for a job ID that does not exist or belongs to another user
- **THEN** the server responds `404 Not Found`

#### Scenario: Job not yet done returns 404
- **WHEN** an authenticated user requests a stem for a job that is still processing
- **THEN** the server responds `404 Not Found`

#### Scenario: Invalid stem name returns 404
- **WHEN** an authenticated user requests a stem name not in `{vocals, drums, bass, other}`
- **THEN** the server responds `404 Not Found`
