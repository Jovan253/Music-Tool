## Context

Upload stores files and returns `status: "pending"`. Nothing processes them. This change wires Demucs into the backend so a successful upload immediately kicks off separation and eventually resolves to 4 stem files. Phase 2 — synchronous enough for local dev, but not so synchronous it blocks the HTTP response for 2 minutes.

## Goals / Non-Goals

**Goals:**
- Run `htdemucs` 4-stem separation on every uploaded file
- Job status transitions: `pending` → `processing` → `done` / `failed`
- Upload endpoint returns immediately with `status: "processing"` — no hung HTTP connections
- Stem files stored at `uploads/<job_id>/stems/{vocals,drums,bass,other}.wav`
- `GET /jobs/{job_id}` returns stem paths when `status: "done"`
- Separation errors captured in `job.error`, status set to `"failed"`

**Non-Goals:**
- Redis/Celery queue — Phase 3
- GPU — CPU only for now
- Progress streaming — Phase 3
- mp3 stem output — wav only
- Advanced models (htdemucs_ft, 6-stem)
- Frontend mixer — next change

## Decisions

### Background thread, not blocking response
Demucs CPU inference on a 3-min song takes 30–120s. Blocking the HTTP request that long would time out most browsers and feels broken. A `threading.Thread` started after the file is saved returns the response instantly while work happens in the background. This is the minimal version of async processing — no extra dependencies, replaces cleanly with Celery in Phase 3.

### Demucs Python API, not CLI subprocess
`demucs.separate.main([...])` avoids shell quoting issues, captures errors as Python exceptions, and is easier to test. The CLI (`subprocess`) works but adds process management complexity with no benefit here.

### Model: `htdemucs` (default 4-stem)
Best quality-to-speed ratio in the Demucs family. Outputs `vocals`, `drums`, `bass`, `other`. The `htdemucs_ft` fine-tuned variant is higher quality but 4× slower — not worth it until we have GPU workers in Phase 3.

### Output directory: `uploads/<job_id>/stems/`
Keeps all files for a job co-located. Demucs writes to a subdirectory named after the model by default; we pass `--out` to control the path explicitly. Stem filenames are predictable (`vocals.wav` etc.) which makes the job record simple.

### Job record extended with `stems` + `error` fields
Both optional. `stems` is a dict `{"vocals": "<path>", "drums": "<path>", ...}` populated on success. `error` is a string populated on failure. `GET /jobs/{job_id}` exposes both.

### Thread safety of in-memory job store
The background thread writes to the same module-level dict as the main thread reads from. CPython's GIL makes simple dict writes atomic enough for Phase 2. This is not safe for multiprocessing or multiple workers — fine, that's Phase 3.

## Risks / Trade-offs

[CPU inference is slow — 30–120s per song] → Expected. Document in README. The frontend will poll and show a "processing" state. Phase 3 adds GPU workers.

[Thread crashes silently without crashing the server] → Wrap the entire worker body in try/except, always update job status to `failed` in the except block with the error message.

[Demucs first run downloads the model (~400 MB)] → One-time cost. Document in README. Add a note to warm up the model on server start in a future change.

[Concurrent uploads — multiple threads competing] → Fine for local dev. In-memory store is safe under CPython GIL for simple writes. Phase 3 will use proper workers.

## Migration Plan

No breaking changes to existing API surface from the caller's perspective — upload still returns `job_id`. The `status` in the response changes from `"pending"` to `"processing"` which the frontend already handles as a non-terminal state.
