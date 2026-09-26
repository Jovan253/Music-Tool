## 1. Storage helpers

- [x] 1.1 Add `delete_files(bucket, paths)` to `apps/api/storage/supabase_storage.py`, tolerant of paths that are already gone
- [x] 1.2 Add `list_files(bucket, prefix)` so the sweep can find stem objects it does not have recorded

## 2. Job queries

- [x] 2.1 Add a query returning jobs whose `created_at` is older than a cutoff and whose `stems` is not null
- [x] 2.2 Added a dedicated `expire_job()` instead of widening `update_job`, keeping the clearing semantics in one obvious place
- [x] 2.3 Add `expired` to the `JobStatus` type

## 3. The sweep

- [x] 3.1 Add `apps/api/workers/retention.py` with `expire_old_jobs(days, exempt, dry_run)` returning what it did
- [x] 3.2 Delete the original upload and the stem objects before touching the row, so a failure leaves the job retryable rather than orphaning files
- [x] 3.3 Skip any job id in the exemption list
- [x] 3.4 Compute the cutoff in UTC and compare against timezone-aware `created_at` without mixing naive and aware datetimes

## 4. Schedule

- [x] 4.1 Add a daily scheduled Modal function in `modal_app.py` that calls the sweep
- [x] 4.2 Confirm it also serves as Supabase keep-alive activity, and note the dependency in `RUNBOOK.md`

## 5. Configuration

- [x] 5.1 Add `STEM_RETENTION_DAYS` (default 14) and `RETENTION_EXEMPT_JOB_IDS` to both `.env.example` files
- [x] 5.2 Left out of the Modal secret: both have safe code defaults, and adding them would mean recreating the secret to change a number

## 6. Client

- [x] 6.1 Add `expired` to `JobResponse['status']` in `apps/web/src/lib/api.ts`
- [x] 6.2 Make the poll loop in `UploadZone.tsx` treat any non-pending, non-processing status as terminal
- [x] 6.3 Show a message for an expired job rather than an empty mixer

## 7. Tests

- [x] 7.1 Selection: a job inside the window is untouched, one outside is selected
- [x] 7.2 Exemption: an exempt job past the window is untouched
- [x] 7.3 Ordering: storage failure leaves the row unchanged
- [x] 7.4 A job with no stems is never selected
- [x] 7.5 `expire_job` clears `stems`, and an already-expired job is not swept twice

## 8. Verify

- [x] 8.1 Dry run against real data with a long window, confirming nothing is selected
- [x] 8.2 Dry run with a zero-day window, confirming it selects the real jobs and still deletes nothing
- [ ] 8.3 Deploy, then confirm the next scheduled run fired
