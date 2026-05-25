## MODIFIED Requirements

### Requirement: Backend mixes and exports stems on demand
The system SHALL expose a `POST /jobs/{job_id}/export` endpoint that verifies the Bearer token, confirms the job belongs to the authenticated user, downloads the requested stems from Supabase Storage, mixes them with the specified per-stem volumes, and returns the result as an audio file. Unauthenticated requests SHALL be rejected with `401 Unauthorized`.

#### Scenario: Authenticated export succeeds
- **WHEN** an authenticated user POSTs a valid export request for a completed job they own
- **THEN** the server responds with the mixed audio file as a downloadable attachment

#### Scenario: Unauthenticated export rejected
- **WHEN** a request is made to `POST /jobs/{job_id}/export` without a valid Bearer token
- **THEN** the server responds `401 Unauthorized`

#### Scenario: Export for another user's job returns 404
- **WHEN** an authenticated user requests an export for a job they do not own
- **THEN** the server responds `404 Not Found`

#### Scenario: Export for incomplete job returns 404
- **WHEN** an authenticated user requests an export for a job that is not yet done
- **THEN** the server responds `404 Not Found`
