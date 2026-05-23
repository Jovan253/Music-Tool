## MODIFIED Requirements

### Requirement: Frontend provides drag-and-drop upload UI
The system SHALL include a drag-and-drop upload zone in `apps/web/src/features/upload/` that accepts mp3, wav, and m4a files. The component SHALL display a visual upload progress indicator while the upload is in flight, poll for job completion after upload, and transition to the stem mixer on success.

#### Scenario: User drags a valid file onto the drop zone
- **WHEN** a user drags a valid audio file onto the upload zone and releases it
- **THEN** the upload begins automatically and a progress bar appears showing upload percentage

#### Scenario: User clicks to browse and selects a file
- **WHEN** a user clicks the upload zone and selects a valid audio file via the file picker
- **THEN** the upload begins and a progress bar appears

#### Scenario: Upload completes — enters processing state
- **WHEN** the backend returns a 201 response with `status: "processing"`
- **THEN** the UI enters a loading/polling state showing that separation is in progress

#### Scenario: Job completes — transitions to mixer
- **WHEN** polling detects `status: "done"`
- **THEN** the upload zone is replaced by the stem mixer showing 4 waveform tracks

#### Scenario: Job fails — shows error with retry
- **WHEN** polling detects `status: "failed"`
- **THEN** the UI displays the error message and allows the user to upload a new file

#### Scenario: Wrong file type dropped
- **WHEN** a user drops a file with an unsupported type (e.g. `.mp4`)
- **THEN** the UI displays an error message without initiating an upload

#### Scenario: File too large selected
- **WHEN** a user selects a file larger than 50 MB
- **THEN** the UI displays a "file too large" error without initiating an upload

#### Scenario: Network or server error during upload
- **WHEN** the upload request fails (network error or non-2xx response)
- **THEN** the UI displays an error message and allows the user to retry
