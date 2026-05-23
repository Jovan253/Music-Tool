## 1. Backend — Dependencies & Structure

- [x] 1.1 Add `python-multipart` to `apps/api/pyproject.toml` dependencies and reinstall into venv
- [x] 1.2 Create `apps/api/services/jobs.py` — in-memory job store with `create_job()` and `get_job()` functions
- [x] 1.3 Create `apps/api/routes/upload.py` — `POST /upload` endpoint with file type validation, size validation, local storage, and job creation
- [x] 1.4 Create `apps/api/routes/jobs.py` — `GET /jobs/{job_id}` endpoint that returns job record or 404
- [x] 1.5 Register both routers in `apps/api/main.py`

## 2. Backend — Verification

- [x] 2.1 Start the backend and test `POST /upload` with a valid mp3 via curl or `/docs` — confirm 201 response with `job_id`
- [x] 2.2 Confirm file appears in `apps/api/uploads/` after upload
- [x] 2.3 Test `GET /jobs/{job_id}` returns the job record with `status: "pending"`
- [x] 2.4 Test rejection of unsupported file type (e.g. `.mp4`) — confirm 422 response
- [x] 2.5 Test rejection of oversized file — confirm 413 response

## 3. Frontend — Upload Feature

- [x] 3.1 Add `uploadFile()` helper to `apps/web/src/lib/api.ts` — uses XHR with `onprogress` callback, returns `Promise<{ job_id, status, filename }>`
- [x] 3.2 Create `apps/web/src/features/upload/UploadZone.tsx` — drag-and-drop zone with hidden file input, accepts mp3/wav/m4a only
- [x] 3.3 Add client-side validation in `UploadZone` — file type check and 50 MB size check before upload starts
- [x] 3.4 Add upload progress bar to `UploadZone` — visible while upload is in flight, shows percentage
- [x] 3.5 Add success state to `UploadZone` — displays job ID and "Upload complete" message on 201 response
- [x] 3.6 Add error state to `UploadZone` — displays message and retry option on wrong type, too large, or network error
- [x] 3.7 Mount `UploadZone` in `apps/web/src/App.tsx` so it renders on the main page

## 4. End-to-End Verification

- [x] 4.1 Start both servers, drag a real mp3 onto the upload zone — confirm progress bar moves and success state appears
- [x] 4.2 Try dropping a `.mp4` file — confirm client-side error appears without network request
- [x] 4.3 Confirm the uploaded file exists in `apps/api/uploads/` with the correct `<job_id>.<ext>` name
