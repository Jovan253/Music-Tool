## 1. Supabase Project Setup (manual)

- [x] 1.1 Create a free Supabase project at supabase.com — note the project URL and service role key from Project Settings → API
- [x] 1.2 In the Supabase dashboard, create two private storage buckets: `uploads` and `stems`
- [x] 1.3 Add `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` to `apps/api/.env` and `.env.example`

## 2. Dependencies & Storage Service

- [x] 2.1 Add `supabase>=2.0` to `apps/api/pyproject.toml` and install into venv
- [x] 2.2 Create `apps/api/storage/__init__.py` (empty)
- [x] 2.3 Create `apps/api/storage/supabase_storage.py` — initialise `supabase.create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)` on import (raise `RuntimeError` if either env var is missing); expose `upload_file(bucket, path, data: bytes, content_type: str)`, `download_file(bucket, path) -> bytes`, and `create_signed_url(bucket, path, ttl_seconds: int) -> str`

## 3. Upload Route

- [x] 3.1 Update `apps/api/routes/upload.py` — after saving the file locally to get the job_id, upload the file bytes to Supabase `uploads` bucket at path `{job_id}.{ext}`; call `update_job(job.job_id, file_path=f"{job_id}.{ext}")` to store the Supabase path (not the local path); delete the local file after upload

## 4. Separation Worker

- [x] 4.1 Update `apps/api/workers/separation.py` — use `tempfile.mkdtemp()` for the Demucs output directory instead of the `uploads/` path; after separation succeeds, upload each stem wav to the Supabase `stems` bucket at `{job_id}/{stem_name}.wav`; call `update_job` with the Supabase paths dict; delete the temp directory with `shutil.rmtree`
- [x] 4.2 Update `apps/api/audio/demucs.py` (or wherever `separate()` is defined) — ensure it accepts an arbitrary output directory path (it already should; verify)

## 5. Stems Route

- [x] 5.1 Update `apps/api/routes/stems.py` — replace `FileResponse` with `RedirectResponse(status_code=307)` pointing to a 1-hour signed URL from `create_signed_url("stems", path, 3600)`

## 6. Export Route

- [x] 6.1 Update `apps/api/routes/export.py` — replace local file reads in `mix_stems` with `download_file("stems", path)` calls; pass the downloaded bytes to pydub via `AudioSegment.from_file(io.BytesIO(data))`; update `apps/api/audio/mixer.py` to accept `bytes` instead of file paths

## 7. Verification

- [x] 7.1 Upload a file — confirm it appears in the Supabase `uploads` bucket in the dashboard
- [x] 7.2 Wait for separation — confirm 4 stem files appear in the `stems` bucket and the job `stems` dict contains Supabase paths
- [x] 7.3 Open the mixer — confirm waveforms load (browser follows the signed URL redirect)
- [x] 7.4 Export a mix — confirm download works with stems fetched from Supabase
