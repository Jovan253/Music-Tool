## 1. Backend — Export Endpoint

- [x] 1.1 Add `pydub` to `apps/api/pyproject.toml` dependencies and install into venv
- [x] 1.2 Create `apps/api/audio/mixer.py` — `mix_stems(stems: dict[str, str], volumes: dict[str, float], format: str) -> bytes` function: load each stem wav with pydub, apply per-stem gain (convert 0–1 scalar to dB), overlay all tracks, export to bytes in requested format
- [x] 1.3 Create `apps/api/routes/export.py` — `POST /jobs/{job_id}/export` endpoint: validate job is done, validate format (`mp3`|`wav`), call `mix_stems`, return `StreamingResponse` with correct `Content-Type` and `Content-Disposition: attachment; filename="mix.<format>"`
- [x] 1.4 Register export router in `apps/api/main.py`

## 2. Frontend — Export Button

- [x] 2.1 Create `apps/web/src/features/export/ExportButton.tsx` — button component that accepts `jobId`, `volumes`, `muted` props; on click POSTs to `/jobs/{job_id}/export` with current mix state (muted stems get volume 0); on response triggers `URL.createObjectURL` download; shows loading state while request is in flight; shows inline error on failure
- [x] 2.2 Add `exportMix(jobId, stems, format)` to `apps/web/src/lib/api.ts` — POST to `/jobs/{job_id}/export`, returns a `Blob`
- [x] 2.3 Add `<ExportButton>` to `StemMixer.tsx` — place it next to the Play button, pass `jobId`, current `volumes`, and `muted` state

## 3. Verification

- [x] 3.1 Upload an mp3, wait for separation, adjust volumes/mutes in the mixer, click Export — confirm a `mix.mp3` downloads
- [x] 3.2 Mute a stem (e.g. vocals), export, open in an audio player and confirm that stem is silent
- [x] 3.3 Export as wav — confirm `mix.wav` downloads and plays correctly
