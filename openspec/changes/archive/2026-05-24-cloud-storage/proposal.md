## Why

Uploaded audio files and Demucs stem output are currently stored on the API server's local filesystem. Hosting platforms like Railway and Render use ephemeral disks — every redeploy wipes all files, making the app non-functional in production. Moving to Supabase Storage makes files durable and accessible from any server instance.

## What Changes

- Create a Supabase project and two storage buckets: `uploads` (original audio) and `stems` (separated wav files)
- Add `supabase-py` to API dependencies
- Add a `storage/supabase.py` service module that wraps upload, download, and signed-URL generation
- On upload: save the file to Supabase `uploads` bucket; store the Supabase path in the DB `file_path` column
- After separation: Demucs writes stems to a local temp directory; worker uploads each stem to the `stems` bucket, then stores public URLs in `job.stems`; temp files are deleted
- Stem playback (`GET /jobs/{job_id}/stems/{stem_name}`): redirect to a short-lived signed URL instead of streaming the file directly
- Export endpoint: download stems from Supabase into memory, mix, return — no local file required
- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` env vars configure the connection

## Capabilities

### New Capabilities
- `cloud-file-storage`: Audio files and stems are stored in Supabase Storage and survive server restarts and redeployments; stem URLs are short-lived signed URLs

### Modified Capabilities
- `stem-separation`: After separation completes, stems are uploaded to cloud storage and local temp files are cleaned up
- `stem-mixer`: Stem audio is served via signed URLs rather than directly from the API server

## Impact

- `apps/api/storage/supabase.py` (new) — upload, download, signed URL helpers
- `apps/api/workers/separation.py` — upload stems to Supabase after separation; delete local temp files
- `apps/api/routes/stems.py` — return redirect to signed URL instead of FileResponse
- `apps/api/routes/export.py` — download stems from Supabase into memory for mixing
- `apps/api/routes/upload.py` — upload original file to Supabase; store Supabase path
- `apps/api/pyproject.toml` — add `supabase>=2.0`
- `.env` / `.env.example` — add `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- Supabase project setup (one-time manual step): create project, create buckets, copy keys
