# Design decisions

Why TrackSplit is built the way it is. Each entry states the choice, what was
rejected, and what it costs — because the trade-off is usually the interesting
part.

For what the system does and how a request flows through it, see
[README.md](README.md). For running and operating it, see [RUNBOOK.md](RUNBOOK.md).

---

## The constraint that shaped everything

Two requirements pulled in opposite directions:

1. **Stem separation needs a GPU.** Demucs takes ~25 seconds on a T4 and ~12
   minutes on a laptop CPU. That is the difference between a product and a
   science experiment.
2. **It had to cost nothing.** This is a portfolio piece and a personal tool. A
   project that quietly bills £20/month while nobody visits gets deleted.

Almost every decision below follows from wanting GPU compute on demand while
paying nothing when idle.

---

## Infrastructure

### Modal for both the API and the GPU work

**Rejected:** Railway (what this ran on originally), Render, a VPS with a GPU.

Railway was the only paid component and it was running four always-on services
— web, worker, Postgres, Redis — for an app with near-zero traffic. Its free
plan grants $1/month of credit, nowhere near enough; the paid tier is $5/month
and four services would likely exceed its included credit.

Modal bills per second of execution and scales to zero. Its free tier includes
$30/month of credits, roughly 50 T4-hours, or thousands of separations. It also
hosts a full ASGI app, so the API and the GPU function live on one platform.

**Cost:** a cold start adds ~6 seconds to the first request after idle. For a
portfolio app that is a fine trade; for a product with waiting users it would
not be.

### No queue at all

**Rejected:** Redis + RQ, which is what this used before.

A Modal function call is already a durable, addressable, automatically retried
unit of work. That is what the queue was providing. Once the API moved to Modal,
Redis and RQ were paying rent for a feature the platform gives away — so
`POST /upload` now calls `.spawn()` and returns.

Deleting the queue removed a Redis instance, a worker process, a queue module,
and the startup recovery logic that existed to clean up after it.

**Cost:** vendor coupling. Moving off Modal would mean reintroducing a queue.
Acceptable — the alternative was paying for infrastructure to avoid a
hypothetical migration.

### Neon for Postgres, not Supabase's

**Rejected:** Supabase Postgres, even though Supabase is already in the stack
for auth and storage.

Supabase's free tier **pauses a project after 7 days of database inactivity**,
and un-pausing requires a human clicking a button in a dashboard. For an app
someone visits once a quarter from a portfolio link, that is fatal: the reviewer
finds a dead site and only the owner can revive it.

Neon auto-suspends too, but **auto-resumes on the next connection in under a
second**. No human in the loop. `pool_pre_ping=True` makes the reconnection
invisible to the app.

### Supabase kept for auth and storage

Auth is the part of an app most worth not writing yourself: password hashing,
email confirmation, token refresh, session handling. 50k monthly active users
free is far beyond what this needs.

Storage is on Supabase for now but is the **next thing to move**, to Cloudflare
R2. The 1 GB free tier holds only 20–50 tracks, and audio streaming is egress
heavy — R2 gives 10 GB and charges nothing for egress, ever.

---

## Application design

### The GPU function owns the whole job

The Modal GPU function does not just run inference. It downloads the upload,
separates, transcodes, uploads the stems, and writes the final job status.

**This reversed an earlier decision.** The original design deliberately kept
storage credentials out of Modal so the function was "purely compute: bytes in,
bytes out", with a trusted worker doing the I/O. That reasoning depended on the
worker existing — and the worker was the thing being deleted. With nowhere else
for the glue to live, the credentials moved into a Modal secret.

The payoff: job state stays in Postgres, so the client polls the database and
never needs to know which executor ran the job. **Zero frontend changes** came
out of a full backend migration.

### Dispatch is decided outside the worker

`run_separation` contains no Modal branch. The choice between "spawn on Modal"
and "run in-process" lives in `workers/dispatch.py`.

This is not stylistic. The same `run_separation` runs *inside* the Modal
container. If it branched on Modal availability internally, the container would
dispatch to Modal from within Modal — recursively.

Relatedly, availability is keyed on `modal.is_local()`, **not** on whether
`MODAL_TOKEN_ID` is set. A Modal container has no token; it is authenticated
ambiently. Keying on the token made the deployed API conclude Modal was
unavailable and run Demucs locally, in an image that deliberately has no torch.

### Migrations run as an explicit one-shot

**Rejected:** running Alembic on app startup, which is what the Railway setup did.

Under scale-to-zero, containers start constantly and several can start at once.
Migrations on startup would race. A dedicated `migrate()` function, invoked
deliberately, keeps it single-writer and makes the deploy sequence legible.

### Retries replace a startup sweep

The old design reset stale `processing` jobs to `pending` at API startup. Under
scale-to-zero that sweep would fire on *every* cold start and re-run jobs that
were legitimately still in flight. Modal's `retries=2` covers the transient
failures the sweep existed for; a job that exhausts them ends as `failed`, which
is the honest outcome.

### Private buckets, short-lived signed URLs

Stems are never publicly readable. The API mints a 1-hour signed URL per stem on
request. The cost is a round trip before playback; the benefit is that a leaked
URL expires and bulk enumeration is impossible.

### Stems stored as MP3, not WAV

256 kbps MP3 rather than the WAV Demucs emits. Waveforms load roughly 10× faster
and storage per job drops to ~20–60 MB, which is what makes a 1 GB tier viable
at all. The quality loss is inaudible for practising along.

### Retention, and why it exists at all

Nothing deleted anything, so storage grew until the free tier filled — surfacing
as an upload error that reads like a bug rather than a quota. A daily Modal cron
now expires jobs past a window, deleting the audio and marking the record
`expired`.

The record survives rather than being deleted so a stale link says "this
existed, its audio is gone" instead of 404-ing indistinguishably from a bug.

The sweep also doubles as the Supabase keep-alive: it touches the project daily,
which prevents the 7-day auto-pause. That is convenient but couples two
concerns — if the sweep breaks, storage stops being reclaimed *and* the project
eventually pauses.

### The demo takes its job id from config, never the request

`/demo/job` and `/demo/stems/{name}` are unauthenticated. If they accepted a job
id parameter, anyone could read anyone's stems. The id comes from
`DEMO_JOB_ID` in configuration, so there is no request shape that reaches
another user's audio.

The demo job is exempt from retention automatically rather than by being listed
in a second variable — requiring both would be easy to get wrong, and getting it
wrong deletes the public demo's audio two weeks later with no warning.

---

## Frontend

- **One dark theme, no light variant.** Mixing hardware is dark. A light version
  of this would read as a generic web form.
- **No router.** Two routes do not justify the dependency; a path check plus an
  SPA rewrite does it.
- **The mixer takes an injectable data source**, so the signed-in app and the
  public demo share one console instead of maintaining two that drift.
- **One channel colour, used by both the waveform and its marker**, so a channel
  is identifiable at a glance — and channels silenced by another channel's solo
  are visibly dimmed, so it is obvious *why* they are inaudible.

---

## Things that went wrong, and what they taught

Worth knowing because they are the parts that were not predictable from reading
docs.

| Symptom | Cause |
|---|---|
| Every upload failed with `No module named 'torch'` | Dispatch keyed on `MODAL_TOKEN_ID`, which a Modal container never has — so the deployed API ran Demucs in an image with no torch |
| Image built fine, then failed at import with `No module named 'numpy'` | Neither torch nor demucs declares numpy in its metadata; it arrives transitively or not at all |
| A retried job showed `done` next to a stale error message | `update_job(error=None)` meant "leave unchanged", so an error could never be cleared |
| The retention sweep would re-expire already-expired jobs forever | A SQLAlchemy `JSON` column stores Python `None` as JSON `null`, not SQL `NULL`, so `isnot(None)` matches every row |
| App wouldn't start after four months | SQLAlchemy 2.1 changed the default driver for `postgresql://` from psycopg2 to psycopg 3 |
| Sign-in failed with a generic 401 | `SUPABASE_URL` was the dashboard's REST URL, not the project URL, so auth calls 404'd and were reported as bad credentials |

The general lesson: **a successful deploy only proves the image built.** Several
of these passed CI, passed a health check, and failed on the first real file.

---

## Known limitations

Being able to name these matters more than pretending they do not exist.

- **No job history.** A job id lives only in React state, so a previous
  separation becomes unreachable. Putting the id in the URL is the next fix.
- **Storage is the binding constraint.** ~20–50 tracks on the current tier; the
  R2 migration raises it roughly tenfold and removes egress cost.
- **One separation model.** `htdemucs`, four stems. A 6-stem variant exists, and
  newer architectures now beat Demucs on the standard benchmark.
- **No observability.** Log lines on Modal, no error tracking or alerting.
- **Mobile layout is written but unverified** on a real device.
- **Cold starts.** ~6s for the API after idle, longer for the GPU container
  while it fetches model weights.

---

## Questions worth having an answer ready for

**Why not just run Demucs in the browser?**
The model is hundreds of MB and needs real compute. It would be a very slow
first load and unusable on a phone.

**Why serverless rather than a small always-on GPU box?**
Traffic is spiky and mostly zero. A rented GPU costs money every hour; this
costs money only during the ~25 seconds a job runs.

**What happens if two people upload at once?**
Modal runs up to 10 concurrent GPU containers on the free tier, so they separate
in parallel rather than queueing behind each other.

**How do you know a job finished?**
The client polls `GET /jobs/{id}`, which reads status from Postgres. The GPU
function writes the terminal status itself, so the API is not involved in
completion at all.

**What is the failure mode if Modal is down?**
Uploads still succeed and jobs are recorded, but separation never starts. Jobs
sit in `processing`. There is no fallback GPU provider — a deliberate choice
given the cost constraint.
