# Spec: audio-upload

## Requirement: Backend accepts audio file uploads
The system SHALL expose a `POST /upload` endpoint that accepts a single audio file (mp3, wav, or m4a) from an authenticated user. The endpoint SHALL validate the Bearer token, validate file type and size, upload the file to Supabase Storage, start a background separation job scoped to the authenticated user, and return a JSON response containing `job_id`, `status: "processing"`, and `filename`. Requests without a valid token SHALL be rejected with `401 Unauthorized`.

### Scenario: Valid mp3 upload by authenticated user
- **WHEN** an authenticated user POSTs a valid mp3 file under 50 MB to `/upload`
- **THEN** the server responds `201 Created` with `{ "job_id": "<uuid>", "status": "processing", "filename": "<original_name>" }`

### Scenario: Valid wav upload by authenticated user
- **WHEN** an authenticated user POSTs a valid wav file under 50 MB to `/upload`
- **THEN** the server responds `201 Created` with `status: "processing"`

### Scenario: Valid m4a upload by authenticated user
- **WHEN** an authenticated user POSTs a valid m4a file under 50 MB to `/upload`
- **THEN** the server responds `201 Created` with `status: "processing"`

### Scenario: Unauthenticated upload rejected
- **WHEN** a request is made to `POST /upload` without a valid Bearer token
- **THEN** the server responds `401 Unauthorized`

### Scenario: Unsupported file type rejected
- **WHEN** an authenticated user POSTs a file with an unsupported extension (e.g. `.mp4`, `.txt`, `.pdf`)
- **THEN** the server responds `422 Unprocessable Entity` with `{ "detail": "Unsupported file type. Allowed: mp3, wav, m4a" }`

### Scenario: File too large rejected
- **WHEN** an authenticated user POSTs a file larger than 50 MB
- **THEN** the server responds `413 Request Entity Too Large` with `{ "detail": "File too large. Maximum size is 50 MB" }`

## Requirement: Uploaded file is stored locally
The system SHALL save uploaded files to an `uploads/` directory under `apps/api/`, using `<job_id>.<original_extension>` as the filename. The directory SHALL be created automatically if it does not exist.

### Scenario: File is persisted after upload
- **WHEN** a valid file is uploaded
- **THEN** a file named `<job_id>.<ext>` exists in `apps/api/uploads/` after the response is returned

## Requirement: Job record tracks upload and processing state
The system SHALL maintain an in-memory job record for each upload containing: `job_id` (UUID), `status` (`pending` | `processing` | `done` | `failed`), `filename`, `file_path`, `created_at` timestamp, `stems` (dict, present when `done`), and `error` (string, present when `failed`).

### Scenario: Job retrievable after upload
- **WHEN** a valid file is uploaded and the returned `job_id` is used in a subsequent `GET /jobs/<job_id>` request
- **THEN** the server responds `200 OK` with the job record

### Scenario: Unknown job ID returns 404
- **WHEN** a `GET /jobs/<job_id>` request is made with a job ID that does not exist
- **THEN** the server responds `404 Not Found`

## Requirement: Frontend provides drag-and-drop upload UI
The system SHALL include a drag-and-drop upload zone in `apps/web/src/features/upload/` that accepts mp3, wav, and m4a files. The component SHALL display a visual upload progress indicator while the upload is in flight, poll for job completion after upload, and transition to the stem mixer on success.

### Scenario: User drags a valid file onto the drop zone
- **WHEN** a user drags a valid audio file onto the upload zone and releases it
- **THEN** the upload begins automatically and a progress bar appears showing upload percentage

### Scenario: User clicks to browse and selects a file
- **WHEN** a user clicks the upload zone and selects a valid audio file via the file picker
- **THEN** the upload begins and a progress bar appears

### Scenario: Upload completes — enters processing state
- **WHEN** the backend returns a 201 response with `status: "processing"`
- **THEN** the UI enters a loading/polling state showing that separation is in progress

### Scenario: Job completes — transitions to mixer
- **WHEN** polling detects `status: "done"`
- **THEN** the upload zone is replaced by the stem mixer showing 4 waveform tracks

### Scenario: Job fails — shows error with retry
- **WHEN** polling detects `status: "failed"`
- **THEN** the UI displays the error message and allows the user to upload a new file

### Scenario: Wrong file type dropped
- **WHEN** a user drops a file with an unsupported type (e.g. `.mp4`)
- **THEN** the UI displays an error message without initiating an upload

### Scenario: File too large selected
- **WHEN** a user selects a file larger than 50 MB
- **THEN** the UI displays a "file too large" error without initiating an upload

### Scenario: Network or server error during upload
- **WHEN** the upload request fails (network error or non-2xx response)
- **THEN** the UI displays an error message and allows the user to retry
