## Context

Storage grows without bound today. The binding constraint is Supabase's 1 GB free tier against ~20–60 MB per job; egress (5 GB/month) is a secondary concern that retention also helps, since fewer stored tracks means fewer stems available to stream.

The sweep has to run somewhere. There is no longer a long-lived server process to hang a timer off — the API scales to zero — so a scheduled Modal function is the natural home, and Modal's cron is included in the free plan.

## Decisions

**Expire the record, don't delete it**

Deleting the job row would be simpler, but it throws away the only history the user has of what they have separated, and it makes a stale link fail as a 404 that is indistinguishable from a bug. Marking the job `expired` with `stems` cleared keeps the record meaningful — "this existed, its audio is gone" — and gives the client something honest to display.

This costs nothing schema-wise: `status` is a `String` column, not a database enum, so adding a fifth value needs no migration. Only the `JobStatus` type and the client's handling change.

**Any unrecognised status is terminal on the client**

The poll loop currently continues unless it sees `done` or `failed`, so introducing `expired` would make it poll forever. Rather than adding a third explicit branch, the loop treats anything that is not `pending` or `processing` as terminal. That is robust to whatever status comes next, and it fixes a latent bug: a typo'd or unknown status already meant an infinite poll.

In practice an expired job is nearly invisible in today's UI, because there is no job history — you can only see the job you just uploaded. The client change is therefore about correctness rather than user-facing behaviour, and it matters more once a history or the demo page exists.

**Delete storage before updating the row**

If the row were marked `expired` first and deletion then failed, the objects would be orphaned with nothing left pointing at them — unreachable and uncollectable. Deleting first means a failure leaves the row untouched and the job is simply retried on the next sweep. Storage deletion is idempotent, so a partial delete followed by a retry is safe.

**An explicit exemption list, added now rather than later**

`RETENTION_EXEMPT_JOB_IDS` exists for the public demo page that is planned but not built. Adding the mechanism now is a few lines; discovering its absence later means the demo silently loses its audio after two weeks and the portfolio link breaks with no warning. The failure would be delayed, quiet, and exactly the kind nobody notices until someone else sees it.

**14 days by default**

Long enough that a practice session's stems are still there next weekend, short enough that the bucket holds steady-state usage. It is configurable because the right number depends on how heavily the tool is used, and the R2 migration will raise the ceiling tenfold.

## Risks

- **A sweep bug deletes audio irrecoverably.** There are no backups on the Supabase free plan. Mitigations: the exemption list, a dry-run capability for the first run, and a query that only ever selects jobs past the window with a non-null `stems`.
- **Clock skew between the sweep and job timestamps.** `created_at` is stored timezone-aware, and the cutoff is computed in UTC; the comparison must not mix naive and aware datetimes.
- **The sweep is the only thing keeping Supabase awake.** If it breaks, the project can pause after 7 days and needs a manual restore. Worth noting in the runbook rather than engineering around.
- **Retention deletes the original upload too**, so an expired job cannot be re-separated without re-uploading. That is the intended trade — the upload is the larger of the two artefacts.

## Rollout

1. Implement and unit-test the selection logic against SQLite, including the exemption list and the boundary condition
2. Run the sweep manually with a long window first, confirming it selects nothing
3. Deploy the scheduled function
4. Confirm on the following day's run that the schedule fired
