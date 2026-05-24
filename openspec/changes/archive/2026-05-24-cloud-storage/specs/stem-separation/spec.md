## MODIFIED Requirements

### Requirement: Stems are stored in a per-job directory
The system SHALL write output stem files to a local temporary directory during processing. After separation completes, each stem SHALL be uploaded to Supabase Storage and the local temp directory SHALL be deleted. The `stems` field in the job record SHALL contain Supabase storage paths (not local file paths).

#### Scenario: Stem files uploaded after successful separation
- **WHEN** separation completes successfully for a given `job_id`
- **THEN** four stem wav files are uploaded to the Supabase `stems` bucket and the local temp directory is removed

#### Scenario: Job stems field contains Supabase paths
- **WHEN** `GET /jobs/{job_id}` is called after successful separation
- **THEN** the `stems` dict values are Supabase storage paths, not local filesystem paths
