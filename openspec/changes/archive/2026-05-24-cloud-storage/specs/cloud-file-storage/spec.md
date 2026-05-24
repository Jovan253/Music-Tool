## ADDED Requirements

### Requirement: Audio files are stored in Supabase Storage
The system SHALL upload all audio files (original uploads and processed stems) to Supabase Storage. Files SHALL persist across server restarts and redeployments.

#### Scenario: Upload stores file in Supabase
- **WHEN** a client uploads an audio file
- **THEN** the file is stored in the Supabase `uploads` bucket and the Supabase path is recorded in the job record

#### Scenario: Stems are stored in Supabase after separation
- **WHEN** Demucs separation completes
- **THEN** all four stem wav files are uploaded to the Supabase `stems` bucket and local temp files are deleted

### Requirement: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured
The system SHALL read `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` from the environment. If either is missing, the application SHALL refuse to start with a clear error message.

#### Scenario: Missing credentials prevent startup
- **WHEN** the API starts without `SUPABASE_URL` or `SUPABASE_SERVICE_ROLE_KEY`
- **THEN** the process exits with an error identifying the missing variable

### Requirement: Stem audio is served via signed URLs
The system SHALL generate short-lived signed URLs (1-hour TTL) for stem audio files and return them as redirects. The API SHALL NOT stream stem audio bytes directly.

#### Scenario: Stem request returns signed URL redirect
- **WHEN** a client requests `GET /jobs/{job_id}/stems/{stem_name}` for a completed job
- **THEN** the server responds `307 Temporary Redirect` to a Supabase signed URL valid for 1 hour
