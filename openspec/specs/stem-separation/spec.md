# Spec: stem-separation

## Requirement: Separation runs on one of two executors
The system SHALL perform stem separation for a job by one of two executors, selected at dispatch time (see `job-queue`).

When Modal is available, a Modal GPU function SHALL own the whole job: retrieve the job record, set status `processing`, download the uploaded audio from storage, run `htdemucs`, transcode each stem to MP3 at 256 kbps, upload the stems, and update the job record with stem paths, `processing_ms`, and status `done`.

When Modal is unavailable, `run_separation(job_id)` in `apps/api/workers/separation.py` SHALL perform the same sequence locally and in-process. `run_separation` SHALL contain no Modal branch of its own: the same function executes inside the Modal container, so an internal branch would cause Modal to dispatch to itself.

On any exception the job SHALL be left with status `failed` and a descriptive `error`. The exception SHALL then be re-raised so the executor's retry accounting sees the failure; swallowing it would report success.

### Scenario: Successful separation stores MP3 stems
- **WHEN** separation runs for a valid job
- **THEN** the job status transitions to `processing` then `done`, the record contains `stems` paths for `vocals.mp3`, `drums.mp3`, `bass.mp3` and `other.mp3`, and `processing_ms` reflects the separation duration

### Scenario: Both executors produce the same record shape
- **WHEN** the same job is separated locally rather than on Modal
- **THEN** the resulting record has the same `stems` keys and a populated `processing_ms`

### Scenario: Separation failure is recorded and re-raised
- **WHEN** separation or transcoding fails
- **THEN** the job status is `failed`, `job.error` describes the failure, and the exception propagates so the retry policy applies

### Scenario: Unknown job ID
- **WHEN** either executor is invoked with a job ID that does not exist
- **THEN** it raises a `ValueError` without leaving a partial record behind

## Requirement: Stems are transcoded to MP3 before upload
After Demucs writes WAV files, the system SHALL transcode each stem to MP3 at 256 kbps using pydub before uploading. MP3 keeps waveform loading fast in the mixer and keeps per-job storage to roughly 20–60 MB.

### Scenario: MP3 files uploaded to storage
- **WHEN** separation completes successfully
- **THEN** four MP3 files exist under the job's stems prefix

### Scenario: Export reads MP3 stems
- **WHEN** the export route downloads stems and passes them to `mixer.py`
- **THEN** they are read as MP3 and produce correct mixed audio output

## Requirement: Intermediate files are ephemeral
The system SHALL write Demucs output to a temporary directory and SHALL delete it once the stems are uploaded, whether or not the job succeeded. No stem or upload artefact SHALL persist on the executor's local disk.

### Scenario: Temporary directory is removed after success
- **WHEN** separation completes and stems are uploaded
- **THEN** the temporary working directory no longer exists

### Scenario: Temporary directory is removed after failure
- **WHEN** separation raises partway through
- **THEN** the temporary working directory is still removed

## Requirement: Job status endpoint exposes stems and errors
The `GET /jobs/{job_id}` endpoint SHALL include `stems` (dict of stem name → storage path) when status is `done`, and `error` (string) when status is `failed`. A job that reaches a non-failed status SHALL NOT carry an error from an earlier attempt.

### Scenario: Completed job includes stems
- **WHEN** `GET /jobs/{job_id}` is called after successful separation
- **THEN** the response includes `"status": "done"` and a `stems` object with keys `vocals`, `drums`, `bass`, `other`

### Scenario: Failed job includes error message
- **WHEN** `GET /jobs/{job_id}` is called after a failed separation
- **THEN** the response includes `"status": "failed"` and a non-empty `error` string

### Scenario: Retry clears a previous error
- **WHEN** a job that previously failed is retried and succeeds
- **THEN** the response includes `"status": "done"` and `error` is null
