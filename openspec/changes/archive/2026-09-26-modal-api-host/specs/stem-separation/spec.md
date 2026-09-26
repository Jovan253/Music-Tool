## MODIFIED Requirements

### Requirement: Separation worker runs Demucs on a job
The system SHALL perform stem separation for a job by one of two executors selected by the presence of `MODAL_TOKEN_ID`.

When set, a Modal GPU function SHALL own the whole job: retrieve the job record, set status `processing`, download the uploaded audio from storage, run `htdemucs`, transcode each stem to MP3, upload the stems, and update the job record with stem paths, `processing_ms`, and status `done`.

When unset, `run_separation(job_id)` in `apps/api/workers/separation.py` SHALL perform the same sequence locally, in-process, as the development path.

In both cases any exception SHALL leave the job with status `failed` and a descriptive `error`, and SHALL NOT crash the caller.

#### Scenario: Successful separation on Modal stores MP3 stems
- **WHEN** the Modal separation function runs for a valid job
- **THEN** the job status transitions to `processing` then `done`, the record contains `stems` paths for `vocals.mp3`, `drums.mp3`, `bass.mp3` and `other.mp3`, and `processing_ms` reflects the separation duration

#### Scenario: Local execution produces the same record shape
- **WHEN** `run_separation(job_id)` runs without `MODAL_TOKEN_ID`
- **THEN** the job reaches `done` with the same `stems` keys and a populated `processing_ms`

#### Scenario: Separation failure is recorded, not raised to the client
- **WHEN** separation or transcoding fails in either executor
- **THEN** the job status is `failed`, `job.error` describes the failure, and the client observes it through `GET /jobs/{job_id}`

#### Scenario: Retries exhausted
- **WHEN** the Modal function fails repeatedly and its retry budget is exhausted
- **THEN** the job ends as `failed` rather than remaining `processing` indefinitely

#### Scenario: Unknown job ID
- **WHEN** either executor is invoked with a job ID that does not exist
- **THEN** it raises a `ValueError` without leaving a partial record behind
