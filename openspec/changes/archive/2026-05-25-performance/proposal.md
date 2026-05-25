## Why

Two concrete slowdowns in the current flow: (1) separation takes minutes on CPU with no feedback, and (2) Demucs stores stems as uncompressed WAV (~40 MB per stem, ~160 MB total) which WaveSurfer must fully download before rendering — making waveform load slow on any connection. Both are fixable without hardware changes.

## What Changes

- Stems are transcoded from WAV to MP3 (256 kbps) immediately after Demucs finishes; the MP3 files are stored in Supabase instead of WAV — roughly 10× smaller, 10× faster waveform load
- `mixer.py` updated to read stems as MP3 instead of WAV (pydub already handles both)
- `DEMUCS_DEVICE` env var added — defaults to `cuda` if available, `cpu` otherwise; makes device explicit and overridable for GPU deployments
- Wall-clock timing added around Demucs; stored as `processing_ms` on the job record and exposed in the API response

**Not changing:**
- Model stays `htdemucs` (`htdemucs_ft` runs 4 passes and is slower — wrong direction)
- Export format options (mp3/wav) unchanged from the user's perspective

## Capabilities

### New Capabilities

- `demucs-config`: Runtime device selection via `DEMUCS_DEVICE` environment variable

### Modified Capabilities

- `stem-separation`: Stems stored as MP3 instead of WAV; `processing_ms` recorded on job
- `job-persistence`: Job schema gains optional `processing_ms: int | null` field

## Impact

- `apps/api/audio/demucs.py` — pass `--device` arg
- `apps/api/workers/separation.py` — transcode WAV → MP3 after separation, add timing
- `apps/api/audio/mixer.py` — read stems as `format="mp3"`
- `apps/api/db/models.py` — add `processing_ms` column
- `apps/api/schemas/job.py` — expose `processing_ms` in response
- `apps/api/.env.example` — document `DEMUCS_DEVICE`
- `apps/web/src/features/mixer/StemMixer.tsx` — display processing time if present
- No new dependencies; pydub and ffmpeg already installed

## On deployment speed

Yes — both improvements work in production:
- **MP3 stems**: waveform load is ~10× faster on any deployment (CPU or GPU), any connection
- **GPU device**: if you deploy to a Railway/Render GPU tier, separation drops from ~3-4 min to ~15-30s — `DEMUCS_DEVICE=cuda` makes that explicit in your env config
