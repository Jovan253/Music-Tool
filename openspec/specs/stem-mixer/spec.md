# Spec: stem-mixer

## Requirement: Backend serves stem audio files
The system SHALL expose a `GET /jobs/{job_id}/stems/{stem_name}` endpoint that verifies the Bearer token, confirms the job belongs to the authenticated user, generates a short-lived signed URL for the requested stem in Supabase Storage, and responds with a `307 Temporary Redirect`. Valid stem names are `vocals`, `drums`, `bass`, and `other`. Unauthenticated requests SHALL be rejected with `401 Unauthorized`.

### Scenario: Valid stem request returns redirect
- **WHEN** an authenticated user requests `GET /jobs/{job_id}/stems/vocals` for a completed job they own
- **THEN** the server responds `307 Temporary Redirect` to a signed URL for the stem audio file

### Scenario: Unauthenticated stem request rejected
- **WHEN** a request is made to the stems endpoint without a valid Bearer token
- **THEN** the server responds `401 Unauthorized`

### Scenario: Unknown job returns 404
- **WHEN** an authenticated user requests a stem for a job ID that does not exist or belongs to another user
- **THEN** the server responds `404 Not Found`

### Scenario: Job not yet done returns 404
- **WHEN** an authenticated user requests a stem for a job that is still processing
- **THEN** the server responds `404 Not Found`

### Scenario: Invalid stem name returns 404
- **WHEN** an authenticated user requests a stem name not in `{vocals, drums, bass, other}`
- **THEN** the server responds `404 Not Found`

## Requirement: Frontend polls job status after upload
The upload flow SHALL poll `GET /jobs/{job_id}` every 3 seconds after receiving a `processing` response, until status reaches `done` or `failed`.

### Scenario: Job completes — transition to mixer
- **WHEN** polling detects `status: "done"`
- **THEN** the UI transitions from the upload/loading state to the stem mixer

### Scenario: Job fails — show error
- **WHEN** polling detects `status: "failed"`
- **THEN** the UI displays the `error` message and allows the user to retry

### Scenario: Processing state shows progress indicator
- **WHEN** the job is in `processing` state
- **THEN** the UI displays a loading indicator with a message indicating separation is in progress

## Requirement: Stem mixer renders 4 synchronized waveforms
The system SHALL render a waveform for each stem (vocals, drums, bass, other) using WaveSurfer.js. All 4 waveforms SHALL be synchronized — play, pause, and seek on any track SHALL apply to all tracks simultaneously.

### Scenario: All 4 waveforms render on load
- **WHEN** the mixer receives a completed job with 4 stem paths
- **THEN** 4 waveform tracks are visible, one per stem, labeled with the stem name

### Scenario: Play/pause controls all tracks
- **WHEN** the user clicks play
- **THEN** all 4 tracks begin playing from the same position simultaneously

### Scenario: Seek syncs all tracks
- **WHEN** the user clicks a position on any waveform
- **THEN** all 4 tracks seek to that position

## Requirement: Per-track volume control
The system SHALL provide a volume slider on each track. Adjusting the slider SHALL change that track's playback volume independently without affecting other tracks.

### Scenario: Volume slider adjusts track level
- **WHEN** the user moves the volume slider on the drums track to 50%
- **THEN** the drums track plays at half volume while other tracks are unaffected

## Requirement: Per-track mute control
The system SHALL provide a mute toggle on each track. Muting a track SHALL silence it without stopping playback of other tracks.

### Scenario: Mute silences a track
- **WHEN** the user clicks mute on the bass track
- **THEN** the bass track produces no audio output while other tracks continue playing

### Scenario: Unmute restores volume
- **WHEN** the user clicks mute again on a muted track
- **THEN** the track resumes playing at its previous volume

## Requirement: Per-track solo control
The system SHALL provide a solo toggle on each track. Soloing a track SHALL silence all other tracks.

### Scenario: Solo silences other tracks
- **WHEN** the user clicks solo on the vocals track
- **THEN** only vocals is audible; drums, bass, and other are silenced

### Scenario: Disabling solo restores all tracks
- **WHEN** the user clicks solo again on the currently soloed track
- **THEN** all tracks resume playing at their configured volumes

## Requirement: Mixer provides an Export button
The stem mixer UI SHALL include an Export button that captures the current per-stem volume and mute state, sends it to the export endpoint, and triggers a browser file download when the response is received.

### Scenario: User clicks Export with default mix
- **WHEN** the user clicks Export with all stems at full volume and none muted
- **THEN** the browser downloads a file named `mix.mp3`

### Scenario: User clicks Export with a stem muted
- **WHEN** the user has muted vocals and clicks Export
- **THEN** the exported file contains no vocal audio

### Scenario: Export in progress shows loading state
- **WHEN** the user clicks Export and the request is in flight
- **THEN** the Export button is disabled and shows a loading indicator

### Scenario: Export error shown to user
- **WHEN** the export request fails (network error or server error)
- **THEN** an error message is displayed near the Export button
