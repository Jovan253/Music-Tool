## MODIFIED Requirements

### Requirement: Backend accepts audio file uploads
The system SHALL expose a `POST /upload` endpoint that accepts a single audio file (mp3, wav, or m4a) from an authenticated user. The endpoint SHALL validate the Bearer token, validate file type and size, upload the file to Supabase Storage, start a background separation job scoped to the authenticated user, and return a JSON response containing `job_id`, `status: "processing"`, and `filename`. Requests without a valid token SHALL be rejected with `401 Unauthorized`.

#### Scenario: Valid mp3 upload by authenticated user
- **WHEN** an authenticated user POSTs a valid mp3 file under 50 MB to `/upload`
- **THEN** the server responds `201 Created` with `{ "job_id": "<uuid>", "status": "processing", "filename": "<original_name>" }`

#### Scenario: Valid wav upload by authenticated user
- **WHEN** an authenticated user POSTs a valid wav file under 50 MB to `/upload`
- **THEN** the server responds `201 Created` with `status: "processing"`

#### Scenario: Valid m4a upload by authenticated user
- **WHEN** an authenticated user POSTs a valid m4a file under 50 MB to `/upload`
- **THEN** the server responds `201 Created` with `status: "processing"`

#### Scenario: Unauthenticated upload rejected
- **WHEN** a request is made to `POST /upload` without a valid Bearer token
- **THEN** the server responds `401 Unauthorized`

#### Scenario: Unsupported file type rejected
- **WHEN** an authenticated user POSTs a file with an unsupported extension
- **THEN** the server responds `422 Unprocessable Entity`

#### Scenario: File too large rejected
- **WHEN** an authenticated user POSTs a file larger than 50 MB
- **THEN** the server responds `413 Request Entity Too Large`
