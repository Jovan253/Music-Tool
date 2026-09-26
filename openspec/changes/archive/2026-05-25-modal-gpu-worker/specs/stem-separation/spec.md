## MODIFIED Requirements

### Requirement: Separation worker runs Demucs on a job
The system SHALL provide a `run_separation(job_id)` function in `apps/api/workers/separation.py` that retrieves the job record, updates its status to `processing`, and performs stem separation either via Modal GPU (if `MODAL_TOKEN_ID` is set in the environment) or locally via the `htdemucs` model (fallback). In both paths the function SHALL record wall-clock separation duration as `processing_ms`, upload MP3 stem files to Supabase, update the job record with stem paths and status `done`, and handle any exception by setting status to `failed` with an error message.

#### Scenario: Successful separation via Modal stores MP3 stems
- **WHEN** `run_separation(job_id)` is called with `MODAL_TOKEN_ID` set and a valid job containing an uploaded audio file
- **THEN** the job status transitions to `processing` then `done`, the job record contains `stems` with Supabase paths to `vocals.mp3`, `drums.mp3`, `bass.mp3`, and `other.mp3`, and `processing_ms` reflects the wall-clock duration including the Modal call

#### Scenario: Fallback to local separation when Modal credentials absent
- **WHEN** `run_separation(job_id)` is called without `MODAL_TOKEN_ID` in the environment
- **THEN** separation runs locally via `separate()` and the job completes with the same output format

#### Scenario: Separation failure
- **WHEN** `run_separation(job_id)` encounters an error during separation or transcoding (Modal or local)
- **THEN** the job status is set to `failed` and `job.error` contains a description of the failure

#### Scenario: Unknown job ID
- **WHEN** `run_separation(job_id)` is called with a job ID that does not exist
- **THEN** the function raises a `ValueError` and does not crash the server
