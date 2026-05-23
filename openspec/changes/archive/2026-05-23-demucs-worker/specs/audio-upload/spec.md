## MODIFIED Requirements

### Requirement: Backend accepts audio file uploads
The system SHALL expose a `POST /upload` endpoint that accepts a single audio file (mp3, wav, or m4a). The endpoint SHALL validate file type and size, store the file locally, start a background separation job, and return a JSON response containing `job_id`, `status: "processing"`, and `filename`.

#### Scenario: Valid mp3 upload
- **WHEN** a client POSTs a valid mp3 file under 50 MB to `/upload`
- **THEN** the server responds `201 Created` with `{ "job_id": "<uuid>", "status": "processing", "filename": "<original_name>" }` within a few seconds

#### Scenario: Valid wav upload
- **WHEN** a client POSTs a valid wav file under 50 MB to `/upload`
- **THEN** the server responds `201 Created` with `status: "processing"`

#### Scenario: Valid m4a upload
- **WHEN** a client POSTs a valid m4a file under 50 MB to `/upload`
- **THEN** the server responds `201 Created` with `status: "processing"`

#### Scenario: Unsupported file type rejected
- **WHEN** a client POSTs a file with an unsupported extension (e.g. `.mp4`, `.txt`, `.pdf`)
- **THEN** the server responds `422 Unprocessable Entity` with `{ "detail": "Unsupported file type. Allowed: mp3, wav, m4a" }`

#### Scenario: File too large rejected
- **WHEN** a client POSTs a file larger than 50 MB
- **THEN** the server responds `413 Request Entity Too Large` with `{ "detail": "File too large. Maximum size is 50 MB" }`

### Requirement: Job record tracks upload and processing state
The system SHALL maintain an in-memory job record for each upload containing: `job_id` (UUID), `status` (`pending` | `processing` | `done` | `failed`), `filename`, `file_path`, `created_at` timestamp, `stems` (dict, present when `done`), and `error` (string, present when `failed`).

#### Scenario: Job retrievable after upload
- **WHEN** a valid file is uploaded and the returned `job_id` is used in a subsequent `GET /jobs/<job_id>` request
- **THEN** the server responds `200 OK` with the job record

#### Scenario: Unknown job ID returns 404
- **WHEN** a `GET /jobs/<job_id>` request is made with a job ID that does not exist
- **THEN** the server responds `404 Not Found`
