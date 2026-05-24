## Why

The mixer lets users control stem volumes and mute tracks, but there's no way to save the result. Export closes the loop: the user adjusts their mix, hits Export, and gets a downloadable audio file they can actually use for practice.

This is Phase 2, Task 5.

## What Changes

- New `POST /jobs/{job_id}/export` backend endpoint — accepts per-stem volume/mute settings, mixes the stems together using pydub/ffmpeg, returns a downloadable mp3 or wav file
- New `apps/web/src/features/export/ExportButton.tsx` — an Export button in the mixer UI that sends the current mix settings and triggers a file download
- pydub added to backend dependencies (ffmpeg is already a system dependency via Demucs)

## Capabilities

### New Capabilities

- `stem-export`: Mix stems together server-side with per-stem volume and mute settings, return a downloadable audio file (mp3 or wav)

### Modified Capabilities

- `stem-mixer`: Mixer UI gains an Export button that sends current mix state to the export endpoint

## Non-goals (MVP scope)

- Client-side mixing/rendering (Web Audio API export) — server-side is simpler given we already have the wav files
- Lossy quality settings / bitrate control — fixed 192kbps mp3 or source-quality wav
- Background export job / progress polling — synchronous response for MVP (mix is fast, < 5s)
- Saving exports to cloud storage — direct file download only
- Export history / re-download — one-shot download per request

## Impact

- New backend dependency: `pydub` (wraps ffmpeg for audio mixing)
- New route file: `apps/api/routes/export.py`
- `apps/api/main.py` updated to register export router
- `StemMixer.tsx` updated to include ExportButton and pass current mix state
- No changes to job store, separation worker, or stem serving route
