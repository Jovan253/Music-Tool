## 1. Storage helpers

- [ ] 1.1 Add `delete_files(bucket, paths)` to `apps/api/storage/supabase_storage.py`, tolerant of paths that are already gone
- [ ] 1.2 Add `list_files(bucket, prefix)` so the sweep can find stem objects it does not have recorded

## 2. Job queries

- [ ] 2.1 Add a query returning jobs whose `created_at` is older than a cutoff and whose `stems` is not null
- [ ] 2.2 Allow `update_job` to clear `stems`, which it currently cannot — `stems=None` means "leave unchanged"
- [ ] 2.3 Add `expired` to the `JobStatus` type

## 3. The sweep

- [ ] 3.1 Add `apps/api/workers/retention.py` with `expire_old_jobs(days, exempt, dry_run)` returning what it did
- [ ] 3.2 Delete the original upload and the stem objects before touching the row, so a failure leaves the job retryable rather than orphaning files
- [ ] 3.3 Skip any job id in the exemption list
- [ ] 3.4 Compute the cutoff in UTC and compare against timezone-aware `created_at` without mixing naive and aware datetimes

## 4. Schedule

- [ ] 4.1 Add a daily scheduled Modal function in `modal_app.py` that calls the sweep
- [ ] 4.2 Confirm it also serves as Supabase keep-alive activity, and note the dependency in `RUNBOOK.md`

## 5. Configuration

- [ ] 5.1 Add `STEM_RETENTION_DAYS` (default 14) and `RETENTION_EXEMPT_JOB_IDS` to both `.env.example` files
- [ ] 5.2 Decide whether these belong in the Modal secret or as function-level defaults

## 6. Client

- [ ] 6.1 Add `expired` to `JobResponse['status']` in `apps/web/src/lib/api.ts`
- [ ] 6.2 Make the poll loop in `UploadZone.tsx` treat any non-pending, non-processing status as terminal
- [ ] 6.3 Show a message for an expired job rather than an empty mixer

## 7. Tests

- [ ] 7.1 Selection: a job inside the window is untouched, one outside is selected
- [ ] 7.2 Exemption: an exempt job past the window is untouched
- [ ] 7.3 Ordering: storage failure leaves the row unchanged
- [ ] 7.4 A job with no stems is never selected
- [ ] 7.5 `update_job` can clear `stems`

## 8. Verify

- [ ] 8.1 Dry run against real data with a long window, confirming nothing is selected
- [ ] 8.2 Dry run with a zero-day window, confirming it selects the real jobs and still deletes nothing
- [ ] 8.3 Deploy, then confirm the next scheduled run fired
