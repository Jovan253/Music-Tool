## Why

Upload works but nothing happens after it — files sit in `uploads/` as `pending` forever. Demucs integration is what makes the product actually do something: take a song and produce 4 playable stems. Without it, the mixer (Phase 2, Task 4) has nothing to play.

This is Phase 2, Task 3.

## What Changes

- New `apps/api/workers/separation.py` — synchronous Demucs worker that takes a `job_id`, runs separation, saves stems, updates job status
- New `apps/api/audio/demucs.py` — thin wrapper around the `demucs` CLI / Python API
- `apps/api/services/jobs.py` updated — job record gains `stems` field (dict mapping stem name → file path) and `error` field
- `POST /upload` updated — after storing the file, triggers the separation worker synchronously before returning (**BREAKING**: response now includes stem paths when processing completes inline, or status `processing` if it takes too long — see design)
- New `GET /jobs/{job_id}` response includes `stems` when status is `done`
- Demucs + torch added to `pyproject.toml`

## Capabilities

### New Capabilities

- `stem-separation`: Demucs-powered audio source separation — accepts a job ID, runs the `htdemucs` model, outputs `vocals.wav`, `drums.wav`, `bass.wav`, `other.wav` into a per-job stems directory, and updates the job record

### Modified Capabilities

- `audio-upload`: Upload response now triggers separation synchronously; job status in the response reflects processing outcome rather than always returning `pending`

## Non-goals (MVP scope)

- Async queue / background worker — Phase 3 (Redis + Celery)
- GPU acceleration — CPU inference only for now
- Advanced Demucs models (htdemucs_ft, 6-stem) — `htdemucs` 4-stem only for MVP
- Stem format conversion (mp3 output) — wav output only
- Frontend mixer wiring — next change (Phase 2, Task 4)
- Progress streaming during separation — Phase 3

## Impact

- New heavy dependencies: `demucs`, `torch`, `torchaudio` — first install will be large (~1-2 GB)
- Processing time: CPU inference on a 3-min song ≈ 30-120s depending on hardware
- `apps/api/uploads/<job_id>/stems/` directory created per job
- `services/jobs.py` schema extended (non-breaking — adds optional fields)
- `routes/upload.py` modified to call worker after file save
