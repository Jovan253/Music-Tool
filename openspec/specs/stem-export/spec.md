# Spec: stem-export

## Requirement: Backend mixes stems and returns downloadable audio
The system SHALL expose a `POST /jobs/{job_id}/export` endpoint that accepts per-stem volume scalars (0.0–1.0) and a format (`mp3` or `wav`), mixes the stems together with those settings, and returns the result as a downloadable audio file.

### Scenario: Export mp3 with default volumes
- **WHEN** a client POSTs `{ "stems": { "vocals": 1.0, "drums": 1.0, "bass": 1.0, "other": 1.0 }, "format": "mp3" }` for a completed job
- **THEN** the server responds `200 OK` with a `audio/mpeg` file and `Content-Disposition: attachment; filename="mix.mp3"`

### Scenario: Export wav with a stem muted
- **WHEN** a client POSTs `{ "stems": { "vocals": 0.0, "drums": 1.0, "bass": 1.0, "other": 1.0 }, "format": "wav" }` for a completed job
- **THEN** the server responds `200 OK` with a `audio/wav` file containing no vocal audio

### Scenario: Export with reduced stem volume
- **WHEN** a client POSTs with a stem volume between 0.0 and 1.0 (e.g. `"drums": 0.5`)
- **THEN** the exported file contains that stem at half its original level

### Scenario: Job not done returns 404
- **WHEN** a client POSTs to export a job that is still `processing` or does not exist
- **THEN** the server responds `404 Not Found`

### Scenario: Invalid format returns 422
- **WHEN** a client POSTs with a format value other than `mp3` or `wav`
- **THEN** the server responds `422 Unprocessable Entity`
