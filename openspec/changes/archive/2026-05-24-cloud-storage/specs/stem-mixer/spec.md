## MODIFIED Requirements

### Requirement: Backend serves stem audio files
The system SHALL expose a `GET /jobs/{job_id}/stems/{stem_name}` endpoint that generates a short-lived signed URL for the requested stem in Supabase Storage and responds with a `307 Temporary Redirect`. Valid stem names are `vocals`, `drums`, `bass`, and `other`.

#### Scenario: Valid stem request returns redirect
- **WHEN** a client requests `GET /jobs/{job_id}/stems/vocals` for a completed job
- **THEN** the server responds `307 Temporary Redirect` to a signed URL for the stem audio file

#### Scenario: Unknown job returns 404
- **WHEN** a client requests a stem for a job ID that does not exist
- **THEN** the server responds `404 Not Found`

#### Scenario: Job not yet done returns 404
- **WHEN** a client requests a stem for a job that is still `processing`
- **THEN** the server responds `404 Not Found`

#### Scenario: Invalid stem name returns 404
- **WHEN** a client requests a stem name not in `{vocals, drums, bass, other}`
- **THEN** the server responds `404 Not Found`
