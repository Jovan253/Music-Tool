## Context

The monorepo is running. The next vertical slice is getting a file from the user's browser into the backend filesystem with a job record attached. This is intentionally thin — no queue, no database, no cloud storage. Those come in Phase 3. The goal here is a working upload path we can build stem separation on top of next.

## Goals / Non-Goals

**Goals:**
- Accept mp3/wav/m4a uploads up to 50 MB
- Validate file type (MIME + extension) and size on the backend
- Store uploaded file locally at `apps/api/uploads/<job_id>.<ext>`
- Create an in-memory job record with status `pending`
- Return `{ job_id, status, filename }` to the frontend
- Frontend drag-and-drop zone with real upload progress via `XMLHttpRequest` (supports `onprogress`)
- Clear error states: wrong file type, file too large, network error

**Non-Goals:**
- Queue / background worker (no Demucs yet)
- Database persistence (job lost on server restart — acceptable now)
- Cloud storage
- Per-user isolation / auth
- Chunked or resumable uploads

## Decisions

### File size limit: 50 MB
Covers typical song files (3-6 min mp3 ≈ 5-12 MB, lossless wav ≈ 50 MB). Enforced on backend; frontend shows friendly error before attempting upload if possible.

### Validation: MIME type + file extension, not content inspection
Sufficient for MVP. Full magic-byte inspection (e.g. python-magic) adds a system dependency (libmagic) and complexity not worth it at this stage.

### Storage: flat `uploads/` directory with `<job_id>.<ext>` filenames
Avoids collisions without a database. UUIDs as job IDs make the filenames unpredictable. Simple to swap for S3 in Phase 3 — the storage call is isolated in a `storage` module.

### Job store: Python module-level dict `{ job_id: JobRecord }`
Zero dependencies, zero setup. Intentionally ephemeral — jobs are wiped on server restart, which is fine for local dev. Will be replaced with PostgreSQL in Phase 3. The dict is wrapped behind a `jobs` service module so the swap is a one-file change.

### Upload progress: `XMLHttpRequest` with `onprogress`, not `fetch`
`fetch` doesn't expose upload progress events. XHR does via `xhr.upload.onprogress`. Wrapped in a thin `uploadFile()` helper in `src/lib/api.ts` that takes a progress callback.

### Frontend component: uncontrolled drag-and-drop, no library
A simple `<div>` with `onDragOver` / `onDrop` handlers + a hidden `<input type="file">`. No react-dropzone dependency — the component is small enough to own directly.

## Risks / Trade-offs

[Concurrent uploads overwrite nothing — UUID filenames] → Safe by design.

[In-memory job store lost on restart] → Acceptable for Phase 2. Document clearly; replace in Phase 3.

[50 MB limit may be too small for long lossless wav files] → Easily raised. Documented in README. Backend and frontend both enforce the same constant.

[CORS on file upload] → Already configured for `http://localhost:5173`. `python-multipart` must be installed or FastAPI rejects multipart forms with a 422.

## Migration Plan

No migration needed — new endpoints and new UI component only. `main.py` gets one new `include_router` call.
