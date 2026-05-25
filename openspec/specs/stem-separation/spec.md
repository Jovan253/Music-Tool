# Spec: stem-separation

## Requirement: Separation worker runs Demucs on a job
The system SHALL provide a `run_separation(job_id)` function in `apps/api/workers/separation.py` that retrieves the job record, updates its status to `processing`, invokes the `htdemucs` model via the Demucs Python API using the device from `DEMUCS_DEVICE` (or auto-detected default), records wall-clock separation duration as `processing_ms`, transcodes the 4 WAV output stems to MP3 at 256 kbps, uploads the MP3 files to Supabase, updates the job record with stem paths and status `done`, and handles any exception by setting status to `failed` with an error message.

### Scenario: Successful separation stores MP3 stems
- **WHEN** `run_separation(job_id)` is called with a valid job containing an uploaded audio file
- **THEN** the job status transitions to `processing` then `done`, the job record contains `stems` with Supabase paths to `vocals.mp3`, `drums.mp3`, `bass.mp3`, and `other.mp3`, and `processing_ms` is set to the wall-clock milliseconds of the Demucs call

### Scenario: Separation failure
- **WHEN** `run_separation(job_id)` encounters an error during Demucs processing or transcoding
- **THEN** the job status is set to `failed` and `job.error` contains a description of the failure

### Scenario: Unknown job ID
- **WHEN** `run_separation(job_id)` is called with a job ID that does not exist
- **THEN** the function raises a `ValueError` and does not crash the server

## Requirement: Stems are transcoded to MP3 after separation
After Demucs writes WAV files, the system SHALL transcode each stem to MP3 at 256 kbps using pydub before uploading to Supabase. The original WAV files SHALL be deleted from local disk after transcoding.

### Scenario: MP3 files uploaded to Supabase
- **WHEN** separation completes successfully
- **THEN** four MP3 files exist in Supabase Storage under the job's stems prefix, and no WAV files remain on local disk for that job

### Scenario: Export reads MP3 stems
- **WHEN** the export route downloads stems from Supabase and passes them to mixer.py
- **THEN** mixer.py reads them as MP3 format and produces correct mixed audio output

## Requirement: Stems are stored in a per-job directory
The system SHALL write output stem files to `uploads/<job_id>/stems/` using the filenames `vocals.wav`, `drums.wav`, `bass.wav`, and `other.wav`. The directory SHALL be created automatically.

### Scenario: Stem files exist after successful separation
- **WHEN** separation completes successfully for a given `job_id`
- **THEN** four files exist at `uploads/<job_id>/stems/vocals.wav`, `drums.wav`, `bass.wav`, and `other.wav`

## Requirement: Upload endpoint triggers separation asynchronously
The `POST /upload` endpoint SHALL start separation in a background thread immediately after storing the uploaded file, and SHALL return `{"job_id": "...", "status": "processing", "filename": "..."}` without waiting for separation to complete.

### Scenario: Upload response returns before separation finishes
- **WHEN** a valid audio file is uploaded
- **THEN** the server responds `201 Created` with `status: "processing"` within a few seconds, before Demucs has completed

### Scenario: Job eventually reaches done status
- **WHEN** a valid audio file is uploaded and sufficient time passes for processing
- **THEN** `GET /jobs/{job_id}` returns `status: "done"` with a `stems` dict containing paths to 4 wav files

## Requirement: Job status endpoint exposes stems and errors
The `GET /jobs/{job_id}` endpoint SHALL include `stems` (dict of stem name → file path) when status is `done`, and `error` (string) when status is `failed`.

### Scenario: Completed job includes stems
- **WHEN** `GET /jobs/{job_id}` is called after successful separation
- **THEN** the response includes `"status": "done"` and a `stems` object with keys `vocals`, `drums`, `bass`, `other`

### Scenario: Failed job includes error message
- **WHEN** `GET /jobs/{job_id}` is called after a failed separation
- **THEN** the response includes `"status": "failed"` and a non-empty `error` string
