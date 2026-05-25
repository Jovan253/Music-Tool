## MODIFIED Requirements

### Requirement: Separation worker runs Demucs on a job
The system SHALL provide a `run_separation(job_id)` function in `apps/api/workers/separation.py` that retrieves the job record, updates its status to `processing`, invokes the `htdemucs` model via the Demucs Python API using the device from `DEMUCS_DEVICE` (or auto-detected default), records wall-clock separation duration as `processing_ms`, transcodes the 4 WAV output stems to MP3 at 256 kbps, uploads the MP3 files to Supabase, updates the job record with stem paths and status `done`, and handles any exception by setting status to `failed` with an error message.

#### Scenario: Successful separation stores MP3 stems
- **WHEN** `run_separation(job_id)` is called with a valid job containing an uploaded audio file
- **THEN** the job status transitions to `processing` then `done`, the job record contains `stems` with Supabase paths to `vocals.mp3`, `drums.mp3`, `bass.mp3`, and `other.mp3`, and `processing_ms` is set to the wall-clock milliseconds of the Demucs call

#### Scenario: Separation failure
- **WHEN** `run_separation(job_id)` encounters an error during Demucs processing or transcoding
- **THEN** the job status is set to `failed` and `job.error` contains a description of the failure

#### Scenario: Unknown job ID
- **WHEN** `run_separation(job_id)` is called with a job ID that does not exist
- **THEN** the function raises a `ValueError` and does not crash the server

## ADDED Requirements

### Requirement: Stems are transcoded to MP3 after separation
After Demucs writes WAV files, the system SHALL transcode each stem to MP3 at 256 kbps using pydub before uploading to Supabase. The original WAV files SHALL be deleted from local disk after transcoding.

#### Scenario: MP3 files uploaded to Supabase
- **WHEN** separation completes successfully
- **THEN** four MP3 files exist in Supabase Storage under the job's stems prefix, and no WAV files remain on local disk for that job

#### Scenario: Export reads MP3 stems
- **WHEN** the export route downloads stems from Supabase and passes them to mixer.py
- **THEN** mixer.py reads them as MP3 format and produces correct mixed audio output
