## Why

The monorepo skeleton is in place but the app does nothing yet. Audio upload is the first user-facing action in the product flow — without it, stem separation, the mixer, and everything else can't start. This is the entry point to the entire MVP.

This is Phase 2, Task 2.

## What Changes

- New `POST /upload` endpoint on the FastAPI backend: accepts mp3/wav/m4a, validates file type and size, stores the file locally, creates a job record, returns a job ID and initial status
- New drag-and-drop upload UI component in the React frontend (`features/upload/`) with file type filtering, size feedback, and upload progress indicator
- Local file storage under `apps/api/uploads/` (no cloud storage yet — Phase 3)
- In-memory job store (Python dict) to track upload state — no database yet

## Capabilities

### New Capabilities

- `audio-upload`: End-to-end audio file upload — frontend drag-and-drop UI through to backend storage and job creation, with validation and progress feedback

### Modified Capabilities

<!-- None — monorepo-foundation has no upload requirements to change -->

## Non-goals (MVP scope)

- Cloud storage (S3, Supabase) — Phase 3
- Persistent job database — Phase 3
- Chunked / resumable uploads — future
- Spotify / YouTube import — never in MVP
- Authentication / per-user isolation — future
- Starting Demucs processing — next change (Phase 2, Task 3)

## Impact

- New route: `apps/api/routes/upload.py`
- New frontend feature: `apps/web/src/features/upload/`
- New dependency: `python-multipart` (FastAPI file upload requirement)
- Creates `apps/api/uploads/` directory at runtime
- `apps/api/main.py` updated to register the upload router
