# Spec: stem-export

## Requirement: Backend mixes and exports stems on demand
The system SHALL expose a `POST /jobs/{job_id}/export` endpoint that verifies the Bearer token, confirms the job belongs to the authenticated user, downloads the requested stems from Supabase Storage, mixes them with the specified per-stem volumes, and returns the result as an audio file. Unauthenticated requests SHALL be rejected with `401 Unauthorized`.

### Scenario: Authenticated export succeeds
- **WHEN** an authenticated user POSTs a valid export request for a completed job they own
- **THEN** the server responds with the mixed audio file as a downloadable attachment

### Scenario: Unauthenticated export rejected
- **WHEN** a request is made to `POST /jobs/{job_id}/export` without a valid Bearer token
- **THEN** the server responds `401 Unauthorized`

### Scenario: Export for another user's job returns 404
- **WHEN** an authenticated user requests an export for a job they do not own
- **THEN** the server responds `404 Not Found`

### Scenario: Export for incomplete job returns 404
- **WHEN** an authenticated user requests an export for a job that is not yet done
- **THEN** the server responds `404 Not Found`

### Scenario: Export mp3 with default volumes
- **WHEN** an authenticated user POSTs `{ "stems": { "vocals": 1.0, "drums": 1.0, "bass": 1.0, "other": 1.0 }, "format": "mp3" }` for a completed job they own
- **THEN** the server responds `200 OK` with a `audio/mpeg` file and `Content-Disposition: attachment; filename="mix.mp3"`

### Scenario: Export wav with a stem muted
- **WHEN** an authenticated user POSTs `{ "stems": { "vocals": 0.0, "drums": 1.0, "bass": 1.0, "other": 1.0 }, "format": "wav" }` for a completed job they own
- **THEN** the server responds `200 OK` with a `audio/wav` file containing no vocal audio

### Scenario: Export with reduced stem volume
- **WHEN** an authenticated user POSTs with a stem volume between 0.0 and 1.0 (e.g. `"drums": 0.5`)
- **THEN** the exported file contains that stem at half its original level

### Scenario: Invalid format returns 422
- **WHEN** an authenticated user POSTs with a format value other than `mp3` or `wav`
- **THEN** the server responds `422 Unprocessable Entity`
