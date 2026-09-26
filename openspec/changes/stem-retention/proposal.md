## Why

Nothing in this system ever deletes a file. Every job leaves an original upload plus four MP3 stems in storage permanently — roughly 20–60 MB per track. Supabase's free tier allows 1 GB, so somewhere between 20 and 50 tracks the bucket fills and uploads start failing.

The failure mode is what makes this urgent rather than tidy: a full bucket surfaces as a storage error on upload, which reads as a bug in the app rather than a quota that was always going to be reached. Two tracks are already stored.

A retention sweep also buys two things for free. It is regular Supabase activity, which matters because the free tier pauses a project after 7 days of inactivity and that pause needs a manual dashboard click to undo. And it establishes the exemption mechanism the planned public demo page will need, so the demo's stems are not deleted out from under it later.

## What Changes

- Add `apps/api/workers/retention.py` with a sweep that finds jobs past the retention window, deletes their upload and stem objects from storage, and marks the job `expired` with `stems` cleared
- Add a daily scheduled Modal function in `modal_app.py` that runs the sweep
- Add storage helpers for deleting and listing objects
- Add `STEM_RETENTION_DAYS` (default 14) and `RETENTION_EXEMPT_JOB_IDS` to configuration
- Add `expired` as a job status. **No database migration is needed** — `status` is already a plain `String` column
- Make the frontend's poll loop treat any non-pending, non-processing status as terminal, so an unrecognised status cannot spin the poller forever

Deliberately out of scope: the R2 storage migration. Retention is worth having on Supabase now, and the same sweep will apply unchanged once storage moves.

## Capabilities

### New Capabilities

- `stem-retention`: the retention window, what gets deleted, the exemption list, the schedule, and the `expired` terminal state

### Modified Capabilities

- `job-persistence`: job status gains a fifth value, `expired`, meaning the record survives but its audio no longer exists
- `stem-mixer`: the client must handle a terminal status it does not recognise rather than polling indefinitely

## Impact

- `apps/api/workers/retention.py` — new
- `apps/api/storage/supabase_storage.py` — add `delete_files`, `list_files`
- `apps/api/services/jobs.py` — add a query for expiry candidates and a way to clear `stems`
- `apps/api/modal_app.py` — add the scheduled function
- `apps/api/.env.example`, `.env.example` — document the two new variables
- `apps/web/src/lib/api.ts`, `apps/web/src/features/upload/UploadZone.tsx` — status handling
- No database migration. No change to the upload or separation paths.
