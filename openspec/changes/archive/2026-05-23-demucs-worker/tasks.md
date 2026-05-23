## 1. Dependencies & Job Model

- [x] 1.1 Add `demucs` and `torch` to `apps/api/pyproject.toml` and install into venv (note: first install downloads ~1-2 GB of model weights)
- [x] 1.2 Extend `JobRecord` in `apps/api/services/jobs.py` — add optional `stems: dict[str, str] | None` and `error: str | None` fields
- [x] 1.3 Update `update_job()` helper in `apps/api/services/jobs.py` — accepts keyword args to patch status, stems, and error on an existing record

## 2. Separation Worker

- [x] 2.1 Create `apps/api/workers/separation.py` — `run_separation(job_id)` function: set status → `processing`, call Demucs, set status → `done` with stems dict, catch all exceptions and set status → `failed` with error message
- [x] 2.2 Create `apps/api/audio/demucs.py` — `separate(input_path, output_dir)` wrapper that calls `demucs.separate.main` with `htdemucs` model and returns dict of stem name → output path

## 3. Wire Upload → Worker

- [x] 3.1 Update `apps/api/routes/upload.py` — after saving the file, start `run_separation(job_id)` in a `threading.Thread(daemon=True)` and return `status: "processing"` in the 201 response
- [x] 3.2 Update `apps/api/routes/jobs.py` — include `stems` and `error` fields in the `GET /jobs/{job_id}` response

## 4. Verification

- [x] 4.1 Install dependencies and confirm `import demucs` works in the venv Python REPL
- [x] 4.2 Start the backend, upload a short real mp3 (30 sec or less to keep wait time low), and poll `GET /jobs/{job_id}` until status reaches `done`
- [x] 4.3 Confirm 4 stem files exist at `uploads/<job_id>/stems/` — vocals.wav, drums.wav, bass.wav, other.wav
- [x] 4.4 Confirm `GET /jobs/{job_id}` returns `stems` dict with correct paths when `done`
- [x] 4.5 Test failure path — rename the uploaded file mid-job to force a failure, confirm status becomes `failed` with an error message
