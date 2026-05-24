## Context

All uploaded audio and Demucs output currently lives in `apps/api/uploads/` on the API server's local disk. This works for local dev but is fatal in production — Railway, Render, and similar platforms use ephemeral disks that are wiped on every redeploy. We need durable, externally-accessible file storage before deploying.

Supabase Storage is the natural choice: it's S3-compatible, has a generous free tier, and we're already planning to use Supabase for auth. Using one platform reduces operational complexity.

## Goals / Non-Goals

**Goals:**
- Uploaded audio stored in Supabase `uploads` bucket
- Separated stems stored in Supabase `stems` bucket
- Stem playback served via short-lived signed URLs (1 hour TTL)
- Export endpoint downloads stems from Supabase into memory, mixes, returns
- Local disk used only as temp scratch during Demucs processing, cleaned up after
- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` configure the connection
- Setup guide for creating the Supabase project and buckets (one-time manual step)

**Non-Goals:**
- Per-user file scoping (that's the auth change)
- Public bucket URLs (signed URLs only for now)
- CDN or custom domain for assets
- Migrating existing local files

## Decisions

### Supabase Storage over S3 directly
Supabase Storage is backed by S3 but adds a simpler SDK, bucket-level policies, and integrates with Supabase Auth (useful for the upcoming auth change). No extra AWS account needed.

### Service role key for all storage operations
Rather than per-user RLS policies (which require auth), the API server uses the `service_role` key for all storage operations. This bypasses RLS — acceptable for MVP since there's no auth yet. When auth is added, the storage service can switch to user-scoped access tokens.

### Signed URLs for stem playback (1-hour TTL)
Stems are in a private bucket. The stems endpoint returns a `307 Temporary Redirect` to a signed URL. WaveSurfer.js follows redirects transparently. This avoids streaming the file through the API server, reducing bandwidth and latency.

### Local temp dir for Demucs scratch space
Demucs must write to a local path. The worker writes to `tempfile.mkdtemp()`, uploads each stem, then deletes the temp dir. The `uploads/` directory is no longer used for permanent storage.

### `storage/supabase.py` thin service wrapper
A single module exposes `upload_file(bucket, path, data)`, `download_file(bucket, path) -> bytes`, and `create_signed_url(bucket, path, ttl) -> str`. This isolates the Supabase SDK from routes and the worker.

## Risks / Trade-offs

- [Supabase outage] If Supabase is down, uploads fail and playback breaks. → Acceptable for MVP; add fallback later.
- [Signed URL expiry] A 1-hour signed URL will expire if the user leaves the mixer open for >1 hour. → WaveSurfer loads the audio on mount; in practice this window is fine for MVP.
- [Upload latency] Uploading stems to Supabase adds latency to the worker after separation. For a 3-min song this is ~4 × 30-50 MB wav files. → Acceptable; worker runs async, user only sees the final `done` status.
- [Cold migration] Existing jobs in the DB still point to local paths that won't exist after deploy. → Document: existing jobs become invalid after switching to cloud storage. No automated migration for MVP.

## Migration Plan

1. Create Supabase project at supabase.com (manual, one-time)
2. Create `uploads` and `stems` buckets (private)
3. Copy `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` to `.env`
4. Add `supabase` Python package
5. Implement `storage/supabase.py`
6. Update `routes/upload.py` to upload to Supabase
7. Update `workers/separation.py` to upload stems and clean up temp dir
8. Update `routes/stems.py` to return signed URL redirect
9. Update `routes/export.py` to download stems from Supabase for mixing
